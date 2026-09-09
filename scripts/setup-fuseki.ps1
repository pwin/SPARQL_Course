<#
.SYNOPSIS
    Install Apache Jena and Fuseki if they are not already here, load the
    Bookshop Trail into a TDB2 store, and start the server.

.DESCRIPTION
    With -Install the script fetches Jena and Fuseki from the Apache CDN,
    checks the published SHA-512 of each download, and unpacks them beside one
    another. Nothing is committed to this repository and nothing is installed
    system-wide: the two directories are all there is, and deleting them
    undoes it.

    Without -Install it expects them to be there already, and falls back to
    whichever apache-jena-fuseki-* it can find if the exact path is missing --
    release and snapshot builds differ only in the directory name.

    It then loads data\bookshop-trail-1.2.ttl into a TDB2 store under build\
    and starts Fuseki on http://localhost:3030/bookshop.

    GeoSPARQL: fuseki-server.jar already carries Jena's GeoSPARQL
    implementation, so the geof: functions are there. Run
    scripts/setup-geosparql.ps1 first to add Apache Derby and the EPSG
    dataset, without which projected systems such as EPSG:27700 are not
    recognised.

.PARAMETER Install
    Download and unpack Jena and Fuseki before doing anything else. About
    75 MB in total. Skipped for anything already present.

.PARAMETER InstallTo
    Where to unpack them. Defaults to C:\, giving C:\apache-jena-6.2.0 and
    C:\apache-jena-fuseki-6.2.0.

.EXAMPLE
    ./scripts/setup-fuseki.ps1 -Install
    ./scripts/setup-fuseki.ps1
    ./scripts/setup-fuseki.ps1 -Port 3131 -Data bookshop-trail-full.ttl
    ./scripts/setup-fuseki.ps1 -LoadOnly
#>
param(
    [string]$Version     = "6.2.0",
    [string]$InstallTo   = "C:\",
    [string]$FusekiHome,
    [string]$FusekiJar,
    [string]$JenaHome,
    [string]$Data        = "bookshop-trail-1.2.ttl",
    [string]$DatasetName = "bookshop",
    [int]$Port           = 3030,
    [switch]$Install,
    [switch]$LoadOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

if (-not $FusekiHome) { $FusekiHome = Join-Path $InstallTo "apache-jena-fuseki-$Version" }
if (-not $JenaHome)   { $JenaHome   = Join-Path $InstallTo "apache-jena-$Version" }
if (-not $FusekiJar)  { $FusekiJar  = Join-Path $FusekiHome "fuseki-server.jar" }

function Say($msg, $colour = "Gray") { Write-Host "  $msg" -ForegroundColor $colour }

# ---------------------------------------------------------------- install
# Apache serves current releases from the CDN and everything ever released
# from the archive, so try the CDN and fall back.
function Get-ApacheZip([string]$name, [string]$dest) {
    $sources = @(
        "https://dlcdn.apache.org/jena/binaries/$name",
        "https://archive.apache.org/dist/jena/binaries/$name"
    )
    foreach ($url in $sources) {
        try {
            Say "downloading $url" "Yellow"
            Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
            # The checksum lives beside the artifact. A download that cannot be
            # verified is not worth keeping, so a mismatch deletes the file.
            $sumUrl = "$url.sha512"
            try {
                $published = ((Invoke-WebRequest -Uri $sumUrl -UseBasicParsing).Content `
                              -split '\s+')[0].Trim().ToLower()
            } catch {
                Say "no published checksum at $sumUrl -- not verified" "Yellow"
                return $true
            }
            $actual = (Get-FileHash -Path $dest -Algorithm SHA512).Hash.ToLower()
            if ($actual -ne $published) {
                Remove-Item $dest -Force -ErrorAction SilentlyContinue
                throw "SHA-512 mismatch for $name. Expected $published, got $actual."
            }
            Say "SHA-512 verified" "Green"
            return $true
        } catch [System.Net.WebException] {
            continue
        }
    }
    return $false
}

function Install-Component([string]$name, [string]$target) {
    if (Test-Path $target) {
        Say "$name already at $target" "Green"
        return
    }
    $zip = Join-Path $env:TEMP "$name.zip"
    if (-not (Test-Path $zip)) {
        if (-not (Get-ApacheZip "$name.zip" $zip)) {
            throw "Could not download $name.zip from the Apache CDN or archive. Fetch it by hand from https://jena.apache.org/download/index.cgi and unpack it to $target."
        }
    }
    Say "unpacking to $target" "Yellow"
    $parent = Split-Path -Parent $target
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Expand-Archive -Path $zip -DestinationPath $parent -Force
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $target)) {
        throw "Unpacked $name but $target is not there. Check what the archive contained."
    }
    Say "$name installed" "Green"
}

if ($Install) {
    Write-Host ""
    Write-Host "Installing Apache Jena $Version and Fuseki $Version" -ForegroundColor Cyan
    Write-Host ""
    Install-Component "apache-jena-$Version"        $JenaHome
    Install-Component "apache-jena-fuseki-$Version" $FusekiHome
    Write-Host ""
}

# ---------------------------------------------------------------- resolve
# Release and snapshot builds differ only in the directory name, so a missing
# path falls back to whichever apache-jena-fuseki-* is actually installed.
function Resolve-Sibling([string]$preferred, [string]$filter) {
    if (Test-Path $preferred) { return $preferred }
    $parent = Split-Path -Parent $preferred
    $found = Get-ChildItem -Path $parent -Directory -Filter $filter `
             -ErrorAction SilentlyContinue | Sort-Object Name -Descending |
             Select-Object -First 1
    if ($found) { return $found.FullName }
    return $preferred
}

$FusekiHome = Resolve-Sibling $FusekiHome "apache-jena-fuseki-*"
$JenaHome   = Resolve-Sibling $JenaHome   "apache-jena-[0-9]*"
if (-not (Test-Path $FusekiJar)) { $FusekiJar = Join-Path $FusekiHome "fuseki-server.jar" }

if (-not (Test-Path $FusekiHome)) {
    throw "Fuseki not found at $FusekiHome. Run this script with -Install, or pass -FusekiHome."
}
if (-not (Test-Path $JenaHome)) {
    throw "Jena not found at $JenaHome. Run this script with -Install, or pass -JenaHome."
}
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    throw "No java on PATH. Jena 6 needs Java 17 or newer; https://adoptium.net has builds."
}

$dataFile = Join-Path $root "data\$Data"
$store = Join-Path $root "build\fuseki-tdb2"
if (-not (Test-Path $dataFile)) {
    throw "No such data file: $dataFile.  Run: python scripts/build_dataset.py"
}

$env:JENA_HOME = $JenaHome

# ---------------------------------------------------------------- load
Write-Host "Loading $Data into a TDB2 store at build\fuseki-tdb2 ..." -ForegroundColor Cyan
if (Test-Path $store) { Remove-Item -Recurse -Force $store }
New-Item -ItemType Directory -Force -Path $store | Out-Null

& "$JenaHome\bat\tdb2_tdbloader.bat" --loc="$store" "$dataFile"
if ($LASTEXITCODE -ne 0) { throw "tdbloader failed with exit code $LASTEXITCODE" }

$countQuery = Join-Path $env:TEMP "bookshop-count.rq"
Set-Content -Path $countQuery -Value "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"
& "$JenaHome\bat\tdb2_tdbquery.bat" --loc="$store" --query="$countQuery"
Remove-Item $countQuery -ErrorAction SilentlyContinue

Write-Host "Loaded." -ForegroundColor Green

# ---------------------------------------------------------------- GeoSPARQL
$libDir  = Join-Path $root "lib\geosparql"
$sisData = Join-Path $root "build\sis-data"
$cp = $FusekiJar
if (Test-Path $libDir) {
    $cp = @($FusekiJar, "$libDir\*") -join ";"
    if (Test-Path $sisData) { $env:SIS_DATA = $sisData }
    Write-Host "GeoSPARQL: lib\geosparql is on the classpath" -ForegroundColor Green
} else {
    Write-Warning "lib\geosparql not found. The geof: functions will load, but coordinate reference systems other than CRS84 will not resolve. Run ./scripts/setup-geosparql.ps1 -AcceptEpsgTerms first."
}

if ($LoadOnly) {
    Write-Host ""
    Write-Host "Store is at $store.  Start Fuseki yourself with:"
    Write-Host "  java -cp '$cp' org.apache.jena.fuseki.main.cmds.FusekiServerUICmd --loc=$store /$DatasetName"
    Write-Host ""
    Write-Host "  fuseki-server.bat works too, but without lib\geosparql on the"
    Write-Host "  classpath the geof: functions lose their coordinate systems."
    return
}

Write-Host ""
Write-Host "Starting Fuseki on http://localhost:$Port/$DatasetName" -ForegroundColor Cyan
Write-Host "  query UI : http://localhost:$Port/#/dataset/$DatasetName/query"
Write-Host "  endpoint : http://localhost:$Port/$DatasetName/sparql"
Write-Host "  stop     : Ctrl+C"
Write-Host ""
Write-Host "  Try module 10's q58 in the query UI: it should return no rows," -ForegroundColor Gray
Write-Host "  which is how the data proves every settlement really does sit"  -ForegroundColor Gray
Write-Host "  inside the polygon it claims."                                  -ForegroundColor Gray
Write-Host ""

& java -Xmx2G -cp $cp org.apache.jena.fuseki.main.cmds.FusekiServerUICmd `
    --port=$Port --loc="$store" "/$DatasetName"

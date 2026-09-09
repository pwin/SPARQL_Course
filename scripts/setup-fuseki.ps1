<#
.SYNOPSIS
    Download and install Apache Jena Fuseki from https://jena.apache.org/download/index.cgi
    Load the Bookshop Trail into Apache Jena Fuseki and start it.

.DESCRIPTION
    Creates a TDB2 dataset, loads the RDF 1.2 Turtle file into it, and starts
    Fuseki on http://localhost:3030/bookshop.  The SPARQL endpoint is then at
    http://localhost:3030/bookshop/sparql and Fuseki's own query page at
    http://localhost:3030/#/dataset/bookshop/query.

    GeoSPARQL: fuseki-server.jar already contains Jena's GeoSPARQL
    implementation, so the geof: functions are available.  Run
    scripts/setup-geosparql.ps1 first to add Apache Derby and the EPSG
    dataset, without which projected coordinate systems such as EPSG:27700
    are not recognised.

.EXAMPLE
    ./scripts/setup-fuseki.ps1
    ./scripts/setup-fuseki.ps1 -Port 3131 -Data bookshop-trail-full.ttl
#>
param(
    [string]$FusekiHome = "C:\apache-jena-fuseki-6.2.0",
    [string]$FusekiJar  = "C:\apache-jena-fuseki-6.2.0\fuseki-server.jar",
    [string]$JenaHome   = "C:\apache-jena-6.2.0",
    [string]$Data       = "bookshop-trail-1.2.ttl",
    [string]$DatasetName = "bookshop",
    [int]$Port          = 3030,
    [switch]$LoadOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# The Fuseki directory name differs between a release and a snapshot build, so
# the default above is a preference rather than a requirement: if it is not
# there, take the newest apache-jena-fuseki-* sitting beside it.
function Resolve-Fuseki([string]$preferred) {
    if (Test-Path $preferred) { return $preferred }
    $parent = Split-Path -Parent $preferred
    $found = Get-ChildItem -Path $parent -Directory -Filter "apache-jena-fuseki-*" `
             -ErrorAction SilentlyContinue | Sort-Object Name -Descending |
             Select-Object -First 1
    if ($found) { return $found.FullName }
    return $preferred
}

$FusekiHome = Resolve-Fuseki $FusekiHome
if (-not (Test-Path $FusekiJar)) {
    $FusekiJar = Join-Path $FusekiHome "fuseki-server.jar"
}
$dataFile = Join-Path $root "data\$Data"
$store = Join-Path $root "build\fuseki-tdb2"

if (-not (Test-Path $dataFile)) {
    throw "No such data file: $dataFile.  Run: python scripts/build_dataset.py"
}
if (-not (Test-Path $FusekiHome)) {
    throw "Fuseki not found at $FusekiHome.  Pass -FusekiHome."
}

$env:JENA_HOME = $JenaHome

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

if ($LoadOnly) {
    Write-Host "Store is at $store.  Start Fuseki yourself with:"
    $geoCp = Join-Path $root "lib\geosparql"
    Write-Host "  java -cp '$FusekiJar;$geoCp\*' org.apache.jena.fuseki.main.cmds.FusekiServerUICmd --loc=$store /$DatasetName"
    Write-Host ""
    Write-Host "  fuseki-server.bat works too, but without lib\geosparql on the"
    Write-Host "  classpath the geof: functions lose their coordinate systems."
    return
}

# ---------------------------------------------------------------- GeoSPARQL
# fuseki-server.jar already carries Jena's GeoSPARQL implementation.  What it
# lacks is Apache Derby and the EPSG dataset, which SIS needs for coordinate
# reference systems.  scripts/setup-geosparql.ps1 puts both in lib\geosparql.
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

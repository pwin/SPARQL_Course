<#
.SYNOPSIS
    Turn on GeoSPARQL for Apache Jena, so module 10 runs on Fuseki as well as
    HOLOS.

.DESCRIPTION
    Three things are needed, and only the first is obvious.

    1. The geof: functions.  Jena ships them in `jena-geosparql`, but the ARQ
       command line does not put that on the classpath, so a geof: call
       resolves to nothing and quietly returns unbound. Fuseki's
       self-contained jar carries the whole implementation, so adding that jar
       to the classpath brings the functions in. No download needed.

    2. Apache Derby.  Jena's GeoSPARQL uses Apache SIS for coordinate
       reference systems, and SIS keeps its CRS database in an embedded Derby
       database. Derby is not bundled. This script takes the jars from a local
       Apache SIS installation if there is one, and downloads them otherwise.

    3. The EPSG geodetic dataset.  SIS ships without it, because the EPSG
       terms of use require the user to accept them rather than a
       redistributor. Without it you get, on every geometry that names a
       projected system:

           SRS URI not recognised ... No CoordinateReferenceSystem object
           found for code "27700"

       The dataset is published on Maven Central as
       org.apache.sis.non-free:sis-epsg. Fetching it is what -AcceptEpsgTerms
       confirms; see https://epsg.org/terms-of-use.html.

    The script then builds the database and verifies the result with a real
    query, rather than assuming it worked.

.PARAMETER AcceptEpsgTerms
    Confirms you accept the EPSG dataset terms of use. Required to download
    the sis-epsg artifact. Without it the script still installs everything
    else, and the topological functions still work -- only projected
    coordinate systems such as EPSG:27700 are lost.

.EXAMPLE
    ./scripts/setup-geosparql.ps1 -AcceptEpsgTerms
    ./scripts/setup-geosparql.ps1 -Verify
#>
param(
    [string]$FusekiJar  = "C:\apache-jena-fuseki-6.2.0\fuseki-server.jar",
    [string]$JenaHome   = "C:\apache-jena-6.2.0",
    [string]$SisHome    = "C:\apache-sis-1.6",
    [string]$SisEpsgVersion = "1.4",
    [switch]$AcceptEpsgTerms,
    [switch]$Verify
)

$ErrorActionPreference = "Stop"
$root    = Split-Path -Parent $PSScriptRoot

# Release and snapshot builds differ only in the directory name, so fall back
# to whichever apache-jena-fuseki-* is actually installed.
if (-not (Test-Path $FusekiJar)) {
    $parent = Split-Path -Parent (Split-Path -Parent $FusekiJar)
    $found = Get-ChildItem -Path $parent -Directory -Filter "apache-jena-fuseki-*" `
             -ErrorAction SilentlyContinue | Sort-Object Name -Descending |
             ForEach-Object { Join-Path $_.FullName "fuseki-server.jar" } |
             Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($found) { $FusekiJar = $found }
}
$libDir  = Join-Path $root "lib\geosparql"
$sisData = Join-Path $root "build\sis-data"

function Say($msg, $colour = "Gray") { Write-Host "  $msg" -ForegroundColor $colour }

Write-Host ""
Write-Host "GeoSPARQL for Jena" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------- 1. the functions
if (-not (Test-Path $FusekiJar)) {
    throw "Fuseki jar not found at $FusekiJar. It carries Jena's GeoSPARQL implementation; pass -FusekiJar."
}
Say "geof: functions      found in $(Split-Path -Leaf $FusekiJar)" "Green"

New-Item -ItemType Directory -Force -Path $libDir | Out-Null

# ---------------------------------------------------------------- 2. Derby
$derbyJars = @("org.apache.derby.engine.jar",
               "org.apache.derby.commons.jar",
               "org.apache.derby.tools.jar")
$haveDerby = $true
foreach ($j in $derbyJars) {
    if (-not (Test-Path (Join-Path $libDir $j))) { $haveDerby = $false }
}

if (-not $haveDerby) {
    $sisLib = Join-Path $SisHome "lib"
    if (Test-Path $sisLib) {
        foreach ($j in $derbyJars) {
            $src = Join-Path $sisLib $j
            if (Test-Path $src) { Copy-Item $src $libDir -Force }
        }
        Say "Apache Derby        copied from $sisLib" "Green"
    } else {
        Say "Apache Derby        no local Apache SIS; downloading from Maven Central" "Yellow"
        $derbyVer = "10.15.2.0"
        $maven = "https://repo1.maven.org/maven2/org/apache/derby"
        foreach ($a in @("derby", "derbyshared", "derbytools")) {
            $url = "$maven/$a/$derbyVer/$a-$derbyVer.jar"
            $out = Join-Path $libDir "$a-$derbyVer.jar"
            if (-not (Test-Path $out)) { Invoke-WebRequest -Uri $url -OutFile $out }
        }
        Say "Apache Derby        downloaded" "Green"
    }
} else {
    Say "Apache Derby        already in lib\geosparql" "Green"
}

# ---------------------------------------------------------------- 3. the EPSG dataset
$epsgJar = Join-Path $libDir "sis-epsg-$SisEpsgVersion.jar"
if (Test-Path $epsgJar) {
    Say "EPSG dataset        already in lib\geosparql" "Green"
} elseif ($AcceptEpsgTerms) {
    $url = "https://repo1.maven.org/maven2/org/apache/sis/non-free/sis-epsg/$SisEpsgVersion/sis-epsg-$SisEpsgVersion.jar"
    Say "EPSG dataset        downloading $url" "Yellow"
    Invoke-WebRequest -Uri $url -OutFile $epsgJar
    Say "EPSG dataset        downloaded" "Green"
} else {
    Say "EPSG dataset        SKIPPED -- re-run with -AcceptEpsgTerms to include it" "Yellow"
    Say "                    Without it, projected systems such as EPSG:27700" "Yellow"
    Say "                    are not recognised. Topology still works." "Yellow"
}

# ---------------------------------------------------------------- build and verify
$cp = @("$JenaHome\lib\*", $FusekiJar, "$libDir\*") -join ";"
New-Item -ItemType Directory -Force -Path $sisData | Out-Null
$env:SIS_DATA = $sisData

$probe = Join-Path $env:TEMP "geosparql-probe.rq"
@'
PREFIX geo:  <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX bs:   <https://example.org/bookshop-trail/schema#>
SELECT (COUNT(*) AS ?inside) WHERE {
  ?s a bs:Settlement ; bs:within ?c ; geo:hasDefaultGeometry/geo:asWKT ?point .
  ?c a bs:CouncilArea ; geo:hasDefaultGeometry/geo:asWKT ?polygon .
  FILTER( geof:sfWithin(?point, ?polygon) )
}
'@ | Set-Content -Path $probe -Encoding UTF8

$data = Join-Path $root "data\bookshop-trail-full.ttl"
if (-not (Test-Path $data)) { throw "No dataset at $data. Run: python scripts/build_dataset.py" }

Write-Host ""
Say "Building the CRS database and verifying (first run takes a minute)..." "Cyan"
$out = & java -cp $cp arq.sparql --data=$data --query=$probe --results=csv 2>&1
$inside = ($out | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)

Write-Host ""
if ($inside -eq "30") {
    Say "geof:sfWithin       30 of 30 settlements inside their council area" "Green"
    Say "                    GeoSPARQL is working on Jena." "Green"
} else {
    Say "geof:sfWithin       expected 30, got '$inside'" "Red"
    Say "                    Something is not right; the raw output follows." "Red"
    $out | Select-Object -First 12 | ForEach-Object { Write-Host "      $_" }
}

Write-Host ""
Write-Host "  What now works on Jena, and what does not" -ForegroundColor Cyan
Write-Host @"
    topological     sfWithin sfIntersects sfContains sfCrosses sfTouches
                    sfDisjoint sfEquals sfOverlaps, and the Egenhofer and
                    RCC8 families                                    WORKS
    constructors    envelope boundary convexHull buffer
                    intersection union difference                    WORKS
    getSRID         reports the declared reference system            WORKS
    distance        in degrees or radians                            WORKS
    distance        in metres or kilometres                          UNBOUND
    area, length    in any unit                                      UNBOUND

  The last two are a limitation of this Jena build, not of the setup: the
  call succeeds, returns HTTP 200, and leaves the variable unbound. Course
  module 10 marks q57, q59 and q60 as HOLOS-only for that reason, and q58
  as running on both. Module 09 answers the same questions with arithmetic
  alone, on every engine.

  The harness picks all this up automatically:
      python scripts/check_queries.py q58
"@ -ForegroundColor Gray
Write-Host ""

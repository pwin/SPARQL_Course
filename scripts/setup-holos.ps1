<#
.SYNOPSIS
    Load the Bookshop Trail into HOLOS, and optionally start its HTTP server.

.DESCRIPTION
    HOLOS runs a query straight from a file with no server at all, which is the
    quickest way to try one:

        holos query --data data\bookshop-trail-1.2.ttl --query-file queries\...\q27-....rq

    This script builds a persistent RocksDB store so repeated queries do not
    re-parse the data, and can start the SPARQL 1.2 Protocol server with its
    YASGUI console on http://localhost:7878.

.EXAMPLE
    ./scripts/setup-holos.ps1
    ./scripts/setup-holos.ps1 -Serve
    ./scripts/setup-holos.ps1 -Query queries\05-property-paths\q31-walking-the-trail-in-either-direction.rq
#>
param(
    [string]$HolosExe = "C:\repos\new_triplestore_sparql_engine\target\release\holos.exe",
    [string]$Data     = "bookshop-trail-full.ttl",
    [string]$Query,
    [switch]$Serve,
    [int]$Port = 7878
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$dataFile = Join-Path $root "data\$Data"
$store = Join-Path $root "build\holos-store"

if (-not (Test-Path $HolosExe)) {
    throw "holos.exe not found at $HolosExe.  Build it with: cargo build --release"
}
if (-not (Test-Path $dataFile)) {
    throw "No such data file: $dataFile.  Run: python scripts/build_dataset.py"
}

if ($Query) {
    $queryFile = if (Test-Path $Query) { $Query } else { Join-Path $root $Query }
    if (-not (Test-Path $queryFile)) { throw "No such query file: $Query" }
    & $HolosExe query --data $dataFile --query-file $queryFile
    return
}

Write-Host "Loading $Data into a RocksDB store at build\holos-store ..." -ForegroundColor Cyan
if (Test-Path $store) { Remove-Item -Recurse -Force $store }

& $HolosExe update --store $store --update "INSERT DATA {}" 2>$null | Out-Null
& $HolosExe query --data $dataFile --store $store --bulk `
    --query "SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }"
if ($LASTEXITCODE -ne 0) { throw "load failed with exit code $LASTEXITCODE" }

Write-Host "Loaded." -ForegroundColor Green

if (-not $Serve) {
    Write-Host ""
    Write-Host "Run a query against the store with:"
    Write-Host "  $HolosExe query --store $store --query-file <file.rq>"
    Write-Host "Or straight from the Turtle, with no store at all:"
    Write-Host "  $HolosExe query --data $dataFile --query-file <file.rq>"
    return
}

$server = Join-Path (Split-Path -Parent $HolosExe) "holos-server.exe"
if (-not (Test-Path $server)) { throw "holos-server.exe not found next to holos.exe" }

Write-Host ""
Write-Host "Starting the HOLOS server on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "  console  : http://localhost:$Port  (YASGUI)"
Write-Host "  endpoint : http://localhost:$Port/query"
Write-Host ""

& $server --store $store --port $Port

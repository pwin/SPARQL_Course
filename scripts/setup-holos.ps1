<#
.SYNOPSIS
    Build HOLOS if it is not already here, load the Bookshop Trail into it,
    and optionally start its HTTP server.

.DESCRIPTION
    HOLOS is an RDF 1.2 triplestore with SPARQL 1.2 and 45 GeoSPARQL
    functions. It has no binary release: with -Install this script clones the
    source and builds it, which needs a Rust toolchain and takes several
    minutes the first time.

    Once built, HOLOS answers a query straight from a Turtle file with no
    server at all, which is the quickest way to try one:

        ./scripts/setup-holos.ps1 -Query queries\05-property-paths\q31-*.rq

    Without -Query it builds a persistent RocksDB store so repeated queries do
    not re-parse the data, and with -Serve it starts the SPARQL 1.2 Protocol
    server and its YASGUI console on http://localhost:7878.

    Of the three environments this course targets, HOLOS is the only one that
    answers module 10 in full: geof:distance in metres, geof:area and
    geof:length all return values here and come back unbound on Jena.

.PARAMETER Install
    Clone and build HOLOS. Needs Rust 1.87 or newer -- https://rustup.rs --
    and a working C toolchain for RocksDB. Expect five to fifteen minutes for
    a release build on a first run.

.EXAMPLE
    ./scripts/setup-holos.ps1 -Install
    ./scripts/setup-holos.ps1
    ./scripts/setup-holos.ps1 -Serve
    ./scripts/setup-holos.ps1 -Query queries\05-property-paths\q31-walking-the-trail-in-either-direction.rq
#>
param(
    [string]$HolosRepo = "https://github.com/pwin/triplestore.git",
    [string]$HolosSrc  = "C:\repos\new_triplestore_sparql_engine",
    [string]$HolosExe,
    [string]$Data      = "bookshop-trail-full.ttl",
    [string]$Query,
    [switch]$Install,
    [switch]$Serve,
    [int]$Port = 7878
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $HolosExe) { $HolosExe = Join-Path $HolosSrc "target\release\holos.exe" }

function Say($msg, $colour = "Gray") { Write-Host "  $msg" -ForegroundColor $colour }

# ---------------------------------------------------------------- install
if ($Install -and -not (Test-Path $HolosExe)) {
    Write-Host ""
    Write-Host "Building HOLOS" -ForegroundColor Cyan
    Write-Host ""

    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw "No cargo on PATH. HOLOS is a Rust project: install a toolchain from https://rustup.rs (1.87 or newer), open a new shell, and run this again."
    }
    $rustc = (& rustc --version) -replace '^rustc\s+([0-9.]+).*', '$1'
    Say "rust                $rustc" "Green"

    if (-not (Test-Path $HolosSrc)) {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            throw "No git on PATH, and no source at $HolosSrc. Clone $HolosRepo by hand, or install git."
        }
        Say "cloning $HolosRepo" "Yellow"
        $parent = Split-Path -Parent $HolosSrc
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        & git clone --depth 1 $HolosRepo $HolosSrc
        if ($LASTEXITCODE -ne 0) { throw "git clone failed with exit code $LASTEXITCODE" }
    } else {
        Say "source              already at $HolosSrc" "Green"
    }

    Say "cargo build --release  (several minutes on a first run)" "Yellow"
    Push-Location $HolosSrc
    try {
        & cargo build --release
        if ($LASTEXITCODE -ne 0) {
            throw "cargo build failed with exit code $LASTEXITCODE. RocksDB needs a C toolchain; on Windows that means the Visual Studio Build Tools with the C++ workload."
        }
    } finally {
        Pop-Location
    }
    Write-Host ""
}

if (-not (Test-Path $HolosExe)) {
    throw "holos.exe not found at $HolosExe. Run this script with -Install to clone and build it, or pass -HolosExe if you have it elsewhere."
}

$dataFile = Join-Path $root "data\$Data"
if (-not (Test-Path $dataFile)) {
    throw "No such data file: $dataFile.  Run: python scripts/build_dataset.py"
}
$store = Join-Path $root "build\holos-store"

# ---------------------------------------------------------------- one query
if ($Query) {
    $queryFile = if (Test-Path $Query) { $Query } else { Join-Path $root $Query }
    if (-not (Test-Path $queryFile)) {
        # a glob such as q31-*.rq is a convenience worth supporting
        $match = Get-ChildItem -Path (Join-Path $root "queries") -Recurse -Filter (Split-Path -Leaf $Query) `
                 -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) { $queryFile = $match.FullName } else { throw "No such query file: $Query" }
    }
    Write-Host ""
    Say "running $(Split-Path -Leaf $queryFile) against $Data" "Cyan"
    Write-Host ""
    & $HolosExe query --data $dataFile --query-file $queryFile
    return
}

# ---------------------------------------------------------------- load
Write-Host "Loading $Data into a RocksDB store at build\holos-store ..." -ForegroundColor Cyan
if (Test-Path $store) { Remove-Item -Recurse -Force $store }

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
    Write-Host ""
    Write-Host "  Module 10 is the one to try here: HOLOS is the only engine of" -ForegroundColor Gray
    Write-Host "  the three that answers geof:distance in metres."               -ForegroundColor Gray
    return
}

$server = Join-Path (Split-Path -Parent $HolosExe) "holos-server.exe"
if (-not (Test-Path $server)) {
    throw "holos-server.exe not found next to holos.exe. It is built by the same cargo build --release; check that the build completed."
}

Write-Host ""
Write-Host "Starting the HOLOS server on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "  console  : http://localhost:$Port  (YASGUI)"
Write-Host "  endpoint : http://localhost:$Port/query"
Write-Host "  stop     : Ctrl+C"
Write-Host ""

& $server --store $store --port $Port

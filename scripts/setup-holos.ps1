<#
.SYNOPSIS
    Install HOLOS if it is not already here, load the Bookshop Trail into it,
    and optionally start its HTTP server.

.DESCRIPTION
    HOLOS is an RDF 1.2 triplestore with SPARQL 1.2 and 45 GeoSPARQL
    functions. It is part of SemOps System (https://github.com/pwin/SemopsSystem),
    the same engine the Turtle Editor Viewer runs in the browser. With -Install
    this script downloads the Windows release from GitHub (about 11 MB), checks
    it against the SHA256SUMS published with the release, and unpacks holos.exe
    and holos-server.exe under lib\holos\.
    Nothing is installed system-wide: deleting lib\holos undoes it.

    Once installed, HOLOS answers a query straight from a Turtle file with no
    server at all, which is the quickest way to try one:

        ./scripts/setup-holos.ps1 -Query queries\05-property-paths\q31-*.rq

    Without -Query it builds a persistent RocksDB store so repeated queries do
    not re-parse the data, and with -Serve it starts the SPARQL 1.2 Protocol
    server and its YASGUI console on http://localhost:7878.

    Of the three environments this course targets, HOLOS is the only one that
    answers module 10 in full: geof:distance in metres, geof:area and
    geof:length all return values here and come back unbound on Jena.

.PARAMETER Install
    Download, verify and unpack the HOLOS release named by -Version. Skipped
    if that version is already under lib\holos. A superseded version there is
    removed, so scripts\check_queries.py finds the one this script installed.

.PARAMETER Version
    The HOLOS release to install: a SemOps System release, which carries the
    holos binaries beside semops, shacl and tarka. Releases, with builds for
    macOS and Linux too, are listed at https://github.com/pwin/SemopsSystem/releases.
    Keep it at the version the editor runs, so the editor and HOLOS columns
    measure one engine.

.PARAMETER FromSource
    With -Install, clone the SemOps System workspace and build HOLOS from it
    instead of downloading it. Needs Rust 1.90 or newer -- https://rustup.rs --
    and a C toolchain for RocksDB;
    on Windows, the Visual Studio Build Tools with the C++ workload. Expect
    five to fifteen minutes for a first release build.

.EXAMPLE
    ./scripts/setup-holos.ps1 -Install
    ./scripts/setup-holos.ps1
    ./scripts/setup-holos.ps1 -Serve
    ./scripts/setup-holos.ps1 -Query queries\05-property-paths\q31-walking-the-trail-in-either-direction.rq
#>
param(
    [string]$Version   = "0.31.0",
    [string]$InstallTo,
    [string]$HolosExe,
    [string]$Data      = "bookshop-trail-full.ttl",
    [string]$Query,
    [switch]$Install,
    [switch]$FromSource,
    [string]$HolosRepo = "https://github.com/pwin/SemopsSystem.git",
    [string]$HolosSrc  = "C:\repos\SemopsSystem",
    [switch]$Serve,
    [int]$Port = 7878
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $InstallTo) { $InstallTo = Join-Path $root "lib\holos" }

$stem       = "holos-$Version-x86_64-pc-windows-msvc"
$releaseExe = Join-Path $InstallTo "$stem\holos.exe"
$sourceExe  = Join-Path $HolosSrc "target\release\holos.exe"
if (-not $HolosExe) {
    # The release under lib\holos unless asked to build, or unless there is no
    # release here but a source build already exists.
    $HolosExe = if ($FromSource) { $sourceExe }
                elseif ((Test-Path $releaseExe) -or $Install -or -not (Test-Path $sourceExe)) { $releaseExe }
                else { $sourceExe }
}

function Say($msg, $colour = "Gray") { Write-Host "  $msg" -ForegroundColor $colour }

# ---------------------------------------------------------------- install: release
function Install-Release {
    Write-Host ""
    Write-Host "Installing HOLOS $Version" -ForegroundColor Cyan
    Write-Host ""

    $base  = "https://github.com/pwin/SemopsSystem/releases/download/v$Version"
    $asset = "$stem.zip"
    # Invoke-WebRequest's progress bar slows Windows PowerShell's downloads
    # many times over.
    $ProgressPreference = "SilentlyContinue"

    try {
        $sums = (Invoke-WebRequest -Uri "$base/SHA256SUMS" -UseBasicParsing).Content
    } catch {
        throw "Could not fetch $base/SHA256SUMS. Is v$Version a SemOps System release? They are listed at https://github.com/pwin/SemopsSystem/releases."
    }
    if ($sums -is [byte[]]) { $sums = [System.Text.Encoding]::UTF8.GetString($sums) }
    $line = $sums -split "`n" | Where-Object { $_.Trim().EndsWith($asset) } | Select-Object -First 1
    if (-not $line) { throw "$asset is not listed in the SHA256SUMS of v$Version." }
    $published = ($line.Trim() -split '\s+')[0].ToLower()

    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("holos-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        $zip = Join-Path $tmp $asset
        Say "downloading $base/$asset" "Yellow"
        Invoke-WebRequest -Uri "$base/$asset" -OutFile $zip -UseBasicParsing
        # A download that cannot be verified is not worth unpacking.
        $actual = (Get-FileHash -Path $zip -Algorithm SHA256).Hash.ToLower()
        if ($actual -ne $published) {
            throw "SHA-256 mismatch for $asset. SHA256SUMS says $published, the download is $actual."
        }
        Say "SHA-256 verified against SHA256SUMS" "Green"

        New-Item -ItemType Directory -Force -Path $InstallTo | Out-Null
        Expand-Archive -Path $zip -DestinationPath $InstallTo -Force
    } finally {
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    }
    if (-not (Test-Path $releaseExe)) {
        throw "Unpacked $asset but $releaseExe is not there. Check what the archive contained."
    }
    # Only this version stays, so nothing that looks under lib\holos can pick
    # up a superseded one.
    Get-ChildItem -Path $InstallTo -Directory -Filter "holos-*" |
        Where-Object { $_.Name -ne $stem } |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName; Say "removed the superseded $($_.Name)" "Yellow" }
    Say "holos.exe and holos-server.exe are in $(Split-Path -Parent $releaseExe)" "Green"

    # The Windows build links the Visual C++ runtime. Most machines have it
    # already; on one that does not, holos.exe cannot start at all.
    $ver = & $releaseExe --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "holos.exe is installed but does not start (exit code $LASTEXITCODE). It needs the Microsoft Visual C++ Redistributable for Visual Studio 2015-2022 (x64): https://aka.ms/vs/17/release/vc_redist.x64.exe"
    }
    Say "$ver" "Green"
    Write-Host ""
}

# ---------------------------------------------------------------- install: source
function Install-FromSource {
    Write-Host ""
    Write-Host "Building HOLOS from source" -ForegroundColor Cyan
    Write-Host ""

    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw "No cargo on PATH. Install a Rust toolchain from https://rustup.rs (1.90 or newer), open a new shell, and run this again -- or drop -FromSource to download the release instead."
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

    Say "cargo build --release -p holos-cli -p holos-server  (several minutes on a first run)" "Yellow"
    Push-Location $HolosSrc
    try {
        # The workspace builds every engine; these two packages are holos.exe
        # and holos-server.exe.
        & cargo build --release -p holos-cli -p holos-server
        if ($LASTEXITCODE -ne 0) {
            throw "cargo build failed with exit code $LASTEXITCODE. RocksDB needs a C toolchain; on Windows that means the Visual Studio Build Tools with the C++ workload."
        }
    } finally {
        Pop-Location
    }
    Write-Host ""
}

if ($Install -and -not (Test-Path $HolosExe)) {
    if ($FromSource) { Install-FromSource } else { Install-Release }
}

if (-not (Test-Path $HolosExe)) {
    throw "holos.exe not found at $HolosExe. Run this script with -Install to download it, or pass -HolosExe if you have it elsewhere."
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
    throw "holos-server.exe not found next to holos.exe. The release archive carries both, and a source build makes both; check that the install completed."
}

Write-Host ""
Write-Host "Starting the HOLOS server on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "  console  : http://localhost:$Port  (YASGUI)"
Write-Host "  endpoint : http://localhost:$Port/query"
Write-Host "  stop     : Ctrl+C"
Write-Host ""

& $server --store $store --listen "127.0.0.1:$Port"

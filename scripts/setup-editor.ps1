<#
.SYNOPSIS
    Start the Turtle Editor Viewer, the browser lab this course is built around.

.DESCRIPTION
    Copies the course data into the editor's public folder so it can be loaded
    by URL, then starts the Vite dev server.  Open the printed address, use
    "Choose File" to load a module, and query it in the SPARQL panel.

    The editor needs Node 22 or newer.  If `node --version` reports anything
    older, pass -NodeExe with the path to a newer one; nvm-for-Windows users
    will find them under ~\.nvm\versions\node.

.EXAMPLE
    ./scripts/setup-editor.ps1
    ./scripts/setup-editor.ps1 -NodeExe "$HOME\.nvm\versions\node\v22.21.1\bin\node.exe"
#>
param(
    [string]$EditorHome = "C:\repos\turtle-editor-viewer",
    [string]$NodeExe,
    [switch]$NoCopy,
    [switch]$NoServe
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path $EditorHome)) {
    throw "Editor not found at $EditorHome.  Pass -EditorHome."
}

if ($NodeExe) {
    $nodeDir = Split-Path -Parent $NodeExe
    $env:PATH = "$nodeDir;$env:PATH"
}
$nodeVersion = (& node --version) -replace '^v', ''
$major = [int]($nodeVersion -split '\.')[0]
if ($major -lt 22) {
    Write-Warning "Node $nodeVersion found; the editor's package.json asks for >= 22. Comunica's HTTP layer fails to load on Node 20. Pass -NodeExe with a newer one."
}

if (-not $NoCopy) {
    $target = Join-Path $EditorHome "public\bookshop-trail"
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item (Join-Path $root "data\*.ttl")  $target -Force
    Copy-Item (Join-Path $root "data\*.trig") $target -Force
    Write-Host "Copied the dataset to $target" -ForegroundColor Green
    Write-Host "  Once the server is up, the files are at, for example:"
    Write-Host "  http://localhost:5173/bookshop-trail/04-bookshops.ttl"
}

if ($NoServe) { return }

Write-Host ""
Write-Host "Starting the Turtle Editor Viewer..." -ForegroundColor Cyan
Write-Host "  Load a module with Choose File, or paste one in."
Write-Host "  Start with data/04-bookshops.ttl -- it is small enough to see whole."
Write-Host ""

Push-Location $EditorHome
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing dependencies (first run only)..." -ForegroundColor Cyan
        & npm install
    }
    & npm run dev
} finally {
    Pop-Location
}

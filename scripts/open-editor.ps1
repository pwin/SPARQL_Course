<#
.SYNOPSIS
    Open the Turtle Editor Viewer with one of the course files already loaded.

.DESCRIPTION
    The editor is used online, at https://semantechs.co.uk/turtle-editor-viewer/.
    There is nothing to install and nothing to run locally: it is a browser
    application, and the course is built around that.

    It accepts ?dot=<url> and loads that URL into the editor pane, and
    &shapes=<url> to open a SHACL shapes file in a second tab already selected
    for validation, so this script simply assembles the link and opens it.
    The files come from the course's own raw URLs on GitHub, which send the
    CORS header the editor needs.

    With no arguments it lists the files and opens the shops, which is the one
    to start with: small enough for the graph view to draw whole.

.PARAMETER File
    A file from data/, with or without the .ttl extension. Tab-completion of
    the folder is easier than remembering them.

.PARAMETER Shapes
    A shapes file from data/, opened alongside the data for validation.
    Usually shapes or shapes-advanced.

.PARAMETER List
    Print the files and their links without opening anything.

.PARAMETER Branch
    Which branch of the course repository to load from. Defaults to main.

.EXAMPLE
    ./scripts/open-editor.ps1
    ./scripts/open-editor.ps1 04-bookshops
    ./scripts/open-editor.ps1 bookshop-trail-1.2.ttl
    ./scripts/open-editor.ps1 bookshop-trail-1.1 -Shapes shapes
    ./scripts/open-editor.ps1 -List
#>
param(
    [string]$File = "04-bookshops.ttl",
    [string]$Editor = "https://semantechs.co.uk/turtle-editor-viewer/",
    [string]$Repo = "https://raw.githubusercontent.com/pwin/SPARQL_Course",
    [string]$Branch = "main",
    [string]$Shapes,
    [switch]$List
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root "data"

function Raw([string]$name) { return "$Repo/$Branch/data/$name" }

function Link([string]$name, [string]$shapesName) {
    $url = $Editor + "?dot=" + [uri]::EscapeDataString((Raw $name))
    if ($shapesName) { $url += "&shapes=" + [uri]::EscapeDataString((Raw $shapesName)) }
    return $url
}

$files = Get-ChildItem -Path $dataDir -Filter "*.ttl" -ErrorAction SilentlyContinue |
         Sort-Object Name
$trig = Get-ChildItem -Path $dataDir -Filter "*.trig" -ErrorAction SilentlyContinue
if ($trig) { $files = @($files) + @($trig) }

if (-not $files) {
    throw "No data files in $dataDir.  Run: python scripts/build_dataset.py"
}

if ($List) {
    Write-Host ""
    Write-Host "The Turtle Editor Viewer, online at $Editor" -ForegroundColor Cyan
    Write-Host ""
    foreach ($f in $files) {
        $size = "{0,5:N0} KB" -f ($f.Length / 1KB)
        Write-Host ("  {0,-30} {1}" -f $f.Name, $size)
    }
    Write-Host ""
    Write-Host "  Open one with:  ./scripts/open-editor.ps1 <name>" -ForegroundColor Gray
    Write-Host "  Every query in the course document has its own link too."   -ForegroundColor Gray
    Write-Host ""
    return
}

if (-not $File.EndsWith(".ttl") -and -not $File.EndsWith(".trig")) { $File = "$File.ttl" }
$match = $files | Where-Object { $_.Name -eq $File } | Select-Object -First 1
if (-not $match) {
    Write-Host ""
    Write-Warning "No file called $File in data/. These are the ones there are:"
    $files | ForEach-Object { Write-Host "    $($_.Name)" }
    Write-Host ""
    return
}

$shapesMatch = $null
if ($Shapes) {
    if (-not $Shapes.EndsWith(".ttl")) { $Shapes = "$Shapes.ttl" }
    $shapesMatch = $files | Where-Object { $_.Name -eq $Shapes } | Select-Object -First 1
    if (-not $shapesMatch) {
        Write-Warning "No shapes file called $Shapes in data/. Try shapes or shapes-advanced."
        return
    }
}

$shapesName = $null
if ($shapesMatch) { $shapesName = $shapesMatch.Name }
$url = Link $match.Name $shapesName

Write-Host ""
$with = if ($shapesMatch) { "$($match.Name) and $($shapesMatch.Name)" } else { $match.Name }
Write-Host "Opening the Turtle Editor Viewer with $with" -ForegroundColor Cyan
Write-Host ""
Write-Host "  $url"
Write-Host ""
Write-Host "  The editor runs online; there is nothing to install." -ForegroundColor Gray
Write-Host "  It loads from the course's raw GitHub URLs, so the file has to be" -ForegroundColor Gray
Write-Host "  pushed to the $Branch branch before a link to it will work."       -ForegroundColor Gray
Write-Host ""
Write-Host "  Once it is open:" -ForegroundColor Gray
Write-Host "    - the graph pane draws the first ten subjects"                   -ForegroundColor Gray
Write-Host "    - Add Prefixes fills in the PREFIX block for your own queries"   -ForegroundColor Gray
Write-Host "    - Get All reloads the internal triplestore the SPARQL panel"     -ForegroundColor Gray
Write-Host "      queries: press it after editing, or your query sees the old"   -ForegroundColor Gray
Write-Host "      data and looks wrong"                                          -ForegroundColor Gray
if ($shapesMatch) {
Write-Host "    - the shapes are in their own tab, already chosen in the Shapes" -ForegroundColor Gray
Write-Host "      dropdown: stay on the data tab and press Validate"             -ForegroundColor Gray
}
Write-Host ""

Start-Process $url

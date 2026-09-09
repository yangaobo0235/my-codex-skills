[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$SkipPlugins,
    [string]$CodexHomePath,
    [string]$CodexCommand = 'codex'
)

$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
$manifestPath = Join-Path $repoRoot 'skills-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Missing manifest: $manifestPath"
}

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
if ($manifest.schemaVersion -ne 1) {
    throw "Unsupported manifest schema version: $($manifest.schemaVersion)"
}

if ([string]::IsNullOrWhiteSpace($CodexHomePath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        $CodexHomePath = $env:CODEX_HOME
    } else {
        $CodexHomePath = Join-Path $env:USERPROFILE '.codex'
    }
}

foreach ($skillName in $manifest.personalSkills) {
    $source = Join-Path (Join-Path $repoRoot 'skills') $skillName
    if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
        throw "Invalid personal skill '$skillName': SKILL.md was not found."
    }
}

Write-Output "Codex home: $CodexHomePath"
Write-Output "Personal skills: $(@($manifest.personalSkills).Count)"
Write-Output "Plugins: $(@($manifest.plugins).Count)"

if ($Check) {
    Write-Output 'Check complete. No files or plugin settings were changed.'
    return
}

$skillsRoot = Join-Path $CodexHomePath 'skills'
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null

foreach ($skillName in $manifest.personalSkills) {
    $source = Join-Path (Join-Path $repoRoot 'skills') $skillName
    $destination = Join-Path $skillsRoot $skillName

    if (Test-Path -LiteralPath $destination) {
        Write-Output "SKIP skill already exists: $skillName"
        continue
    }

    Copy-Item -LiteralPath $source -Destination $destination -Recurse
    Write-Output "INSTALLED skill: $skillName"
}

if ($SkipPlugins) {
    Write-Output 'Plugin installation skipped.'
    return
}

Get-Command $CodexCommand -ErrorAction Stop | Out-Null
$LASTEXITCODE = 0
$inventoryOutput = & $CodexCommand 'plugin' 'list' '--json' 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read the Codex plugin inventory: $($inventoryOutput -join [Environment]::NewLine)"
}

try {
    $inventory = $inventoryOutput -join [Environment]::NewLine | ConvertFrom-Json
} catch {
    throw "Codex returned an invalid plugin inventory: $($_.Exception.Message)"
}

$installedPluginIds = @{}
foreach ($plugin in @($inventory.installed)) {
    $installedPluginIds[$plugin.pluginId] = $true
}

foreach ($plugin in $manifest.plugins) {
    $pluginId = $plugin.id
    if ($installedPluginIds.ContainsKey($pluginId)) {
        Write-Output "SKIP plugin already installed: $pluginId"
        continue
    }

    $LASTEXITCODE = 0
    $installOutput = & $CodexCommand 'plugin' 'add' $pluginId '--json' 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to install plugin '$pluginId': $($installOutput -join [Environment]::NewLine)"
    }

    Write-Output "INSTALLED plugin: $pluginId"
}

Write-Output 'Restore complete. Restart Codex before using the restored skills.'

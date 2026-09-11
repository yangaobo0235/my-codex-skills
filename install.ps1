[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$SkipPlugins,
    [string]$CodexHomePath,
    [string]$CodexCommand = 'codex'
)

$ErrorActionPreference = 'Stop'

function Get-PluginMarketplaceName {
    param([string]$PluginId)

    $separator = $PluginId.LastIndexOf('@')
    if ($separator -le 0 -or $separator -eq ($PluginId.Length - 1)) {
        throw "Invalid plugin id in manifest: $PluginId"
    }

    return $PluginId.Substring($separator + 1)
}

function Invoke-CodexJson {
    param(
        [string[]]$Arguments,
        [string]$FailureMessage
    )

    $global:LASTEXITCODE = 0
    $output = & $CodexCommand @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }

    try {
        return $output -join [Environment]::NewLine | ConvertFrom-Json
    } catch {
        throw "$FailureMessage Codex returned invalid JSON."
    }
}

function Find-PrimaryRuntimeMarketplace {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_PRIMARY_RUNTIME_MARKETPLACE_PATH)) {
        if (Test-Path -LiteralPath $env:CODEX_PRIMARY_RUNTIME_MARKETPLACE_PATH) {
            return $env:CODEX_PRIMARY_RUNTIME_MARKETPLACE_PATH
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_MCP_NODE_PATH)) {
        $current = Split-Path $env:CODEX_MCP_NODE_PATH -Parent
        while (-not [string]::IsNullOrWhiteSpace($current)) {
            if ((Split-Path $current -Leaf) -eq 'dependencies') {
                $candidate = Join-Path (Split-Path $current -Parent) 'plugins\openai-primary-runtime'
                if (Test-Path -LiteralPath $candidate) {
                    return $candidate
                }
                break
            }
            $parent = Split-Path $current -Parent
            if ($parent -eq $current) {
                break
            }
            $current = $parent
        }
    }

    $fallback = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime'
    if (Test-Path -LiteralPath $fallback) {
        return $fallback
    }

    return $null
}

function Find-BundledMarketplace {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_BUNDLED_MARKETPLACE_PATH)) {
        if (Test-Path -LiteralPath $env:CODEX_BUNDLED_MARKETPLACE_PATH) {
            return $env:CODEX_BUNDLED_MARKETPLACE_PATH
        }
    }

    if ($IsWindows -or $env:OS -eq 'Windows_NT') {
        $getAppxPackage = Get-Command 'Get-AppxPackage' -ErrorAction SilentlyContinue
        if ($null -ne $getAppxPackage) {
            $package = Get-AppxPackage 'OpenAI.Codex' -ErrorAction SilentlyContinue
            if ($null -ne $package) {
                $candidate = Join-Path $package.InstallLocation 'app\resources\plugins\openai-bundled'
                if (Test-Path -LiteralPath $candidate) {
                    return $candidate
                }
            }
        }
    }

    return $null
}

function Copy-MarketplaceContent {
    param(
        [string]$Source,
        [string]$Destination
    )

    [IO.Directory]::CreateDirectory($Destination) | Out-Null
    $sourceRoot = $Source.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    foreach ($file in Get-ChildItem -LiteralPath $Source -Recurse -File -Force) {
        $relativePath = $file.FullName.Substring($sourceRoot.Length).TrimStart(
            [IO.Path]::DirectorySeparatorChar,
            [IO.Path]::AltDirectorySeparatorChar
        )
        $target = Join-Path $Destination $relativePath
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null

        $inputStream = [IO.File]::OpenRead($file.FullName)
        try {
            $outputStream = [IO.File]::Create($target)
            try {
                $inputStream.CopyTo($outputStream)
            } finally {
                $outputStream.Dispose()
            }
        } finally {
            $inputStream.Dispose()
        }
    }
}

function Add-LocalMarketplace {
    param(
        [string]$MarketplaceName,
        [hashtable]$RegisteredMarketplaces
    )

    if ($RegisteredMarketplaces.ContainsKey($MarketplaceName)) {
        Write-Output "SKIP marketplace already registered: $MarketplaceName"
        return
    }

    if ($MarketplaceName -eq 'openai-primary-runtime') {
        $source = Find-PrimaryRuntimeMarketplace
        if ([string]::IsNullOrWhiteSpace($source)) {
            throw "Marketplace '$MarketplaceName' was not found. Install and start the latest Codex desktop app, then retry."
        }
    } elseif ($MarketplaceName -eq 'openai-bundled') {
        $source = Find-BundledMarketplace
        if ([string]::IsNullOrWhiteSpace($source)) {
            throw "Marketplace '$MarketplaceName' was not found. Install and start the latest Codex desktop app, then retry."
        }

        # Windows Store package files carry protected attributes. Copy their contents
        # into Codex's expected user cache before registering the reserved marketplace.
        $cacheRoot = Join-Path $CodexHomePath '.tmp\bundled-marketplaces\openai-bundled'
        Copy-MarketplaceContent -Source $source -Destination $cacheRoot
        $source = $cacheRoot
    } else {
        throw "Marketplace '$MarketplaceName' is not registered. Add it to Codex, then retry."
    }

    $null = Invoke-CodexJson -Arguments @('plugin', 'marketplace', 'add', $source, '--json') `
        -FailureMessage "Unable to register marketplace '$MarketplaceName'."
    $RegisteredMarketplaces[$MarketplaceName] = $true
    Write-Output "REGISTERED marketplace: $MarketplaceName"
}

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

Write-Output 'Codex home: resolved for the current user.'
Write-Output "Personal skills: $(@($manifest.personalSkills).Count)"
Write-Output "Plugins: $(@($manifest.plugins).Count)"
Write-Output "Plugin marketplaces: $(@($manifest.plugins | ForEach-Object { Get-PluginMarketplaceName $_.id } | Sort-Object -Unique).Count)"

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
$marketplaceInventory = Invoke-CodexJson -Arguments @('plugin', 'marketplace', 'list', '--json') `
    -FailureMessage 'Unable to read the Codex marketplace inventory.'
$registeredMarketplaces = @{}
foreach ($marketplace in @($marketplaceInventory.marketplaces)) {
    $registeredMarketplaces[$marketplace.name] = $true
}

$requiredMarketplaces = @($manifest.plugins | ForEach-Object {
    Get-PluginMarketplaceName $_.id
} | Sort-Object -Unique)
foreach ($marketplaceName in $requiredMarketplaces) {
    Add-LocalMarketplace -MarketplaceName $marketplaceName -RegisteredMarketplaces $registeredMarketplaces
}

$inventory = Invoke-CodexJson -Arguments @('plugin', 'list', '--json') `
    -FailureMessage 'Unable to read the Codex plugin inventory.'

$installedPluginIds = @{}
foreach ($plugin in @($inventory.installed)) {
    $installedPluginIds[$plugin.pluginId] = $true
}

$pluginInstallErrors = @()
foreach ($plugin in $manifest.plugins) {
    $pluginId = $plugin.id
    if ($installedPluginIds.ContainsKey($pluginId)) {
        Write-Output "SKIP plugin already installed: $pluginId"
        continue
    }

    try {
        $null = Invoke-CodexJson -Arguments @('plugin', 'add', $pluginId, '--json') `
            -FailureMessage "Unable to install plugin '$pluginId'."
        $installedPluginIds[$pluginId] = $true
        Write-Output "INSTALLED plugin: $pluginId"
    } catch {
        $pluginInstallErrors += $_.Exception.Message
        Write-Warning $_.Exception.Message
    }
}

$verification = Invoke-CodexJson -Arguments @('plugin', 'list', '--json') `
    -FailureMessage 'Unable to verify the Codex plugin inventory.'
$verifiedPluginIds = @{}
foreach ($plugin in @($verification.installed)) {
    $verifiedPluginIds[$plugin.pluginId] = $true
}

$missingPlugins = @($manifest.plugins | Where-Object {
    -not $verifiedPluginIds.ContainsKey($_.id)
} | ForEach-Object { $_.id })
if ($missingPlugins.Count -gt 0) {
    $detail = if ($pluginInstallErrors.Count -gt 0) {
        " Installation errors: $($pluginInstallErrors -join ' ')"
    } else {
        ''
    }
    throw "Restore incomplete. Missing plugins: $($missingPlugins -join ', ').$detail"
}

Write-Output 'VERIFIED all manifest plugins are installed.'
Write-Output 'Restore complete. Restart Codex before using the restored skills and plugins.'

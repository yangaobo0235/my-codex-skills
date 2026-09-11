$ErrorActionPreference = 'Stop'

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw "Assertion failed: $Message"
    }
}

function Assert-Equal {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )

    if ($Expected -ne $Actual) {
        throw "Assertion failed: $Message. Expected '$Expected', got '$Actual'."
    }
}

$repoRoot = Split-Path $PSScriptRoot -Parent
$installer = Join-Path $repoRoot 'install.ps1'
$manifestPath = Join-Path $repoRoot 'skills-manifest.json'

Assert-True (Test-Path -LiteralPath $installer) 'install.ps1 must exist'
Assert-True (Test-Path -LiteralPath $manifestPath) 'skills-manifest.json must exist'

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$expectedSkills = @(
    'backend-interview-simulator',
    'kwai',
    'run-interview-note-defense',
    'write-engineering-resume',
    'write-interview-notes'
)

Assert-Equal 1 $manifest.schemaVersion 'manifest schema version'
Assert-Equal $expectedSkills.Count @($manifest.personalSkills).Count 'personal skill count'
foreach ($skillName in $expectedSkills) {
    Assert-True ($skillName -in $manifest.personalSkills) "manifest includes $skillName"
}
$expectedPluginIds = @(
    'computer-use@openai-bundled',
    'documents@openai-primary-runtime',
    'pdf@openai-primary-runtime',
    'presentations@openai-primary-runtime',
    'spreadsheets@openai-primary-runtime',
    'template-creator@openai-primary-runtime',
    'visualize@openai-bundled',
    'browser@openai-bundled',
    'chrome@openai-bundled',
    'codex-app-tools@openai-bundled',
    'unified-computer-use@openai-bundled'
)
Assert-Equal $expectedPluginIds.Count @($manifest.plugins).Count 'plugin count'
foreach ($pluginId in $expectedPluginIds) {
    Assert-True ($pluginId -in @($manifest.plugins.id)) "manifest includes $pluginId"
}

$trackedTextFiles = Get-ChildItem -LiteralPath $repoRoot -Recurse -File | Where-Object {
    $_.Extension -in @('.md', '.json', '.ps1', '.py', '.yaml', '.yml') -and
    $_.FullName -notmatch '[\\/]\.git[\\/]'
}
foreach ($file in $trackedTextFiles) {
    $content = Get-Content -Raw -LiteralPath $file.FullName
    Assert-True ($content -notmatch '[A-Za-z]:\\Users\\[^<]') "no user-specific absolute path in $($file.Name)"
}

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("codex-skill-install-test-" + [guid]::NewGuid().ToString('N'))
$checkHome = Join-Path $testRoot 'check-home'
$installHome = Join-Path $testRoot 'install-home'
$fakeCodex = Join-Path $testRoot 'fake-codex.ps1'
$pluginState = Join-Path $testRoot 'plugins.json'
$marketplaceState = Join-Path $testRoot 'marketplaces.json'
$commandLog = Join-Path $testRoot 'commands.log'
$bundledMarketplace = Join-Path $testRoot 'openai-bundled-source'
$primaryMarketplace = Join-Path $testRoot 'openai-primary-runtime'

New-Item -ItemType Directory -Path $testRoot | Out-Null

try {
    @'
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$RemainingArgs)

$statePath = $env:CODEX_SKILL_TEST_PLUGIN_STATE
$marketplaceStatePath = $env:CODEX_SKILL_TEST_MARKETPLACE_STATE
$logPath = $env:CODEX_SKILL_TEST_COMMAND_LOG
Add-Content -LiteralPath $logPath -Value ($RemainingArgs -join ' ')

$installed = if (Test-Path -LiteralPath $statePath) {
    @((Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json).ids)
} else {
    @()
}

$marketplaces = if (Test-Path -LiteralPath $marketplaceStatePath) {
    @((Get-Content -Raw -LiteralPath $marketplaceStatePath | ConvertFrom-Json).names)
} else {
    @()
}

if ($RemainingArgs[0] -eq 'plugin' -and $RemainingArgs[1] -eq 'marketplace' -and $RemainingArgs[2] -eq 'list') {
    @{ marketplaces = @($marketplaces | ForEach-Object { @{ name = $_ } }) } | ConvertTo-Json -Depth 4
    return
}

if ($RemainingArgs[0] -eq 'plugin' -and $RemainingArgs[1] -eq 'marketplace' -and $RemainingArgs[2] -eq 'add') {
    $source = $RemainingArgs[3]
    $manifest = Get-Content -Raw -LiteralPath (Join-Path $source '.agents\plugins\marketplace.json') | ConvertFrom-Json
    @{ names = @(@($marketplaces) + @($manifest.name) | Sort-Object -Unique) } |
        ConvertTo-Json | Set-Content -LiteralPath $marketplaceStatePath
    @{ name = $manifest.name; added = $true } | ConvertTo-Json
    return
}

if ($RemainingArgs[0] -eq 'plugin' -and $RemainingArgs[1] -eq 'list') {
    @{ installed = @($installed | ForEach-Object { @{ pluginId = $_ } }) } | ConvertTo-Json -Depth 4
    return
}

if ($RemainingArgs[0] -eq 'plugin' -and $RemainingArgs[1] -eq 'add') {
    $pluginId = $RemainingArgs[2]
    @{ ids = @(@($installed) + @($pluginId) | Sort-Object -Unique) } | ConvertTo-Json | Set-Content -LiteralPath $statePath
    @{ pluginId = $pluginId; installed = $true } | ConvertTo-Json
    return
}

throw "Unexpected fake Codex command: $($RemainingArgs -join ' ')"
'@ | Set-Content -LiteralPath $fakeCodex

    $env:CODEX_SKILL_TEST_PLUGIN_STATE = $pluginState
    $env:CODEX_SKILL_TEST_MARKETPLACE_STATE = $marketplaceState
    $env:CODEX_SKILL_TEST_COMMAND_LOG = $commandLog

    foreach ($marketplace in @(
        @{ Path = $bundledMarketplace; Name = 'openai-bundled' },
        @{ Path = $primaryMarketplace; Name = 'openai-primary-runtime' }
    )) {
        $manifestDirectory = Join-Path $marketplace.Path '.agents\plugins'
        New-Item -ItemType Directory -Path $manifestDirectory -Force | Out-Null
        @{ name = $marketplace.Name; plugins = @() } | ConvertTo-Json |
            Set-Content -LiteralPath (Join-Path $manifestDirectory 'marketplace.json')
    }

    $env:CODEX_BUNDLED_MARKETPLACE_PATH = $bundledMarketplace
    $env:CODEX_PRIMARY_RUNTIME_MARKETPLACE_PATH = $primaryMarketplace

    & $installer -Check -CodexHomePath $checkHome -CodexCommand $fakeCodex
    Assert-True (-not (Test-Path -LiteralPath $checkHome)) 'check mode must not create the Codex home'
    Assert-True (-not (Test-Path -LiteralPath $commandLog)) 'check mode must not invoke Codex'

    $existingSkill = Join-Path $installHome 'skills\kwai'
    New-Item -ItemType Directory -Path $existingSkill -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $existingSkill 'marker.txt') -Value 'preserve me'

    & $installer -CodexHomePath $installHome -CodexCommand $fakeCodex

    foreach ($skillName in $expectedSkills | Where-Object { $_ -ne 'kwai' }) {
        Assert-True (Test-Path -LiteralPath (Join-Path $installHome "skills\$skillName\SKILL.md")) "installs $skillName"
    }
    Assert-True (Test-Path -LiteralPath (Join-Path $existingSkill 'marker.txt')) 'existing skills are preserved'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $existingSkill 'SKILL.md'))) 'existing skills are not overwritten'

    $installedPlugins = @((Get-Content -Raw -LiteralPath $pluginState | ConvertFrom-Json).ids)
    Assert-Equal @($manifest.plugins).Count $installedPlugins.Count 'all manifest plugins are installed'

    $firstRunLog = @(Get-Content -LiteralPath $commandLog)
    Assert-Equal 2 @($firstRunLog | Where-Object { $_ -eq 'plugin list --json' }).Count 'plugin inventory is queried and verified'
    Assert-Equal 1 @($firstRunLog | Where-Object { $_ -eq 'plugin marketplace list --json' }).Count 'marketplace inventory is queried once'
    Assert-Equal 2 @($firstRunLog | Where-Object { $_ -like 'plugin marketplace add * --json' }).Count 'missing official marketplaces are registered'
    Assert-Equal @($manifest.plugins).Count @($firstRunLog | Where-Object { $_ -like 'plugin add * --json' }).Count 'missing plugins are added once'

    & $installer -CodexHomePath $installHome -CodexCommand $fakeCodex
    $secondRunLog = @(Get-Content -LiteralPath $commandLog)
    Assert-Equal @($manifest.plugins).Count @($secondRunLog | Where-Object { $_ -like 'plugin add * --json' }).Count 'second run does not add plugins again'
    Assert-Equal 2 @($secondRunLog | Where-Object { $_ -eq 'plugin marketplace list --json' }).Count 'marketplace inventory is queried on each run'
    Assert-Equal 2 @($secondRunLog | Where-Object { $_ -like 'plugin marketplace add * --json' }).Count 'registered marketplaces are not added again'

    Write-Output 'All installer tests passed.'
}
finally {
    Remove-Item Env:CODEX_SKILL_TEST_PLUGIN_STATE -ErrorAction SilentlyContinue
    Remove-Item Env:CODEX_SKILL_TEST_MARKETPLACE_STATE -ErrorAction SilentlyContinue
    Remove-Item Env:CODEX_SKILL_TEST_COMMAND_LOG -ErrorAction SilentlyContinue
    Remove-Item Env:CODEX_BUNDLED_MARKETPLACE_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:CODEX_PRIMARY_RUNTIME_MARKETPLACE_PATH -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}

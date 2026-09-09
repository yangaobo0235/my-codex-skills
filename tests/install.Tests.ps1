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

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("codex-skill-install-test-" + [guid]::NewGuid().ToString('N'))
$checkHome = Join-Path $testRoot 'check-home'
$installHome = Join-Path $testRoot 'install-home'
$fakeCodex = Join-Path $testRoot 'fake-codex.ps1'
$pluginState = Join-Path $testRoot 'plugins.json'
$commandLog = Join-Path $testRoot 'commands.log'

New-Item -ItemType Directory -Path $testRoot | Out-Null

try {
    @'
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$RemainingArgs)

$statePath = $env:CODEX_SKILL_TEST_PLUGIN_STATE
$logPath = $env:CODEX_SKILL_TEST_COMMAND_LOG
Add-Content -LiteralPath $logPath -Value ($RemainingArgs -join ' ')

$installed = if (Test-Path -LiteralPath $statePath) {
    @((Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json).ids)
} else {
    @()
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
    $env:CODEX_SKILL_TEST_COMMAND_LOG = $commandLog

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
    Assert-Equal 1 @($firstRunLog | Where-Object { $_ -eq 'plugin list --json' }).Count 'plugin inventory is queried once'
    Assert-Equal @($manifest.plugins).Count @($firstRunLog | Where-Object { $_ -like 'plugin add * --json' }).Count 'missing plugins are added once'

    & $installer -CodexHomePath $installHome -CodexCommand $fakeCodex
    $secondRunLog = @(Get-Content -LiteralPath $commandLog)
    Assert-Equal @($manifest.plugins).Count @($secondRunLog | Where-Object { $_ -like 'plugin add * --json' }).Count 'second run does not add plugins again'

    Write-Output 'All installer tests passed.'
}
finally {
    Remove-Item Env:CODEX_SKILL_TEST_PLUGIN_STATE -ErrorAction SilentlyContinue
    Remove-Item Env:CODEX_SKILL_TEST_COMMAND_LOG -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}

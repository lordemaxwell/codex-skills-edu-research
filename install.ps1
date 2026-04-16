[CmdletBinding()]
param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),
    [string]$PythonPath,
    [switch]$SetupLiteratureHarvest,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[codex-skills] $Message"
}

function Resolve-RepoRoot {
    return Split-Path -Parent $PSCommandPath
}

function Resolve-Python {
    param([string]$RequestedPath)

    $candidates = New-Object System.Collections.Generic.List[string]

    if ($RequestedPath) {
        $candidates.Add($RequestedPath)
    }

    foreach ($candidate in @(
        "D:\Python\Python311\python.exe",
        "C:\Python311\python.exe"
    )) {
        $candidates.Add($candidate)
    }

    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command -and $command.Source -and $command.Source -notmatch "WindowsApps") {
        $candidates.Add($command.Source)
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    return $null
}

function Install-Skill {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [switch]$Overwrite
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        throw "Source skill not found: $SourceDir"
    }

    if (Test-Path -LiteralPath $TargetDir) {
        if (-not $Overwrite) {
            Write-Step "Skip existing skill: $TargetDir"
            return
        }

        Write-Step "Removing existing skill: $TargetDir"
        Remove-Item -LiteralPath $TargetDir -Recurse -Force
    }

    Write-Step "Copying skill to $TargetDir"
    Copy-Item -LiteralPath $SourceDir -Destination $TargetDir -Recurse
}

function Ensure-LiteratureEnvTemplate {
    param([string]$SkillDir)

    $examplePath = Join-Path $SkillDir ".env.example"
    $envPath = Join-Path $SkillDir ".env"

    if ((Test-Path -LiteralPath $examplePath) -and -not (Test-Path -LiteralPath $envPath)) {
        Copy-Item -LiteralPath $examplePath -Destination $envPath
        Write-Step "Created .env from .env.example at $envPath"
    }
}

$repoRoot = Resolve-RepoRoot
$sourceSkillsRoot = Join-Path $repoRoot "skills"
$targetSkillsRoot = Join-Path $CodexHome "skills"

New-Item -ItemType Directory -Force -Path $targetSkillsRoot | Out-Null

$literatureSource = Join-Path $sourceSkillsRoot "literature-harvest"
$literatureTarget = Join-Path $targetSkillsRoot "literature-harvest"
$stataSource = Join-Path $sourceSkillsRoot "stata-research"
$stataTarget = Join-Path $targetSkillsRoot "stata-research"

Install-Skill -SourceDir $literatureSource -TargetDir $literatureTarget -Overwrite:$Force
Install-Skill -SourceDir $stataSource -TargetDir $stataTarget -Overwrite:$Force
Ensure-LiteratureEnvTemplate -SkillDir $literatureTarget

if ($SetupLiteratureHarvest) {
    $resolvedPython = Resolve-Python -RequestedPath $PythonPath
    if (-not $resolvedPython) {
        throw "No usable Python found. Pass -PythonPath explicitly."
    }

    $env:LIT_HARVEST_PYTHON = $resolvedPython
    $setupScript = Join-Path $literatureTarget "scripts\setup_environment.py"
    $runnerScript = Join-Path $literatureTarget "scripts\run.py"

    Write-Step "Initializing literature-harvest with Python: $resolvedPython"
    & $resolvedPython $setupScript
    if ($LASTEXITCODE -ne 0) {
        throw "literature-harvest setup_environment failed."
    }

    Write-Step "Running literature-harvest environment check"
    & $resolvedPython $runnerScript check_env --json
    if ($LASTEXITCODE -ne 0) {
        throw "literature-harvest check_env failed."
    }
}

Write-Step "Install complete. Restart Codex to load the updated skills."

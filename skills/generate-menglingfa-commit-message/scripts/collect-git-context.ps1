param(
    [Parameter(Mandatory = $true)]
    [string]$RepoPath,

    [string]$Author = "menglingfa",

    [ValidateRange(1, 100)]
    [int]$MaxCommits = 20,

    [switch]$NoPatch
)

$ErrorActionPreference = "Stop"

$resolvedRepo = (Resolve-Path -LiteralPath $RepoPath).Path

function Write-GitSection {
    param(
        [string]$Title,
        [string[]]$GitArgs
    )

    Write-Output "=== $Title ==="
    & git -C $resolvedRepo @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git command failed: git -C `"$resolvedRepo`" $($GitArgs -join ' ')"
    }
    Write-Output ""
}

& git -C $resolvedRepo rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Not a Git repository: $resolvedRepo"
}

Write-Output "=== REPOSITORY ==="
Write-Output $resolvedRepo
Write-Output ""

Write-GitSection -Title "STATUS" -GitArgs @("status", "--short")
Write-GitSection -Title "DIFF STAT" -GitArgs @("diff", "HEAD", "--stat")
Write-GitSection -Title "CHANGED FILES" -GitArgs @("diff", "HEAD", "--name-status")

if (-not $NoPatch) {
    Write-GitSection -Title "PATCH" -GitArgs @("diff", "HEAD")
}

$logFormat = "%h`t%s%n%b%n---"
Write-GitSection -Title "AUTHOR COMMITS" -GitArgs @(
    "log",
    "--author=$Author",
    "--no-merges",
    "--max-count=$MaxCommits",
    "--pretty=format:$logFormat"
)

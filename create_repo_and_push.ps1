
param(
  [string]$RepoName = "Capstone",
  [string]$GithubUser = "eskgyimah",
  [string]$UserName = "Edd",
  [string]$UserEmail = "edward.gyimah002@stu.ucc.edu.gh",
  [ValidateSet("public","private")][string]$Visibility = "public",
  [string]$LocalPath = "",
  [switch]$UseCLI,        # force GitHub CLI path
  [switch]$UseREST        # force REST API path (requires PAT)
)

function Have-Cmd($name) {
  try { Get-Command $name -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

if (-not $LocalPath) {
  $LocalPath = Join-Path (Get-Location) $RepoName
}
if (-not (Test-Path $LocalPath)) {
  New-Item -ItemType Directory -Path $LocalPath | Out-Null
}

Write-Host "Repo Name   : $RepoName"
Write-Host "GitHub User : $GithubUser"
Write-Host "Local Path  : $LocalPath"
Write-Host "Visibility  : $Visibility"

Set-Location $LocalPath

# Ensure git is installed
if (-not (Have-Cmd git)) {
  Write-Error "git is not installed or not in PATH. Install Git for Windows first."
  exit 1
}

# Initialize repo and first commit
git init | Out-Null
# default to main
git branch -M main
git add .
git -c user.name="$UserName" -c user.email="$UserEmail" commit -m "Initial commit: Capstone app + Docker + GH Actions" | Out-Null

$remoteUrl = "https://github.com/$GithubUser/$RepoName.git"

# Helper to push to origin
function Push-Origin {
  if (-not (git remote | Select-String -SimpleMatch "origin")) {
    git remote add origin $remoteUrl
  }
  git push -u origin main
}

$didCreate = $false

# Path A: GitHub CLI
$canCLI = (Have-Cmd gh)
if (($UseCLI -or $canCLI) -and -not $UseREST) {
  if (-not $canCLI) {
    Write-Error "GitHub CLI (gh) not found. Install with: winget install --id GitHub.cli -e"
    exit 1
  }
  # Ensure auth
  try {
    gh auth status | Out-Null
  } catch {
    Write-Host "Logging into GitHub CLI..."
    gh auth login
  }

  $visFlag = if ($Visibility -eq "private") { "--private" } else { "--public" }
  Write-Host "Creating repo via GitHub CLI..."
  gh repo create "$GithubUser/$RepoName" $visFlag --source . --remote origin --push
  if ($LASTEXITCODE -eq 0) {
    $didCreate = $true
  } else {
    Write-Warning "gh repo create did not succeed; will attempt REST fallback if enabled."
  }
}

# Path B: REST API (requires PAT with 'repo' scope)
if ((-not $didCreate) -and $UseREST) {
  if (-not (Have-Cmd "curl")) {
    Write-Error "curl not found. Install curl or use the GitHub CLI path."
    exit 1
  }
  $secure = Read-Host "Enter GitHub Personal Access Token (repo scope)" -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  $pat  = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)

  $isPrivate = if ($Visibility -eq "private") { "true" } else { "false" }
  $payload = "{`"name`":`"$RepoName`", `"private`":$isPrivate}"
  Write-Host "Creating repo via REST API..."
  $resp = curl -s -X POST -H "Authorization: token $pat" -H "Accept: application/vnd.github+json" `
               https://api.github.com/user/repos -d $payload
  if ($LASTEXITCODE -ne 0) {
    Write-Error "REST create failed. Response: $resp"
    exit 1
  }
  # add remote + push
  Push-Origin
  $didCreate = $true
}

if (-not $didCreate -and -not $UseREST -and -not $UseCLI) {
  Write-Warning "No creation path selected. Try one of these:"
  Write-Host "  1) GitHub CLI path (recommended):"
  Write-Host "     winget install --id GitHub.cli -e"
  Write-Host "     gh auth login"
  Write-Host "     .\create_repo_and_push.ps1 -UseCLI -RepoName '$RepoName' -GithubUser '$GithubUser' -LocalPath '$LocalPath'"
  Write-Host ""
  Write-Host "  2) REST API path (needs PAT with 'repo' scope):"
  Write-Host "     .\create_repo_and_push.ps1 -UseREST -RepoName '$RepoName' -GithubUser '$GithubUser' -LocalPath '$LocalPath'"
  exit 2
}

Write-Host "Done. Repo available at: $remoteUrl"

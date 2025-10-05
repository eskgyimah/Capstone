
param(
  [string]$GithubUser = "eskgyimah",
  [string]$RepoName = "Capstone",
  [string]$UserEmail = "edward.gyimah002@stu.ucc.edu.gh"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Join-Path $root $RepoName
if (-not (Test-Path $repo)) { New-Item -ItemType Directory -Path $repo | Out-Null }

Copy-Item -Path (Join-Path $root "Capstone.py") -Destination $repo -Force
Copy-Item -Path (Join-Path $root "requirements.txt") -Destination $repo -Force
Copy-Item -Path (Join-Path $root "Dockerfile") -Destination $repo -Force
Copy-Item -Path (Join-Path $root ".dockerignore") -Destination $repo -Force
Copy-Item -Path (Join-Path $root ".gitignore") -Destination $repo -Force
Copy-Item -Path (Join-Path $root ".streamlit") -Destination $repo -Recurse -Force
Copy-Item -Path (Join-Path $root ".github") -Destination $repo -Recurse -Force
Copy-Item -Path (Join-Path $root "README.md") -Destination $repo -Force

Push-Location $repo
git init
git branch -m main
git add .
git -c user.name="Edd" -c user.email=$UserEmail commit -m "Initial commit: Capstone app + Docker + GH Actions"
git remote add origin ("https://github.com/{0}/{1}.git" -f $GithubUser, $RepoName)
git push -u origin main
Pop-Location

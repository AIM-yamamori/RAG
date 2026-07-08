# 1. 仮想環境（.venv）がなければ作成
if (-not (Test-Path ".venv")) {
    Write-Host "仮想環境を作成しています..." -ForegroundColor Cyan
    python -m venv .venv
} else {
    Write-Host "仮想環境は既に存在します。" -ForegroundColor Green
}

# 2. 仮想環境を有効化
.\.venv\Scripts\Activate.ps1

# 3. requirements.txt があればパッケージをインストール
if (Test-Path "requirements.txt") {
    Write-Host "依存パッケージをインストールしています..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt が見つからないため、インストールをスキップします。" -ForegroundColor Yellow
}
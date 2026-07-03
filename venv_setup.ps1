# 仮想環境作成
python -m venv .venv

# 仮想環境を有効化
.\.venv\Scripts\Activate.ps1

# requirements.txt があればインストール
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt が見つかりません"
}

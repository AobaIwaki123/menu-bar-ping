# PingBar

macOSのメニューバーにリアルタイムでping（レイテンシ）を表示するシンプルなアプリ。

## 開発環境のセットアップ

```bash
conda create -n menu-ping python=3.13
conda activate menu-ping
pip install -r requirements.txt
```

## 開発中の実行

```bash
python pingbar.py
```

## .app としてビルド

ビルドすると以下のメリットがあります：
- スタンドアロンアプリとして動作（Python環境不要）
- Finderからダブルクリックで起動可能
- ログイン時の自動起動設定が可能
- Dockに表示されず、メニューバーのみに常駐

```bash
python setup.py py2app
# dist/PingBar.app が生成される
cp -r dist/PingBar.app /Applications/
```

ビルド後は `/Applications/PingBar.app` をダブルクリックで起動できます。

## カスタマイズ

`pingbar.py` の先頭2行で変更可能：

```python
PING_HOST = "8.8.8.8"   # pingの送信先
PING_INTERVAL = 2.0      # 更新間隔（秒）
```
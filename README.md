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

### ビルド手順

```bash
# 1. 古いビルドをクリーンアップ（推奨）
rm -rf build dist

# 2. .appをビルド
python setup.py py2app

# 3. コード署名
codesign --force --deep --sign - dist/PingBar.app

# 4. Applicationsフォルダにコピー
cp -r dist/PingBar.app /Applications/
```

ビルド後は `/Applications/PingBar.app` をダブルクリックで起動できます。

### トラブルシューティング

もし "Launch error" が発生した場合：

```bash
# エラーログを確認
/Applications/PingBar.app/Contents/MacOS/PingBar

# libffi.8.dylibエラーの場合（setup.pyで自動対応済み）
# 手動で追加する場合：
cp $(python -c "import sys; print(sys.prefix)")/lib/libffi.8.dylib \
   /Applications/PingBar.app/Contents/Frameworks/
codesign --force --deep --sign - /Applications/PingBar.app
```

## カスタマイズ

`pingbar.py` の先頭2行で変更可能：

```python
PING_HOST = "8.8.8.8"   # pingの送信先
PING_INTERVAL = 2.0      # 更新間隔（秒）
```
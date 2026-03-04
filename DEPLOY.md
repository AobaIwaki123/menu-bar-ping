# デプロイ手順

このドキュメントでは、PingBarをHomebrew Caskでインストール可能にするための手順を説明します。

## 前提条件

- GitHubアカウント
- GitHubでこのプロジェクトのリポジトリが作成済み
- `gh` CLI（GitHub CLI）がインストール済み

## 1. リリースの準備

### 1.1 バージョン番号の更新

`setup.py` のバージョン番号を更新：

```python
"CFBundleShortVersionString": "1.0.0",  # 適切なバージョンに変更
```

### 1.2 アプリケーションのビルド

```bash
# クリーンビルド
rm -rf build dist
python setup.py py2app
```

### 1.3 動作確認

```bash
open dist/PingBar.app
```

メニューバーでアプリが正常に動作することを確認してください。

## 2. GitHubリリースの作成

### 2.1 アプリケーションのアーカイブ

```bash
cd dist
zip -r PingBar.zip PingBar.app
cd ..
```

### 2.2 リリースの作成とアップロード

```bash
# バージョンタグを作成してリリース
VERSION="v1.0.0"  # 適切なバージョンに変更
git tag -a $VERSION -m "Release $VERSION"
git push origin $VERSION

# GitHubリリースを作成
gh release create $VERSION \
  dist/PingBar.zip \
  --title "PingBar $VERSION" \
  --notes "Release notes here"
```

### 2.3 SHA256ハッシュの取得

```bash
shasum -a 256 dist/PingBar.zip
```

このハッシュ値は後で使用するため、メモしておきます。

## 3. Homebrew Tap の作成

### 3.1 Tapリポジトリの作成

GitHubで新しいリポジトリを作成します：
- リポジトリ名: `homebrew-tap`（必ず `homebrew-` で始める）
- 公開設定: Public

```bash
# ローカルにクローン
git clone https://github.com/YOUR_USERNAME/homebrew-tap.git
cd homebrew-tap
mkdir Casks
```

### 3.2 Cask Formulaの作成

`Casks/pingbar.rb` を作成：

```ruby
cask "pingbar" do
  version "1.0.0"
  sha256 "ここにSHA256ハッシュを貼り付け"

  url "https://github.com/YOUR_USERNAME/menu-bar-ping/releases/download/v#{version}/PingBar.zip"
  name "PingBar"
  desc "Real-time ping display in macOS menu bar"
  homepage "https://github.com/YOUR_USERNAME/menu-bar-ping"

  app "PingBar.app"

  zap trash: [
    "~/Library/Preferences/com.yourname.PingBar.plist",
  ]
end
```

**注意**: 
- `YOUR_USERNAME` を自分のGitHubユーザー名に置き換えてください
- `sha256` に手順2.3で取得したハッシュ値を設定してください
- `version` をリリースバージョンに合わせてください

### 3.3 Tapリポジトリにプッシュ

```bash
git add Casks/pingbar.rb
git commit -m "Add PingBar cask"
git push origin main
```

## 4. インストール方法

### 4.1 Tapの追加とインストール

```bash
# Tapを追加
brew tap YOUR_USERNAME/tap

# PingBarをインストール
brew install --cask pingbar
```

### 4.2 アップデート方法

新しいバージョンをリリースする場合：

1. 手順1〜2を繰り返して新しいバージョンをリリース
2. `Casks/pingbar.rb` の `version` と `sha256` を更新
3. Tapリポジトリにプッシュ

ユーザーは以下のコマンドで更新できます：

```bash
brew upgrade --cask pingbar
```

## 5. 公式Homebrew Caskへの登録（オプション）

より多くのユーザーに届けたい場合は、公式の `homebrew-cask` リポジトリへプルリクエストを送ることができます：

```bash
# Homebrew Caskリポジトリをフォーク後
brew install --cask pingbar  # まず自分のTapでテスト
cd $(brew --repository homebrew/cask)
git checkout -b pingbar
cp /path/to/your/tap/Casks/pingbar.rb Casks/
git add Casks/pingbar.rb
git commit -m "Add PingBar"
git push YOUR_FORK pingbar
# GitHubでPRを作成
```

詳細は[Homebrew Cask Contributing Guide](https://github.com/Homebrew/homebrew-cask/blob/master/CONTRIBUTING.md)を参照してください。

## トラブルシューティング

### インストール後にアプリが起動しない

```bash
# アプリのコード署名を確認
codesign -dv --verbose=4 /Applications/PingBar.app

# Gatekeeperの制限を解除（開発中のみ）
xattr -cr /Applications/PingBar.app
```

### SHA256ハッシュのミスマッチ

リリースファイルを再度ダウンロードしてハッシュを再計算：

```bash
curl -L -o PingBar.zip https://github.com/YOUR_USERNAME/menu-bar-ping/releases/download/vX.X.X/PingBar.zip
shasum -a 256 PingBar.zip
```

## 参考資料

- [Homebrew Cask Documentation](https://docs.brew.sh/Cask-Cookbook)
- [Creating a Homebrew Tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)

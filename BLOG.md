# 【macOS】Pythonでたった50行！メニューバーにpingを表示するアプリを作ってみました

## はじめに

Wi-Fiやテザリング、カフェのフリーWi-Fiなど、作業環境を切り替えながら開発していると「いまの回線は快適か？」が体感だけでは判断しづらいことがあります。ブラウジングは普通でも、VS Codeのリモート開発だけ突然カクつく……といったケースもあります。

そこで本記事では、**macOSのメニューバーにping（レイテンシ）を常時表示する**小さな常駐アプリ「PingBar」を、Python + rumpsで作ります。2秒ごとに `ping: 12ms` のように更新されるので、「いまはレスポンスが良いから集中して作業する」「遅いからローカル作業に切り替える」といった判断材料になります。

実装はシンプルで、pingの計測と表示を合わせても**47行程度**。必要なコードとポイントを順に解説します。

（背景）筆者は引っ越し直後に固定回線の開通を待つことになり、複数のネットワークを行き来する中でこのツールが欲しくなりました。

> **注意**: この記事はmacOS専用の内容になります。今回使用するrumpsライブラリはmacOSのメニューバー（ステータスバー）専用なので、WindowsやLinuxでは動作しません。ご注意くださいね。

## 完成イメージ

（※ここにメニューバーでping値が表示されているスクリーンショットを挿入）  
メニューバーにリアルタイムでping値が「ping: 12ms」のように表示され、2秒ごとに自動更新されます。メニューをクリックすると接続先ホストも確認できます。

## メニューバーアプリ専用ライブラリ「rumps」

「メニューバーアプリ」と聞くと、Objective-CやSwiftでガッツリ書くものだと思っていました。でも調べてみると、**rumps**（Ridiculously Uncomplicated macOS Python Statusbar apps）という素晴らしいライブラリがあったんです。

最小構成はこれだけです：

```python
import rumps

class MyApp(rumps.App):
    @rumps.timer(2)
    def update(self, _):
        self.title = "Hello!"

if __name__ == "__main__":
    MyApp().run()
```

これで2秒ごとに「Hello!」と表示されるメニューバーアプリが動いてしまいます。デコレータだけで定期実行ができる設計がとても美しいですね。

## まずはpingを打つ処理（10行）

まずはping処理を実装してみましょう。macOSの`/sbin/ping`コマンドを実行し、その出力から応答時間を正規表現でサクッと抽出します。

```python
import re
import subprocess

def measure_ping(host: str) -> float | None:
    """Return round-trip time in ms, or None on failure."""
    try:
        result = subprocess.run(
            ["/sbin/ping", "-c", "1", "-W", "1000", host],
            capture_output=True,
            text=True,
            timeout=3,
        )
        match = re.search(r"time=(\d+(?:\.\d+)?)", result.stdout)
        return float(match.group(1)) if match else None
    except (subprocess.TimeoutExpired, OSError):
        return None
```

ポイント：
- `-c 1`: 1回だけpingを送信します
- `-W 1000`: タイムアウトは1秒（ミリ秒単位）に設定
- `timeout=3`: subprocess自体のタイムアウトです
- 失敗時は`None`を返すシンプルな設計
- エラーハンドリング込みで約10行に収まりました

pingコマンドの出力例：
```
64 bytes from 8.8.8.8: icmp_seq=0 ttl=118 time=12.345 ms
```

ここから`time=12.345`の部分を抽出しています。

## メニューバーへの表示（これで完成！）

ping処理とrumpsを組み合わせてみましょう。完成したコード全体はこちらです：

```python
import re
import subprocess
import rumps

PING_HOST = "8.8.8.8"
PING_INTERVAL = 2.0  # seconds


def measure_ping(host: str) -> float | None:
    """Return round-trip time in ms, or None on failure."""
    try:
        result = subprocess.run(
            ["/sbin/ping", "-c", "1", "-W", "1000", host],
            capture_output=True,
            text=True,
            timeout=3,
        )
        match = re.search(r"time=(\d+(?:\.\d+)?)", result.stdout)
        return float(match.group(1)) if match else None
    except (subprocess.TimeoutExpired, OSError):
        return None


def format_title(ms: float | None) -> str:
    if ms is None:
        return "ping: --"
    return f"ping: {ms:.0f}ms"


class PingBarApp(rumps.App):
    def __init__(self):
        super().__init__(name="PingBar", title="ping: …", quit_button="Quit")
        self.menu = [
            rumps.MenuItem("Host: " + PING_HOST),
            None,  # separator
        ]

    @rumps.timer(PING_INTERVAL)
    def update(self, _):
        ms = measure_ping(PING_HOST)
        self.title = format_title(ms)


if __name__ == "__main__":
    PingBarApp().run()
```

**全部で47行**。たったこれだけで実用的なアプリが完成しちゃいます。

### コードのポイント

1. **定数で設定を明示**
   ```python
   PING_HOST = "8.8.8.8"      # どこにpingするか
   PING_INTERVAL = 2.0         # 何秒ごとに更新するか
   ```
   変更したければ、この2行を編集するだけです。

2. **接続先をメニューに表示**
   ```python
   self.menu = [
       rumps.MenuItem("Host: " + PING_HOST),
       None,  # separator
   ]
   ```
   「今どこに接続しているか」を常に明示して、透明性を担保しています。

3. **タイマーで自動更新**
   ```python
   @rumps.timer(PING_INTERVAL)
   def update(self, _):
       ms = measure_ping(PING_HOST)
       self.title = format_title(ms)
   ```
   デコレータ1行で定期実行できます。rumpsの設計、本当に素晴らしいですよね。

## 実行方法

### 開発中

```bash
# 依存関係をインストール
pip install rumps

# 実行
python pingbar.py
```

メニューバーにアイコンが表示され、2秒ごとにping値が更新されますよ！

### スタンドアロンアプリ化（py2app）

開発中の実行でも十分使えるのですが、以下の理由からスタンドアロンアプリ化してみたくなりました：

- Python環境なしでサクッと起動したい
- Macのログイン時に自動起動させたい
- Dockには表示せず、メニューバーのみにひっそりと常駐させたい

py2appを使えば、おなじみの`.app`形式にビルドできちゃいます。

#### setup.pyの作成

```python
from setuptools import setup

APP = ['pingbar.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'LSUIElement': True,  # Dockに表示しない
    },
    'packages': ['rumps', 'objc', 'Foundation', 'AppKit'],
    'includes': ['subprocess', 're'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

#### ビルド手順

```bash
# py2appのインストール
pip install py2app

# ビルド
python setup.py py2app

# コード署名（必須）
codesign --force --deep --sign - dist/PingBar.app

# Applicationsフォルダにコピー
cp -r dist/PingBar.app /Applications/
```

これで`/Applications/PingBar.app`をダブルクリックするだけで起動できるようになります！

### ちょっとつまずいたポイント: libffiエラー

初回ビルド時、起動してみると以下のエラーが発生してしまいました：

```
Library not loaded: @rpath/libffi.8.dylib
```

これはpy2appがlibffiを自動的にバンドルしてくれないという問題でした。setup.pyに以下を追加して解決しています：

```python
import sys
from pathlib import Path

# libffiのパスを取得
libffi_path = Path(sys.prefix) / "lib" / "libffi.8.dylib"

DATA_FILES = []
if libffi_path.exists():
    DATA_FILES = [
        ('Frameworks', [str(libffi_path)])
    ]
```

再ビルド後、無事に動作するようになりました！

## カスタマイズ例

### 接続先を変更

```python
PING_HOST = "1.1.1.1"           # Cloudflare DNS
PING_HOST = "192.168.1.1"       # 自宅ルーター
PING_HOST = "example.com"       # ドメイン名も可
```

IPアドレスだけでなく、ホスト名での指定も可能です。

### 更新間隔を調整

```python
PING_INTERVAL = 1.0   # 1秒ごと（頻繁）
PING_INTERVAL = 5.0   # 5秒ごと（省エネ）
```

### ログイン時に自動起動

macOSのシステム設定から簡単に設定できます：

1. **システム設定** → **一般** → **ログイン項目**を開く
2. **+**ボタンをクリック
3. `/Applications/PingBar.app`を追加するだけ！

## よくある質問

### Q1. Mac以外でも動きますか？

A. **残念ながら動きません。** rumpsはmacOS専用のライブラリなんです。Windowsならシステムトレイ用の`pystray`、Linuxなら`gtk`や`qt`ベースのライブラリを使う必要があります。ping処理の部分（`measure_ping`関数）は他OSでも動作しますが、メニューバーの表示部分は全面的に書き換える必要があります。

### Q2. 指定できるのはIPアドレスだけですか？

A. **ホスト名でも大丈夫です！** `PING_HOST = "google.com"`のようにドメイン名も使えます。内部で`/sbin/ping`コマンドを実行しているので、DNSで解決できるホスト名ならなんでもOKです。

### Q3. 環境変数でホストを指定できますか？

A. **現状は対応していません。** コード内の定数を直接変更していただく形になります。環境変数で指定できるようにすることも可能なんですが、スタンドアロンアプリは通常の環境変数を引き継がないため、設定ファイルを読み込む仕組みが別途必要になります。「50行で完結する」という良さを保つために、今はシンプルな定数方式を採用しています。

### Q4. Homebrewでインストールできますか？

A. **今のところ未対応です。** ビルド手順がとても簡単なので、リポジトリをcloneしてご自身でビルドする方式で十分かなと思っています。もしリクエストが多ければ、Homebrew Caskへの登録も考えてみますね。

## 使ってみての感想

実際に使い始めて数週間経ちますが、想像以上に便利でした！

- **回線の調子がひと目でわかる！**  
  「今日はテザリングの調子が悪いから、ブラウジングは後回しにしてローカル作業しよう」といった見切りがつけやすくなりました。

- **イライラが減る**: VS Codeのリモート開発で文字入力が遅れたとき、「あ、今pingが100ms超えてるから仕方ないな」と納得できるようになり、精神衛生上とても良いです。

- **Macへの負担はほぼゼロ**  
  2秒に1回のping程度なら、CPUやメモリへの影響は誤差レベルです。

- **コードが短いという圧倒的な安心感**  
  たった47行なので、裏で何をしているかが完全に把握できます。変な動きをしていないという安心感は大きいです。

## まとめ

Pythonとrumpsを使えば、macOSのメニューバーアプリがびっくりするくらい簡単に作れちゃいます。今回のpingモニターは：

- コード**47行**で実用レベル
- 開発時間はたったの**2〜3時間**
- Pythonの標準的な知識だけでOK
- スタンドアロンアプリ化もサクッとできる

「こんなちょっとしたツールがほしいな」と思ったとき、自分で作ってみるのも楽しいですよ。コードが短ければ、それ自体が安心にもつながります。

rumpsの公式ドキュメントを見ると、メニュー項目の追加やアイコンの変更など、もっといろいろなカスタマイズができることがわかります。シンプルなツールを自作する楽しさを、ぜひ皆さんも味わってみてくださいね！

## リポジトリ

https://github.com/AobaIwaki123/menu-bar-ping

---

**関連リンク**
- [rumps公式ドキュメント](https://rumps.readthedocs.io/)
- [py2app公式ドキュメント](https://py2app.readthedocs.io/)

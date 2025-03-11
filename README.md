# Obsidian PDF Processor

Obsidian PDF Processorは、PDFの書籍管理をObsidianで簡単に行うためのツールです。PDFファイルの表紙画像を自動的に抽出し、シンボリックリンクを作成して、Obsidianでの表示に最適化されたマークダウン形式の一覧を生成します。

https://github.com/user-attachments/assets/96c5915a-21b6-4417-b992-c2430708a2f3

## 機能

- PDFファイルの表紙画像を自動抽出
- シンボリックリンクの自動作成
- 表形式または単純なリスト形式でのマークダウン生成
- 設定の保存と読み込み
- カスタマイズ可能なサブディレクトリ構造

## インストール方法

### 依存パッケージのインストール

```bash
pip install pillow pdf2image pymupdf PyPDF2
```

macOSの場合、追加で以下のコマンドを実行してpoppler（PDF処理に必要）をインストールします：

```bash
brew install poppler
```

### アプリケーションの実行

```bash
python main.py
```

## 使い方

1. **入力設定**
   - 「ファイル選択」ボタンで個別のPDFファイルを選択
   - 「ディレクトリ選択」ボタンでフォルダ内のすべてのPDFファイルを選択

2. **出力設定**
   - 「画像保存先」には表紙画像を保存するディレクトリを指定 (使用しているObsidianプロジェクト内の保存したいディレクトリをセットしてください)
   - 「リンク作成先」にはシンボリックリンクを作成するディレクトリを指定 (使用しているObsidianプロジェクト内の保存したいディレクトリをセットしてください)
   - 「サブディレクトリ名」には画像とPDFの両方で使用するサブディレクトリ名を指定

3. **オプション**
   - 「表形式にしない」にチェックを入れると、単純なリスト形式でマークダウンを生成
   - 「タイトルを表示する」にチェックを入れると、画像の下にPDFのタイトルを表示

4. **処理の実行**
   - 「画像抽出のみ実行」ボタンで表紙画像のみを抽出
   - 「シンボリックリンク作成のみ実行」ボタンでシンボリックリンクのみを作成
   - 「すべて実行」ボタンで画像抽出、シンボリックリンク作成、マークダウン生成を一括実行

5. **マークダウンの利用**
   - 処理が完了すると、マークダウンテキストが自動的にクリップボードにコピーされます
   - Obsidianに貼り付けることで、書籍の一覧ページを作成できます

## 生成されるマークダウンの例

### 表形式の場合
4列並びの表で出力されます。

```markdown
| | | | |
|---|---|---|---|
| [![](JS+α/Gatsby5(前編).png)](JS+α/Gatsby5(前編).pdf) | [![](JS+α/Gatsby5(後編).png)](JS+α/Gatsby5(後編).pdf) | [![](JS+α/SEはまずJSを正しく読めるようになろう.png)](JS+α/SEはまずJSを正しく読めるようになろう.pdf) | [![](JS+α/[Gatsby]サイト.png)](JS+α/[Gatsby]サイト.pdf) |
```

### リスト形式の場合

```markdown
[![](JS+α/Gatsby5(前編).png)](JS+α/Gatsby5(前編).pdf)
[![](JS+α/Gatsby5(後編).png)](JS+α/Gatsby5(後編).pdf)
[![](JS+α/SEはまずJSを正しく読めるようになろう.png)](JS+α/SEはまずJSを正しく読めるようになろう.pdf)
```

## 仕組み

1. **PDFの表紙抽出**：PyMuPDFライブラリを使用して、PDFの1ページ目を高品質な画像として抽出します。ビューワーでの表示に忠実なレンダリングを行うため、背表紙や裏表紙が不要に表示される問題を回避します。

2. **シンボリックリンク作成**：指定されたディレクトリにPDFファイルへのシンボリックリンクを作成します。ファイル名の空白や全角スペースはアンダースコアに変換されるため、Obsidianでのリンク問題を回避できます。

3. **マークダウン生成**：表紙画像とPDFへのリンクを含むマークダウン形式のテキストを生成します。表形式（4列）または単純なリスト形式から選択できます。

## ファイル構成

```
obsidian_pdf_processor/
├── main.py                    # メインの実行ファイル
├── pdf_processor_settings.json # 設定ファイル
└── src/                       # ソースコードディレクトリ
    ├── __init__.py            # パッケージ初期化ファイル
    ├── app_settings.py        # 設定管理クラス
    ├── logger.py              # ログ管理クラス
    ├── main_application.py    # メインアプリケーションクラス
    ├── markdown_generator.py  # マークダウン生成クラス
    ├── pdf_processor.py       # PDF処理クラス
    └── symbolic_link_creator.py # シンボリックリンク作成クラス
```

## 注意事項

- シンボリックリンクの作成には、ファイルシステムの権限が必要です。
- 特殊な文字を含むファイル名では問題が発生する可能性があるため、シンプルなファイル名を使用することをお勧めします。

## トラブルシューティング

- **画像が抽出できない場合**：popperが正しくインストールされているか確認してください。
- **シンボリックリンクが作成できない場合**：権限を確認し、必要に応じて管理者権限で実行してください。
- **マークダウンのリンクが機能しない場合**：ファイルパスに特殊文字が含まれていないか確認してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

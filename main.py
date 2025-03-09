import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import pdf2image
from PIL import Image, ImageTk
import shutil
import threading
from pathlib import Path


class PDFProcessor:
    """PDFの処理を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def extract_cover_image(self, pdf_path, output_dir, dpi=150):
        """PDFの表紙（1ページ目）を画像として抽出する"""
        try:
            # ファイル名（拡張子なし）を取得
            pdf_filename = os.path.basename(pdf_path)
            pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
            
            # 出力ファイルパスを作成
            output_path = os.path.join(output_dir, f"{pdf_name_without_ext}.png")
            
            # すでに画像が存在する場合はスキップ
            if os.path.exists(output_path):
                if self.logger:
                    self.logger.log(f"画像すでに存在します: {output_path}")
                return output_path
            
            # PDFの1ページ目を画像に変換
            images = pdf2image.convert_from_path(
                pdf_path, 
                dpi=dpi, 
                first_page=1, 
                last_page=1
            )
            
            # 画像を保存
            if images:
                images[0].save(output_path, "PNG")
                if self.logger:
                    self.logger.log(f"表紙画像を保存しました: {output_path}")
                return output_path
            else:
                if self.logger:
                    self.logger.log(f"エラー: PDFから画像を抽出できませんでした: {pdf_path}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.log(f"エラー: {str(e)}")
            return None


class SymbolicLinkCreator:
    """シンボリックリンクの作成を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.created_links = []
    
    def create_symlink(self, source_path, output_dir):
        """シンボリックリンクを作成する"""
        try:
            # ファイル名を取得
            filename = os.path.basename(source_path)
            
            # 出力ファイルパスを作成
            output_path = os.path.join(output_dir, filename)
            
            # すでに存在する場合は削除
            if os.path.exists(output_path):
                if os.path.islink(output_path):
                    os.unlink(output_path)
                    if self.logger:
                        self.logger.log(f"既存のシンボリックリンクを削除しました: {output_path}")
                else:
                    if self.logger:
                        self.logger.log(f"警告: 同名のファイルが存在します: {output_path}")
                    return None
            
            # シンボリックリンクを作成
            os.symlink(source_path, output_path)
            self.created_links.append(output_path)
            
            if self.logger:
                self.logger.log(f"シンボリックリンクを作成しました: {output_path} -> {source_path}")
            
            return output_path
        except Exception as e:
            if self.logger:
                self.logger.log(f"エラー: シンボリックリンクの作成に失敗しました: {str(e)}")
            return None
    
    def get_created_links(self):
        """作成されたシンボリックリンクのリストを返す"""
        return self.created_links
    
    def clear_created_links(self):
        """作成されたシンボリックリンクのリストをクリアする"""
        self.created_links = []


class MarkdownGenerator:
    """マークダウン文字列の生成を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def generate_markdown(self, pdf_files, image_dir, symlink_dir, use_table=True, show_title=False):
        """マークダウン文字列を生成する"""
        try:
            if not pdf_files:
                if self.logger:
                    self.logger.log("警告: 処理するPDFファイルがありません")
                return ""
            
            # PDFファイルを名前でソート
            pdf_files.sort(key=lambda x: os.path.basename(x).lower())
            
            markdown_lines = []
            
            if use_table:
                # PDFファイルの数を4の倍数になるように調整
                while len(pdf_files) % 4 != 0:
                    pdf_files.append(None)
                
                # 4列ずつ処理
                for i in range(0, len(pdf_files), 4):
                    chunk = pdf_files[i:i+4]
                    
                    # テーブルの行を作成
                    if i == 0:
                        markdown_lines.append("| | | | |")
                        markdown_lines.append("|---|---|---|---|")
                    
                    # 画像行
                    image_row = "|"
                    for pdf_file in chunk:
                        if pdf_file:
                            pdf_filename = os.path.basename(pdf_file)
                            pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
                            image_path = f"{pdf_name_without_ext}.png"
                            symlink_path = pdf_filename
                            image_row += f" [![]({image_path})]({symlink_path}) |"
                        else:
                            image_row += " |"
                    markdown_lines.append(image_row)
                    
                    # タイトル行（オプション）
                    if show_title:
                        title_row = "|"
                        for pdf_file in chunk:
                            if pdf_file:
                                pdf_name_without_ext = os.path.splitext(os.path.basename(pdf_file))[0]
                                title_row += f" {pdf_name_without_ext} |"
                            else:
                                title_row += " |"
                        markdown_lines.append(title_row)
            else:
                # 単純なリスト形式
                for pdf_file in pdf_files:
                    if pdf_file:
                        pdf_filename = os.path.basename(pdf_file)
                        pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
                        image_path = f"{pdf_name_without_ext}.png"
                        symlink_path = pdf_filename
                        line = f"[![]({image_path})]({symlink_path})"
                        if show_title:
                            line += f" {pdf_name_without_ext}"
                        markdown_lines.append(line)
            
            return "\n".join(markdown_lines)
        except Exception as e:
            if self.logger:
                self.logger.log(f"エラー: マークダウン生成に失敗しました: {str(e)}")
            return ""


class AppSettings:
    """アプリケーション設定の管理を担当するクラス"""
    
    def __init__(self, settings_file="pdf_processor_settings.json"):
        self.settings_file = settings_file
        self.settings = {
            "input_path": "",
            "image_output_dir": "/obsidian/images/",
            "symlink_output_dir": "/obsidian/pdfs/",
            "use_table": True,
            "show_title": False
        }
        self.load_settings()
    
    def load_settings(self):
        """設定をファイルから読み込む"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception:
            # 設定ファイルの読み込みに失敗した場合はデフォルト設定を使用
            pass
    
    def save_settings(self):
        """設定をファイルに保存する"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception:
            # 設定ファイルの保存に失敗した場合は無視
            pass
    
    def get_setting(self, key):
        """設定値を取得する"""
        return self.settings.get(key)
    
    def set_setting(self, key, value):
        """設定値を設定する"""
        self.settings[key] = value
        self.save_settings()
    
    def reset_settings(self):
        """設定をデフォルトに戻す"""
        self.settings = {
            "input_path": "",
            "image_output_dir": "/obsidian/images/",
            "symlink_output_dir": "/obsidian/pdfs/",
            "use_table": True,
            "show_title": False
        }
        self.save_settings()


class Logger:
    """ログを管理するクラス"""
    
    def __init__(self, text_widget=None):
        self.text_widget = text_widget
    
    def log(self, message):
        """ログメッセージを追加する"""
        if self.text_widget:
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, message + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        print(message)  # コンソールにも出力


class MainApplication(tk.Tk):
    """メインのTkinterアプリケーションクラス"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Obsidian PDF Processor")
        self.geometry("800x1200")
        self.minsize(600, 500)
        
        # アプリケーション設定
        self.settings = AppSettings()
        
        # 変数の初期化
        self.input_files = []
        self.input_var = tk.StringVar(value=self.settings.get_setting("input_path"))
        self.image_output_var = tk.StringVar(value=self.settings.get_setting("image_output_dir"))
        self.symlink_output_var = tk.StringVar(value=self.settings.get_setting("symlink_output_dir"))
        self.use_table_var = tk.BooleanVar(value=self.settings.get_setting("use_table"))
        self.show_title_var = tk.BooleanVar(value=self.settings.get_setting("show_title"))
        
        # UIの構築
        self.create_ui()
        
        # オブジェクトの初期化
        self.logger = Logger(self.log_text)
        self.pdf_processor = PDFProcessor(self.logger)
        self.symlink_creator = SymbolicLinkCreator(self.logger)
        self.markdown_generator = MarkdownGenerator(self.logger)
    
    def create_ui(self):
        """UIを構築する"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 入力セクション
        input_frame = ttk.LabelFrame(main_frame, text="入力設定", padding=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        input_buttons_frame = ttk.Frame(input_frame)
        input_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(input_buttons_frame, text="ファイル選択", command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_buttons_frame, text="ディレクトリ選択", command=self.select_directory).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(input_frame, text="選択中:").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(input_frame, textvariable=self.input_var, state="readonly").pack(fill=tk.X, pady=5)
        
        # 出力セクション
        output_frame = ttk.LabelFrame(main_frame, text="出力設定", padding=5)
        output_frame.pack(fill=tk.X, pady=5)
        
        # 画像出力ディレクトリ
        image_output_frame = ttk.Frame(output_frame)
        image_output_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(image_output_frame, text="画像保存先:").pack(side=tk.LEFT)
        ttk.Button(image_output_frame, text="選択", command=self.select_image_output_dir).pack(side=tk.LEFT, padx=5)
        ttk.Entry(image_output_frame, textvariable=self.image_output_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # シンボリックリンク出力ディレクトリ
        symlink_output_frame = ttk.Frame(output_frame)
        symlink_output_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(symlink_output_frame, text="リンク作成先:").pack(side=tk.LEFT)
        ttk.Button(symlink_output_frame, text="選択", command=self.select_symlink_output_dir).pack(side=tk.LEFT, padx=5)
        ttk.Entry(symlink_output_frame, textvariable=self.symlink_output_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # オプションセクション
        options_frame = ttk.LabelFrame(main_frame, text="オプション", padding=5)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(options_frame, text="表形式にしない", variable=self.use_table_var, 
                        onvalue=False, offvalue=True, command=self.update_preview).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="タイトルを表示する", variable=self.show_title_var, 
                        command=self.update_preview).pack(anchor=tk.W)
        
        # プレビューセクション
        preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        preview_notebook = ttk.Notebook(preview_frame)
        preview_notebook.pack(fill=tk.BOTH, expand=True)
        
        # マークダウンプレビュータブ
        markdown_preview_frame = ttk.Frame(preview_notebook)
        preview_notebook.add(markdown_preview_frame, text="マークダウンプレビュー")
        
        self.markdown_preview = scrolledtext.ScrolledText(markdown_preview_frame, wrap=tk.WORD)
        self.markdown_preview.pack(fill=tk.BOTH, expand=True)
        
        # シンボリックリンクパス一覧タブ
        symlink_preview_frame = ttk.Frame(preview_notebook)
        preview_notebook.add(symlink_preview_frame, text="シンボリックリンクパス一覧")
        
        self.symlink_preview = scrolledtext.ScrolledText(symlink_preview_frame, wrap=tk.WORD)
        self.symlink_preview.pack(fill=tk.BOTH, expand=True)
        
        # ログセクション
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding=5)
        log_frame.pack(fill=tk.X, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH)
        self.log_text.configure(state="disabled")
        
        # ボタンセクション
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 各処理用の個別のボタン
        ttk.Button(button_frame, text="画像抽出のみ実行", command=self.execute_image_extraction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="シンボリックリンク作成のみ実行", command=self.execute_symlink_creation).pack(side=tk.LEFT, padx=5)
        
        # 実行ボタンをより目立たせる
        execute_btn = ttk.Button(button_frame, text="すべて実行", command=self.execute, style="Execute.TButton")
        execute_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="設定リセット", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        
        # 実行ボタン用の特別なスタイルを定義
        style = ttk.Style()
        style.configure("Execute.TButton", font=("Helvetica", 12, "bold"), padding=5)
    
    def select_files(self):
        """ファイル選択ダイアログを表示"""
        files = filedialog.askopenfilenames(
            title="処理するPDFファイルを選択",
            filetypes=[("PDFファイル", "*.pdf")]
        )
        if files:
            self.input_files = list(files)
            self.input_var.set(f"{len(self.input_files)} ファイルを選択中")
            self.settings.set_setting("input_path", self.input_files[0] if self.input_files else "")
            self.update_preview()
    
    def select_directory(self):
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory(title="処理するPDFファイルを含むディレクトリを選択")
        if directory:
            self.input_var.set(directory)
            self.settings.set_setting("input_path", directory)
            
            # ディレクトリ内のPDFファイルを取得
            self.input_files = []
            for file in os.listdir(directory):
                if file.lower().endswith(".pdf"):
                    self.input_files.append(os.path.join(directory, file))
            
            self.update_preview()
    
    def select_image_output_dir(self):
        """画像出力ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory(title="画像の保存先ディレクトリを選択")
        if directory:
            self.image_output_var.set(directory)
            self.settings.set_setting("image_output_dir", directory)
            self.update_preview()
    
    def select_symlink_output_dir(self):
        """シンボリックリンク出力ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory(title="シンボリックリンクの作成先ディレクトリを選択")
        if directory:
            self.symlink_output_var.set(directory)
            self.settings.set_setting("symlink_output_dir", directory)
            self.update_preview()
    
    def update_preview(self):
        """プレビューを更新"""
        # 設定を更新
        self.settings.set_setting("use_table", self.use_table_var.get())
        self.settings.set_setting("show_title", self.show_title_var.get())
        
        # マークダウンプレビューを更新
        markdown = self.markdown_generator.generate_markdown(
            self.input_files,
            self.image_output_var.get(),
            self.symlink_output_var.get(),
            self.use_table_var.get(),
            self.show_title_var.get()
        )
        
        self.markdown_preview.delete(1.0, tk.END)
        self.markdown_preview.insert(tk.END, markdown)
        
        # シンボリックリンクパス一覧を更新
        self.symlink_preview.delete(1.0, tk.END)
        for pdf_file in self.input_files:
            if pdf_file:
                symlink_path = os.path.join(
                    self.symlink_output_var.get(),
                    os.path.basename(pdf_file)
                )
                self.symlink_preview.insert(tk.END, f"{symlink_path} -> {pdf_file}\n")
    
    def execute(self):
        """処理を実行"""
        if not self.input_files:
            messagebox.showwarning("警告", "処理するPDFファイルが選択されていません。")
            return
        
        image_output_dir = self.image_output_var.get()
        symlink_output_dir = self.symlink_output_var.get()
        
        # 出力ディレクトリが存在するか確認
        if not os.path.exists(image_output_dir):
            try:
                os.makedirs(image_output_dir)
                self.logger.log(f"ディレクトリを作成しました: {image_output_dir}")
            except Exception as e:
                messagebox.showerror("エラー", f"画像保存先ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        if not os.path.exists(symlink_output_dir):
            try:
                os.makedirs(symlink_output_dir)
                self.logger.log(f"ディレクトリを作成しました: {symlink_output_dir}")
            except Exception as e:
                messagebox.showerror("エラー", f"シンボリックリンク作成先ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        # 処理を別スレッドで実行
        threading.Thread(target=self._process_files).start()
        
    def execute_image_extraction(self):
        """PDFから画像のみを抽出する"""
        if not self.input_files:
            messagebox.showwarning("警告", "処理するPDFファイルが選択されていません。")
            return
        
        image_output_dir = self.image_output_var.get()
        
        # 出力ディレクトリが存在するか確認
        if not os.path.exists(image_output_dir):
            try:
                os.makedirs(image_output_dir)
                self.logger.log(f"ディレクトリを作成しました: {image_output_dir}")
            except Exception as e:
                messagebox.showerror("エラー", f"画像保存先ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        # 処理を別スレッドで実行
        threading.Thread(target=self._extract_images_only).start()
        
    def _extract_images_only(self):
        """画像抽出のみを実行（別スレッド）"""
        image_output_dir = self.image_output_var.get()
        
        self.logger.log("画像抽出を開始します...")
        
        # 各PDFファイルを処理
        for pdf_file in self.input_files:
            try:
                # 表紙画像を抽出
                self.pdf_processor.extract_cover_image(pdf_file, image_output_dir)
            except Exception as e:
                self.logger.log(f"エラー: 画像抽出中にエラーが発生しました: {str(e)}")
        
        def update_ui():
            self.logger.log("画像抽出が完了しました。")
            messagebox.showinfo("完了", "画像抽出が完了しました。")
        
        # UIの更新はメインスレッドで実行
        self.after(0, update_ui)
        
    def execute_symlink_creation(self):
        """シンボリックリンクのみを作成する"""
        if not self.input_files:
            messagebox.showwarning("警告", "処理するPDFファイルが選択されていません。")
            return
        
        symlink_output_dir = self.symlink_output_var.get()
        
        # 出力ディレクトリが存在するか確認
        if not os.path.exists(symlink_output_dir):
            try:
                os.makedirs(symlink_output_dir)
                self.logger.log(f"ディレクトリを作成しました: {symlink_output_dir}")
            except Exception as e:
                messagebox.showerror("エラー", f"シンボリックリンク作成先ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        # 処理を別スレッドで実行
        threading.Thread(target=self._create_symlinks_only).start()
        
    def _create_symlinks_only(self):
        """シンボリックリンク作成のみを実行（別スレッド）"""
        symlink_output_dir = self.symlink_output_var.get()
        
        self.logger.log("シンボリックリンク作成を開始します...")
        
        # シンボリックリンク作成記録をクリア
        self.symlink_creator.clear_created_links()
        
        # 各PDFファイルを処理
        for pdf_file in self.input_files:
            try:
                # シンボリックリンクを作成
                self.symlink_creator.create_symlink(pdf_file, symlink_output_dir)
            except Exception as e:
                self.logger.log(f"エラー: シンボリックリンク作成中にエラーが発生しました: {str(e)}")
        
        # シンボリックリンクパス一覧を更新
        created_links = self.symlink_creator.get_created_links()
        
        def update_ui():
            self.symlink_preview.delete(1.0, tk.END)
            for link in created_links:
                target = os.readlink(link) if os.path.islink(link) else "不明"
                self.symlink_preview.insert(tk.END, f"{link} -> {target}\n")
            
            self.logger.log("シンボリックリンク作成が完了しました。")
            messagebox.showinfo("完了", "シンボリックリンク作成が完了しました。")
        
        # UIの更新はメインスレッドで実行
        self.after(0, update_ui)
    
    def _process_files(self):
        """ファイル処理を実行（別スレッド）"""
        image_output_dir = self.image_output_var.get()
        symlink_output_dir = self.symlink_output_var.get()
        
        self.logger.log("処理を開始します...")
        
        # シンボリックリンク作成記録をクリア
        self.symlink_creator.clear_created_links()
        
        # 各PDFファイルを処理
        for pdf_file in self.input_files:
            try:
                # 表紙画像を抽出
                self.pdf_processor.extract_cover_image(pdf_file, image_output_dir)
                
                # シンボリックリンクを作成
                self.symlink_creator.create_symlink(pdf_file, symlink_output_dir)
            except Exception as e:
                self.logger.log(f"エラー: ファイル処理中にエラーが発生しました: {str(e)}")
        
        # シンボリックリンクパス一覧を更新
        created_links = self.symlink_creator.get_created_links()
        
        def update_ui():
            self.symlink_preview.delete(1.0, tk.END)
            for link in created_links:
                target = os.readlink(link) if os.path.islink(link) else "不明"
                self.symlink_preview.insert(tk.END, f"{link} -> {target}\n")
            
            # マークダウンをクリップボードにコピー
            markdown = self.markdown_preview.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(markdown)
            
            self.logger.log("処理が完了しました。マークダウンテキストがクリップボードにコピーされました。")
            messagebox.showinfo("完了", "処理が完了しました。マークダウンテキストがクリップボードにコピーされました。")
        
        # UIの更新はメインスレッドで実行
        self.after(0, update_ui)
    
    def reset_settings(self):
        """設定をリセット"""
        if messagebox.askyesno("確認", "設定をデフォルトに戻しますか？"):
            self.settings.reset_settings()
            
            # UI変数を更新
            self.input_var.set(self.settings.get_setting("input_path"))
            self.image_output_var.set(self.settings.get_setting("image_output_dir"))
            self.symlink_output_var.set(self.settings.get_setting("symlink_output_dir"))
            self.use_table_var.set(self.settings.get_setting("use_table"))
            self.show_title_var.set(self.settings.get_setting("show_title"))
            
            # 入力ファイルリストをクリア
            self.input_files = []
            
            # プレビューを更新
            self.update_preview()
            
            self.logger.log("設定がリセットされました。")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
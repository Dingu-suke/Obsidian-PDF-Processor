import os
import re

class MarkdownGenerator:
    """マークダウン文字列の生成を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def generate_markdown(self, pdf_files, image_dir, symlink_dir, use_table=True, show_title=False, subdir_name="book_covers"):
        """マークダウン文字列を生成する"""
        try:
            if not pdf_files:
                if self.logger:
                    self.logger.log("警告: 処理するPDFファイルがありません")
                return ""
            
            # PDFファイルを名前でソート
            pdf_files.sort(key=lambda x: os.path.basename(x).lower())
            
            markdown_lines = []
            
            # 画像サブディレクトリ名
            image_subdir = subdir_name
            
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
                            # ファイル名のスペース（半角・全角）をアンダースコアに置換
                            image_filename = re.sub(r'[\s\u3000]+', '_', f"{pdf_name_without_ext}.png")
                            pdf_filename_no_spaces = re.sub(r'[\s\u3000]+', '_', pdf_filename)
                            image_path = f"{image_subdir}/{image_filename}"
                            symlink_path = f"{subdir_name}/{pdf_filename_no_spaces}"
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
                        # ファイル名のスペース（半角・全角）をアンダースコアに置換
                        image_filename = re.sub(r'[\s\u3000]+', '_', f"{pdf_name_without_ext}.png")
                        pdf_filename_no_spaces = re.sub(r'[\s\u3000]+', '_', pdf_filename)
                        image_path = f"{image_subdir}/{image_filename}"
                        symlink_path = f"{subdir_name}/{pdf_filename_no_spaces}"
                        line = f"[![]({image_path})]({symlink_path})"
                        if show_title:
                            line += f" {pdf_name_without_ext}"
                        markdown_lines.append(line)
            
            return "\n".join(markdown_lines)
        except Exception as e:
            if self.logger:
                self.logger.log(f"エラー: マークダウン生成に失敗しました: {str(e)}")
            return ""
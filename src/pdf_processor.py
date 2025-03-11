import os
import re
from PIL import Image
import fitz  # PyMuPDF
from io import BytesIO

class PDFProcessor:
    """PDFの処理を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def extract_cover_image_with_pymupdf(self, pdf_path, output_dir, subdir_name="book_covers"):
        """PyMuPDFを使用してPDFの表紙画像を視覚的に正確に抽出する"""
        try:

            # ファイル名の処理
            pdf_filename = os.path.basename(pdf_path)
            pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
            output_filename = re.sub(r'[\s\u3000]+', '_', f"{pdf_name_without_ext}.png")
            
            # サブディレクトリ作成
            subdir_path = os.path.join(output_dir, subdir_name)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
                if self.logger:
                    self.logger.log(f"表紙画像用サブディレクトリを作成しました: {subdir_path}")
            
            output_path = os.path.join(subdir_path, output_filename)
            
            # 既存ファイルチェック
            if os.path.exists(output_path):
                if self.logger:
                    self.logger.log(f"画像すでに存在します: {output_path}")
                return output_path, subdir_name
            
            # PDFドキュメントを開く
            doc = fitz.open(pdf_path)
            if not doc:
                if self.logger:
                    self.logger.log(f"エラー: PDFを開けませんでした: {pdf_path}")
                return None, None
            
            # 1ページ目を取得
            page = doc[0]
            
            # 高解像度でレンダリング（dpi = 300に相当）
            zoom_factor = 300 / 72  # 標準DPIの4倍の解像度
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            # PDFのビューワー表示に忠実なレンダリング
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PILイメージに変換
            img_data = pix.tobytes("png")
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
            
            # 必要に応じてサイズ調整
            max_size = (600, 800)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # 画像を保存
            img.save(output_path, "PNG")
            
            if self.logger:
                self.logger.log(f"表紙画像を保存しました: {output_path}")
            
            return output_path, subdir_name
            
        except ImportError:
            if self.logger:
                self.logger.log("PyMuPDFがインストールされていません。pip install pymupdfを実行してください。")
            return None, None
        except Exception as e:
            if self.logger:
                self.logger.log(f"エラー: {str(e)}")
            return None, None
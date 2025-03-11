import os
import re

class SymbolicLinkCreator:
    """シンボリックリンクの作成を担当するクラス"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.created_links = []
    
    def create_symlink(self, source_path, output_dir, subdir_name="book_covers"):
        """シンボリックリンクを作成する"""
        try:
            # ファイル名を取得
            filename = os.path.basename(source_path)
            # ファイル名のスペース（半角・全角）をアンダースコアに置換
            filename_no_spaces = re.sub(r'[\s\u3000]+', '_', filename)
            
            # サブディレクトリを作成
            subdir_path = os.path.join(output_dir, subdir_name)
            
            # サブディレクトリが存在しない場合は作成
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
                if self.logger:
                    self.logger.log(f"PDFリンク用サブディレクトリを作成しました: {subdir_path}")
            
            # 出力ファイルパスを作成（スペースをアンダースコアに置換した名前を使用）
            output_path = os.path.join(subdir_path, filename_no_spaces)
            
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
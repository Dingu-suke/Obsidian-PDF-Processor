import os
import json

class AppSettings:
    """アプリケーション設定の管理を担当するクラス"""
    
    def __init__(self, settings_file="pdf_processor_settings.json"):
        self.settings_file = settings_file
        self.settings = {
            "input_path": "",
            "image_output_dir": "/obsidian/images/",
            "symlink_output_dir": "/obsidian/pdfs/",
            "subdir_name": "book_covers",
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
            "subdir_name": "book_covers",
            "use_table": True,
            "show_title": False
        }
        self.save_settings()
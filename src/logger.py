import tkinter as tk

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

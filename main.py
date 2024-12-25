import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QRadioButton, QButtonGroup, QComboBox, QWidget, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from yt_dlp import YoutubeDL


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    
    def __init__(self, url, save_path, options):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.options = options

    def run(self):
        try:
            with YoutubeDL(self.options) as ydl:
                ydl.download([self.url])
            self.progress_signal.emit("完成")
        except Exception as e:
            self.progress_signal.emit(f"失敗：{str(e)}")


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MeowMeow")
        self.setGeometry(300, 200, 500, 400)
        self.setFont(QFont("微軟正黑體", 12))

        # 默認保存路徑為桌面
        self.save_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # 主界面布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 標題
        title_label = QLabel("我是Youtube音樂下載器")
        title_label.setFont(QFont("微軟正黑體", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 輸入欄
        self.url_label = QLabel("請輸入 YouTube 影片網址：")
        layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        # 選擇格式
        self.format_label = QLabel("選擇下載格式：")
        layout.addWidget(self.format_label)

        self.mp3_radio = QRadioButton("MP3（音樂）")
        self.mp4_radio = QRadioButton("MP4（影片）")
        self.mp3_radio.setChecked(True)
        self.format_group = QButtonGroup()
        self.format_group.addButton(self.mp3_radio)
        self.format_group.addButton(self.mp4_radio)
        layout.addWidget(self.mp3_radio)
        layout.addWidget(self.mp4_radio)

        # 畫質選擇
        self.quality_label = QLabel("選擇 MP4 視頻畫質：")
        layout.addWidget(self.quality_label)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "360p", "480p", "720p", "1080p"])
        self.quality_combo.setCurrentIndex(0)  # 默認選擇 "best"
        layout.addWidget(self.quality_combo)

        # 選擇保存路徑
        self.path_label = QLabel("選擇保存路徑：")
        layout.addWidget(self.path_label)
        self.path_button = QPushButton("選擇路徑")
        self.path_button.clicked.connect(self.select_path)
        layout.addWidget(self.path_button)

        # 顯示當前保存路徑
        self.selected_path_label = QLabel(f"當前保存路徑（默認桌面）：{self.save_path}")
        layout.addWidget(self.selected_path_label)

        # 開始下載按鈕
        self.download_button = QPushButton("開始下載")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

    def select_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "選擇保存路徑")
        if selected_path:
            self.save_path = selected_path
            self.selected_path_label.setText(f"當前保存路徑：{self.save_path}")
        else:
            self.selected_path_label.setText(f"當前保存路徑：{self.save_path}")

    def start_download(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "錯誤", "請輸入有效的 YouTube 影片網址！")
            return

        if not self.save_path:
            QMessageBox.warning(self, "錯誤", "請選擇保存路徑！")
            return

        if self.mp3_radio.isChecked():
            output_template = f"{self.save_path}/%(title)s.mp3"
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template
            }
        elif self.mp4_radio.isChecked():
            output_template = f"{self.save_path}/%(title)s.mp4"
            quality = self.quality_combo.currentText()  # 獲取當前選擇的畫質
            if quality == "best":
                format_selector = "best"
            else:
                height_value = quality[:-1]  # 去掉 "p"，保留數字部分
                format_selector = f"best[height<={height_value}]"
            ydl_opts = {
                "format": format_selector,
                "outtmpl": output_template
            }
        else:
            return

        # 啟動下載線程
        self.download_thread = DownloadThread(url, self.save_path, ydl_opts)
        self.download_thread.progress_signal.connect(self.show_progress)
        self.download_thread.start()
        QMessageBox.information(self, "通知", "下載已開始，請稍候。")

    def show_progress(self, message):
        if "完成" in message:
            QMessageBox.information(self, "完成", "下載成功！")
        else:
            QMessageBox.critical(self, "錯誤", f"下載失敗：{message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())

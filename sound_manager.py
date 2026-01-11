import winsound # Thư viện âm thanh mặc định của Windows
import threading

class SoundManager:
    @staticmethod
    def play_click():
        # Phát tiếng bíp ngắn khi nhấn nút
        threading.Thread(target=lambda: winsound.Beep(600, 100), daemon=True).start()

    @staticmethod
    def play_win():
        # Phát tiếng thắng cuộc
        threading.Thread(target=lambda: winsound.Beep(1000, 500), daemon=True).start()

    @staticmethod
    def play_lose():
        # Phát tiếng khi thua
        threading.Thread(target=lambda: winsound.Beep(300, 500), daemon=True).start()
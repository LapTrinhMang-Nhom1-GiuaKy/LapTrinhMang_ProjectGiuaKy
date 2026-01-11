import socket
import sys
from login_gui import LoginWindow  # Gọi hàm Login từ file bạn vừa sửa
from game_gui import GameWindow
from sound_manager import SoundManager

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

class RPSClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.gui_game = None
        self.player_name = ""

    def send_line(self, msg):
        if self.sock:
            self.sock.sendall((msg + "\n").encode("utf-8"))

    def recv_line(self):
        data = b""
        while True:
            try:
                chunk = self.sock.recv(1)
                if not chunk: return None
                if chunk == b"\n": break
                data += chunk
            except: return None
        return data.decode("utf-8", errors="ignore").strip()

    def start_connection(self, name):
        """Hàm này sẽ được truyền vào LoginWindow để chạy khi nhấn nút"""
        self.player_name = name
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            
            # Nhận câu chào từ server và gửi HELLO
            self.recv_line() 
            self.send_line(f"HELLO {name}")
            
            # Đợi lệnh START từ server để mở màn hình Game
            while True:
                line = self.recv_line()
                if not line: break
                
                if line.startswith("START "):
                    opponent = line.split(" ", 1)[1]
                    # Khởi tạo giao diện bàn chơi chính (Nhiệm vụ UI/UX)
                    self.gui_game = GameWindow(self.player_name, opponent, self.send_move)
                    self.listen_server_results()
                    break
        except Exception as e:
            print(f"Lỗi kết nối: {e}")

    def send_move(self, move):
        """Gửi nước đi và phát âm thanh click"""
        SoundManager.play_click()
        self.send_line(f"MOVE {move}")

    def listen_server_results(self):
        """Vòng lặp lắng nghe kết quả để cập nhật giao diện"""
        while True:
            line = self.recv_line()
            if not line: break

            if line == "PROMPT_MOVE":
                self.gui_game.label_status.config(text="Đến lượt bạn chọn!")
            
            elif line.startswith("RESULT "):
                parts = line.split()
                status, my_m, opp_m = parts[1], parts[2], parts[3]
                
                # Cập nhật kết quả lên màn hình và phát âm thanh thắng/thua
                self.gui_game.update_result(status, my_m, opp_m)
                if status == "win": SoundManager.play_win()
                elif status == "lose": SoundManager.play_lose()
                
            elif line == "ASK_PLAY_AGAIN":
                self.send_line("PLAY_AGAIN yes")

    def run(self):
        # Gọi hàm LoginWindow từ file login_gui.py
        # Lưu ý: Không dùng .run() vì nó đã là một hàm tự chạy mainloop
        LoginWindow(self.start_connection)

if __name__ == "__main__":
    client_app = RPSClient(SERVER_HOST, SERVER_PORT)
    client_app.run()
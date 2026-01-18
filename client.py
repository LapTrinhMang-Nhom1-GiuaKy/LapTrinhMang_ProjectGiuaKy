import socket
import threading
from tkinter import messagebox
from login_gui import LoginWindow
from game_gui import GameWindow
from lobby_gui import LobbyWindow
from sound_manager import SoundManager

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

class RPSClient:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.sock = None
        self.gui_lobby = self.gui_game = None
        self.player_name = ""
        self.tk_login_root = None

    def send_line(self, msg):
        if self.sock:
            try: self.sock.sendall((msg + "\n").encode("utf-8"))
            except: pass

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

    def start_connection(self, name, tk_root_login):
        self.player_name, self.tk_login_root = name, tk_root_login
        threading.Thread(target=self._connect_and_listen, args=(name,), daemon=True).start()

    def _connect_and_listen(self, name):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.recv_line() # WELCOME
            self.send_line(f"HELLO {name}")
            resp = self.recv_line()
            if resp and resp.startswith("OK"):
                # CHÚ Ý: Dùng after để gọi giao diện trên Main Thread
                self.tk_login_root.after(0, self.open_lobby)
                self.listen_loop()
            else:
                messagebox.showerror("Lỗi", "Tên đã tồn tại hoặc server từ chối.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Kết nối thất bại: {e}")

    def open_lobby(self):
        # Không destroy login_root, chỉ ẩn đi nếu cần hoặc dùng làm master
        self.gui_lobby = LobbyWindow(self.player_name, master=self.tk_login_root, on_invite_callback=self.send_invite)

    def listen_loop(self):
        while True:
            line = self.recv_line()
            if not line: break
            if line.startswith("LOBBY_UPDATE "):
                d = line.split(" ", 1)[1]
                if self.gui_lobby: self.tk_login_root.after(0, lambda d=d: self.gui_lobby.update_list(d))
            elif line.startswith("INVITE_REQ "):
                s = line.split(" ", 1)[1]
                self.tk_login_root.after(0, lambda s=s: self.handle_invite(s))
            elif line.startswith("START "):
                opp = line.split(" ", 1)[1]
                self.tk_login_root.after(0, lambda opp=opp: self.enter_game(opp))
            elif line == "PROMPT_MOVE":
                self.tk_login_root.after(0, lambda: self.gui_game.enable_buttons() if self.gui_game else None)
            elif line.startswith("RESULT "):
                p = line.split()
                if len(p) >= 6:
                    self.tk_login_root.after(0, lambda p=p: self.gui_game.update_result(p[1], p[2], p[3], int(p[4]), int(p[5])))
            elif line == "ASK_PLAY_AGAIN":
                self.send_line("PLAY_AGAIN YES")
            elif line == "GOODBYE":
                self.tk_login_root.after(0, self.return_to_lobby)

    def handle_invite(self, sender):
        ans = "YES" if messagebox.askyesno("Lời mời", f"{sender} rủ bạn chơi?") else "NO"
        self.send_line(f"INVITE_RESP {sender} {ans}")

    def enter_game(self, opponent):
        if self.gui_lobby: self.gui_lobby.withdraw() # Ẩn sảnh chờ
        self.gui_game = GameWindow(self.player_name, opponent, lambda m: self.send_line(f"MOVE {m}"), master=self.tk_login_root)

    def return_to_lobby(self):
        if self.gui_game: 
            try: self.gui_game.root.destroy()
            except: pass
            self.gui_game = None
        if self.gui_lobby: self.gui_lobby.deiconify() # Hiện lại sảnh chờ

    def run(self):
        LoginWindow(self.start_connection)

if __name__ == "__main__":
    RPSClient(SERVER_HOST, SERVER_PORT).run()
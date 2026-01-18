import socket
import sys
import threading
import time
from tkinter import messagebox
import tkinter as tk

from login_gui import LoginWindow
from game_gui import GameWindow
from lobby_gui import LobbyWindow
from sound_manager import SoundManager

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

class RPSClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.gui_lobby = None
        self.gui_game = None
        self.player_name = ""
        self.tk_root = None # Holds the root of the current major window (usually Lobby)
        self.last_lobby_data = None # Start with None

    def send_line(self, msg):
        if self.sock:
            try:
                self.sock.sendall((msg + "\n").encode("utf-8"))
            except:
                pass

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
        """
        tk_root_login: root của LoginWindow.
        """
        self.player_name = name
        self.tk_login_root = tk_root_login
        
        threading.Thread(target=self._connect_and_listen, args=(name,), daemon=True).start()

    def _connect_and_listen(self, name):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

            # Handshake
            self.recv_line() # WELCOME
            self.send_line(f"HELLO {name}")
            
            response = self.recv_line() # OK ... or ERROR
            if not response or not response.startswith("OK"):
                print("Login failed")
                return

            # Login Success -> Show Lobby
            self.tk_login_root.after(0, self.open_lobby)

            # Main Loop Listen
            self.listen_loop()

        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            messagebox.showerror("Lỗi", f"Không thể kết nối đến server: {e}")

    def open_lobby(self):
        # Create Lobby Window
        self.gui_lobby = LobbyWindow(self.player_name, master=self.tk_login_root,
                                     on_invite_callback=self.send_invite)
        
        # Bind manual refresh
        self.tk_login_root.bind("<<RefreshLobby>>", lambda e: self.send_line("HELLO " + self.player_name))

        # Check buffer
        if self.last_lobby_data:
             self.gui_lobby.update_list(self.last_lobby_data)
    
    def send_invite(self, target_name):
        self.send_line(f"INVITE {target_name}")

    def send_move(self, move):
        SoundManager.play_click()
        self.send_line(f"MOVE {move}")

    def listen_loop(self):
        while True:
            line = self.recv_line()
            if not line:
                print("Disconnected from server")
                break
            
            # --- LOBBY MESSAGES ---
            if line.startswith("LOBBY_UPDATE "):
                data = line.split(" ", 1)[1]
                self.last_lobby_data = data # Buffer it
                
                if self.gui_lobby:
                    self.gui_lobby.after(0, lambda d=data: self.gui_lobby.update_list(d))
            
            elif line.startswith("INVITE_REQ "):
                sender = line.split(" ", 1)[1]
                self.handle_invite_request(sender)
            
            elif line.startswith("INVITE_REJECT "):
                target = line.split(" ", 1)[1]
                if self.gui_lobby:
                    self.gui_lobby.after(0, lambda t=target: messagebox.showinfo("Từ chối", f"{t} đã từ chối lời mời."))

            elif line.startswith("ERROR "):
                err = line.split(" ", 1)[1]
                if self.gui_lobby:
                    self.gui_lobby.after(0, lambda e=err: messagebox.showerror("Lỗi", e))

            # --- GAME MESSAGES ---
            elif line.startswith("START "):
                opponent = line.split(" ", 1)[1]
                self.enter_game(opponent)
            
            elif line == "PROMPT_MOVE":
                def _try_enable(count=0):
                    if self.gui_game:
                         try:
                             self.gui_game.enable_buttons()
                             self.gui_game.label_status.configure(text="Đến lượt bạn chọn!", text_color="#9feffb")
                         except: pass
                    elif count < 20:
                        if self.tk_login_root:
                            self.tk_login_root.after(100, lambda: _try_enable(count+1))
                
                if self.tk_login_root:
                    self.tk_login_root.after(0, _try_enable)

            elif line.startswith("RESULT "):
                print(f"[CLIENT] Recv RESULT: {line}")
                parts = line.split()
                if len(parts) >= 6:
                    status, my_m, opp_m, my_score, opp_score = parts[1], parts[2], parts[3], int(parts[4]), int(parts[5])
                    
                    def _update_result(count=0):
                        if self.gui_game:
                            try:
                                self.gui_game.update_result(status, my_m, opp_m, my_score, opp_score)
                            except: pass
                        elif count < 20:
                             if self.tk_login_root:
                                self.tk_login_root.after(100, lambda: _update_result(count+1))
                    
                    if self.tk_login_root:
                        self.tk_login_root.after(0, _update_result)
                    
                    if status == "win": SoundManager.play_win()
                    elif status == "lose": SoundManager.play_lose()

                    if my_m == "exit" or opp_m == "exit":
                         print("[CLIENT] Detected Exit Result -> Scheduling Return to Lobby")
                         if self.tk_login_root:
                             self.tk_login_root.after(2000, self.return_to_lobby)

            elif line == "ASK_PLAY_AGAIN":
                self.send_line("PLAY_AGAIN yes")

            elif line == "GOODBYE":
                self.return_to_lobby()

    def handle_invite_request(self, sender):
        def _ask():
            ans = messagebox.askyesno("Lời mời", f"{sender} muốn rủ bạn chơi. Đồng ý?")
            if ans:
                self.send_line(f"INVITE_RESP {sender} YES")
            else:
                self.send_line(f"INVITE_RESP {sender} NO")
        
        if self.gui_lobby:
            self.gui_lobby.after(0, _ask)

    def enter_game(self, opponent):
        if self.gui_lobby:
            self.gui_lobby.after(0, self.gui_lobby.withdraw)
        
        def _create():
            self.gui_game = GameWindow(self.player_name, opponent, self.send_move, master=self.tk_login_root)
            
            def _on_destroy(event):
                if event.widget == self.gui_game.root:
                    self.return_to_lobby()
                    
            self.gui_game.root.bind("<Destroy>", _on_destroy)
        
        self.tk_login_root.after(0, _create)

    def return_to_lobby(self):
        def _back():
            if self.gui_game:
                try:
                    if self.gui_game.root.winfo_exists():
                        self.gui_game.root.destroy()
                except:
                    pass
                self.gui_game = None

            if self.gui_lobby:
                try:
                    self.gui_lobby.deiconify()
                    self.send_line("HELLO " + self.player_name)
                except:
                    pass
        
        if self.tk_login_root:
            self.tk_login_root.after(0, _back)

    def run(self):
        LoginWindow(self.start_connection)

if __name__ == "__main__":
    client_app = RPSClient(SERVER_HOST, SERVER_PORT)
    client_app.run()
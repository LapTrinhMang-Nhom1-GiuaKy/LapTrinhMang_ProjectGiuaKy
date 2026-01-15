import customtkinter as ctk
from tkinter import messagebox
from sound_manager import SoundManager

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Theme colors
_BG = "#071020"
_CARD = "#0d1624"
_ACCENT = "#00f5ff"
_NEON_ROCK = "#ff8c42"
_NEON_PAPER = "#6ee7ff"
_NEON_SCISSORS = "#7cff8a"
_TEXT = "#e7ffff"


class GameWindow:
    def __init__(self, player_name, opponent_name, on_send_move, master=None):
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.on_send_move = on_send_move

        if master is not None:
            self.root = ctk.CTkToplevel(master)
        else:
            self.root = ctk.CTk()
        self.root.title(f"Bàn chơi - {player_name} vs {opponent_name}")
        self.root.geometry("420x300")
        self.root.configure(bg=_BG)

        header = ctk.CTkFrame(self.root, fg_color=_CARD)
        header.pack(fill="x", pady=12, padx=12)
        ctk.CTkLabel(header, text=f"Bạn: {player_name}", font=("Helvetica", 12, "bold"), text_color=_ACCENT).pack(side="left", padx=6)
        self.label_score = ctk.CTkLabel(header, text="Điểm: 0 - 0", font=("Helvetica", 12), text_color=_TEXT)
        self.label_score.pack(side="left", padx=20)
        ctk.CTkLabel(header, text=f"Đối thủ: {opponent_name}", font=("Helvetica", 12), text_color=_TEXT).pack(side="right", padx=6)

        self.label_status = ctk.CTkLabel(self.root, text="Chờ lệnh START...", font=("Helvetica", 12), text_color="#9feffb")
        self.label_status.pack(pady=10)

        btn_frame = ctk.CTkFrame(self.root, fg_color=_BG)
        btn_frame.pack(pady=10)

        b_rock = ctk.CTkButton(btn_frame, text="ROCK", fg_color=_NEON_ROCK, text_color="#0b0b06", width=100,
                               font=("Helvetica", 10, "bold"), hover_color="#ffb070",
                               command=lambda: self.send_move("rock"))
        b_paper = ctk.CTkButton(btn_frame, text="PAPER", fg_color=_NEON_PAPER, text_color="#04202a", width=100,
                                font=("Helvetica", 10, "bold"), hover_color="#bff7ff",
                                command=lambda: self.send_move("paper"))
        b_scissors = ctk.CTkButton(btn_frame, text="SCISSORS", fg_color=_NEON_SCISSORS, text_color="#052205", width=100,
                                   font=("Helvetica", 10, "bold"), hover_color="#cffecc",
                                   command=lambda: self.send_move("scissors"))

        b_rock.pack(side="left", padx=8)
        b_paper.pack(side="left", padx=8)
        b_scissors.pack(side="left", padx=8)

        self.buttons = [b_rock, b_paper, b_scissors]  # Để dễ quản lý
        self.disable_buttons()  # Disable ban đầu, enable khi PROMPT_MOVE

        self.label_result = ctk.CTkLabel(self.root, text="", font=("Helvetica", 16, "bold"), text_color=_ACCENT)
        self.label_result.pack(pady=12)

        # Music toggle
        self.music_on = False
        self.btn_music = ctk.CTkButton(self.root, text="Nhạc: Tắt", width=120, fg_color="#14202a", text_color=_ACCENT,
                                       command=self.toggle_music)
        self.btn_music.pack(pady=6)

        # Exit button
        self.btn_exit = ctk.CTkButton(self.root, text="Thoát Game", width=120, fg_color="#ff4444", text_color="#ffffff",
                                      command=self.exit_game)
        self.btn_exit.pack(pady=6)

    def send_move(self, move):
        self.label_status.configure(text=f"Đã chọn: {move}", text_color="#9feffb")
        try:
            self.on_send_move(move)
        except Exception:
            pass

    def update_result(self, status, my_move, opp_move, my_score, opp_score):
        if my_move == "exit":
            msg = "Đối thủ đã thoát, bạn thắng!"
            color = "#7cff8a"
        elif status == "win":
            msg = f"Bạn thắng! {my_move} vs {opp_move}"
            color = "#7cff8a"
        elif status == "lose":
            msg = f"Bạn thua! {my_move} vs {opp_move}"
            color = "#ff6b6b"
        else:
            msg = f"Hòa! {my_move} vs {opp_move}"
            color = "#ffd86b"
        self.label_result.configure(text=msg, text_color=color)
        self.label_score.configure(text=f"Điểm: {my_score} - {opp_score}")
        self.disable_buttons()  # Disable sau kết quả

    def toggle_music(self):
        new_state = not self.music_on
        SoundManager.play_music(new_state)
        self.music_on = new_state
        self.btn_music.configure(text=("Nhạc: Bật" if self.music_on else "Nhạc: Tắt"))

    def exit_game(self):
        # Gửi EXIT và đóng cửa sổ
        try:
            self.on_send_move("EXIT")
        except Exception:
            pass
        self.root.destroy()

    def disable_buttons(self):
        for btn in self.buttons:
            btn.configure(state="disabled")

    def enable_buttons(self):
        for btn in self.buttons:
            btn.configure(state="normal")

    def mainloop(self):
        self.root.mainloop()
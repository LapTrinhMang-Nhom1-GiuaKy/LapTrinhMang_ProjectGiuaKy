import tkinter as tk
from tkinter import messagebox
from sound_manager import SoundManager

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
            self.root = tk.Toplevel(master)
        else:
            self.root = tk.Tk()
        self.root.title(f"Bàn chơi - {player_name} vs {opponent_name}")
        self.root.geometry("420x300")
        self.root.configure(bg=_BG)

        header = tk.Frame(self.root, bg=_CARD)
        header.pack(fill=tk.X, pady=12, padx=12)
        tk.Label(header, text=f"Bạn: {player_name}", font=("Helvetica", 12, "bold"), bg=_CARD, fg=_ACCENT).pack(side=tk.LEFT, padx=6)
        tk.Label(header, text=f"Đối thủ: {opponent_name}", font=("Helvetica", 12), bg=_CARD, fg=_TEXT).pack(side=tk.RIGHT, padx=6)

        self.label_status = tk.Label(self.root, text="Chờ lệnh START...", font=("Helvetica", 12), bg=_BG, fg="#9feffb")
        self.label_status.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg=_BG)
        btn_frame.pack(pady=10)

        b_rock = tk.Button(btn_frame, text="ROCK", bg=_NEON_ROCK, fg="#0b0b06", width=10,
                           font=("Helvetica", 10, "bold"), bd=0, activebackground="#ffb070",
                           command=lambda: self.send_move("rock"))
        b_paper = tk.Button(btn_frame, text="PAPER", bg=_NEON_PAPER, fg="#04202a", width=10,
                            font=("Helvetica", 10, "bold"), bd=0, activebackground="#bff7ff",
                            command=lambda: self.send_move("paper"))
        b_scissors = tk.Button(btn_frame, text="SCISSORS", bg=_NEON_SCISSORS, fg="#052205", width=10,
                               font=("Helvetica", 10, "bold"), bd=0, activebackground="#cffecc",
                               command=lambda: self.send_move("scissors"))

        b_rock.pack(side=tk.LEFT, padx=8)
        b_paper.pack(side=tk.LEFT, padx=8)
        b_scissors.pack(side=tk.LEFT, padx=8)

        self.label_result = tk.Label(self.root, text="", font=("Helvetica", 13, "bold"), bg=_BG, fg=_ACCENT)
        self.label_result.pack(pady=12)

        # Music toggle
        self.music_on = False
        self.btn_music = tk.Button(self.root, text="Nhạc: Tắt", width=12, bg="#14202a", fg=_ACCENT, bd=0,
                                   command=self.toggle_music)
        self.btn_music.pack(pady=6)

    def send_move(self, move):
        self.label_status.config(text=f"Đã chọn: {move}", fg="#9feffb")
        try:
            self.on_send_move(move)
        except Exception:
            pass

    def update_result(self, status, my_move, opp_move):
        if status == "win":
            msg = f"Bạn thắng! {my_move} vs {opp_move}"
            color = "#7cff8a"
        elif status == "lose":
            msg = f"Bạn thua! {my_move} vs {opp_move}"
            color = "#ff6b6b"
        else:
            msg = f"Hòa! {my_move} vs {opp_move}"
            color = "#ffd86b"
        self.label_result.config(text=msg, fg=color)

    def toggle_music(self):
        new_state = not self.music_on
        SoundManager.play_music(new_state)
        self.music_on = new_state
        self.btn_music.config(text=("Nhạc: Bật" if self.music_on else "Nhạc: Tắt"))

    def mainloop(self):
        self.root.mainloop()
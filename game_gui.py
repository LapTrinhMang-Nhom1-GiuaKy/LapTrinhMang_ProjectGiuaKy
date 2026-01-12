import tkinter as tk
from tkinter import messagebox
from sound_manager import SoundManager


class GameWindow:
    def __init__(self, player_name, opponent_name, on_send_move, master=None):
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.on_send_move = on_send_move

        # If a master Tk root is provided, create a Toplevel so GUI stays
        # on the main Tk thread; otherwise create a new Tk (fallback).
        if master is not None:
            self.root = tk.Toplevel(master)
        else:
            self.root = tk.Tk()
        self.root.title(f"Bàn chơi - {player_name} vs {opponent_name}")
        self.root.geometry("380x260")

        tk.Label(self.root, text=f"Bạn: {player_name}", font=("Arial", 12, "bold")).pack(pady=4)
        tk.Label(self.root, text=f"Đối thủ: {opponent_name}", font=("Arial", 12)).pack(pady=4)

        self.label_status = tk.Label(self.root, text="Chờ lệnh START...", font=("Arial", 12))
        self.label_status.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        for move, color in [("rock", "orange"), ("paper", "skyblue"), ("scissors", "lightgreen")]:
            tk.Button(btn_frame, text=move.upper(), bg=color, width=10,
                      command=lambda m=move: self.send_move(m)).pack(side=tk.LEFT, padx=5)

        self.label_result = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.label_result.pack(pady=8)

        # Music toggle button
        self.music_on = False
        self.btn_music = tk.Button(self.root, text="Nhạc: Tắt", width=12, command=self.toggle_music)
        self.btn_music.pack(pady=6)

    def send_move(self, move):
        self.label_status.config(text=f"Đã chọn: {move}")
        self.on_send_move(move)

    def update_result(self, status, my_move, opp_move):
        if status == "win":
            msg = f"Bạn thắng! {my_move} vs {opp_move}"
        elif status == "lose":
            msg = f"Bạn thua! {my_move} vs {opp_move}"
        else:
            msg = f"Hòa! {my_move} vs {opp_move}"
        self.label_result.config(text=msg)

    def toggle_music(self):
        # Toggle music and update button text
        new_state = not self.music_on
        SoundManager.play_music(new_state)
        self.music_on = new_state
        self.btn_music.config(text=("Nhạc: Bật" if self.music_on else "Nhạc: Tắt"))

    def mainloop(self):
        self.root.mainloop()
import customtkinter as ctk
from tkinter import messagebox
from sound_manager import SoundManager
from PIL import Image
import os

# Cấu hình giao diện chuẩn
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Bảng màu Theme Neon
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
        self.root.geometry("500x580")
        self.root.configure(fg_color=_BG)

        # --- TỰ ĐỘNG LOAD HÌNH ẢNH ---
        img_path = os.path.join(os.path.dirname(__file__), "assets", "images")
        self.img_size = (100, 100)
        
        def load_icon(name):
            p = os.path.join(img_path, name)
            if os.path.exists(p):
                return ctk.CTkImage(Image.open(p), size=self.img_size)
            return None

        # Tên file ảnh vẫn giữ nguyên như bạn yêu cầu
        self.img_bua = load_icon("rock.png")
        self.img_bao = load_icon("papper.png")
        self.img_keo = load_icon("scissors.png")

        # Header: Thông tin người chơi và điểm số
        header = ctk.CTkFrame(self.root, fg_color=_CARD)
        header.pack(fill="x", pady=15, padx=15)
        
        ctk.CTkLabel(header, text=f"BẠN\n{player_name}", font=("Helvetica", 13, "bold"), text_color=_ACCENT).pack(side="left", padx=20)
        self.label_score = ctk.CTkLabel(header, text="0 - 0", font=("Helvetica", 28, "bold"), text_color="#ffffff")
        self.label_score.pack(side="left", expand=True)
        ctk.CTkLabel(header, text=f"ĐỐI THỦ\n{opponent_name}", font=("Helvetica", 13), text_color=_TEXT).pack(side="right", padx=20)

        self.label_status = ctk.CTkLabel(self.root, text="Đang chờ ván mới...", font=("Helvetica", 14), text_color="#9feffb")
        self.label_status.pack(pady=10)

        # Khung chứa các nút bấm Búa - Bao - Kéo
        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.b_bua = ctk.CTkButton(btn_frame, text="BÚA", image=self.img_bua, compound="top",
                                   command=lambda: self.send_move("bua"), width=140, height=160, 
                                   fg_color=_NEON_ROCK, text_color="#000000", font=("Helvetica", 14, "bold"))
        
        self.b_bao = ctk.CTkButton(btn_frame, text="BAO", image=self.img_bao, compound="top",
                                   command=lambda: self.send_move("bao"), width=140, height=160, 
                                   fg_color=_NEON_PAPER, text_color="#000000", font=("Helvetica", 14, "bold"))
        
        self.b_keo = ctk.CTkButton(btn_frame, text="KÉO", image=self.img_keo, compound="top",
                                   command=lambda: self.send_move("keo"), width=140, height=160, 
                                   fg_color=_NEON_SCISSORS, text_color="#000000", font=("Helvetica", 14, "bold"))

        self.b_bua.grid(row=0, column=0, padx=10)
        self.b_bao.grid(row=0, column=1, padx=10)
        self.b_keo.grid(row=0, column=2, padx=10)

        self.buttons = [self.b_bua, self.b_bao, self.b_keo]
        self.disable_buttons()

        # Hiển thị kết quả ván đấu
        self.label_result = ctk.CTkLabel(self.root, text="", font=("Helvetica", 20, "bold"))
        self.label_result.pack(pady=20)

        # Các nút chức năng phụ
        ctrl_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        ctrl_frame.pack(pady=10)

        self.music_on = False
        self.btn_music = ctk.CTkButton(ctrl_frame, text="Nhạc: Tắt", width=120, fg_color="#14202a", text_color=_ACCENT,
                                       command=self.toggle_music)
        self.btn_music.pack(side="left", padx=10)

        self.btn_exit = ctk.CTkButton(ctrl_frame, text="Thoát Trận", width=120, fg_color="#ff4444", text_color="#ffffff",
                                      command=self.exit_game)
        self.btn_exit.pack(side="left", padx=10)

    def send_move(self, move):
        names = {"bua": "BÚA", "bao": "BAO", "keo": "KÉO"}
        self.label_status.configure(text=f"Bạn đã chọn: {names.get(move)}", text_color=_ACCENT)
        try:
            self.on_send_move(move)
        except Exception:
            pass

    def update_result(self, status, my_move, opp_move, my_score, opp_score):
        names = {"bua": "Búa", "bao": "Bao", "keo": "Kéo", "exit": "Thoát"}
        
        if my_move == "exit":
            msg = "Đối thủ đã thoát, bạn thắng!"
            color = _NEON_SCISSORS
        elif status == "win":
            msg = f"THẮNG 🎉\n({names.get(my_move)} thắng {names.get(opp_move)})"
            color = _NEON_SCISSORS # Màu xanh Neon cho chiến thắng
        elif status == "lose":
            msg = f"THUA 💀\n({names.get(my_move)} thua {names.get(opp_move)})"
            color = "#ff6b6b" # Màu đỏ cho thất bại
        else:
            msg = f"HÒA 🤝\n({names.get(my_move)} vs {names.get(opp_move)})"
            color = "#ffd86b" # Màu vàng cho kết quả hòa
            
        self.label_result.configure(text=msg, text_color=color)
        self.label_score.configure(text=f"{my_score} - {opp_score}")
        self.disable_buttons()

    def toggle_music(self):
        new_state = not self.music_on
        SoundManager.play_music(new_state)
        self.music_on = new_state
        self.btn_music.configure(text=("Nhạc: Bật" if self.music_on else "Nhạc: Tắt"))

    def exit_game(self):
        self.root.destroy()
        try:
            self.on_send_move("EXIT")
        except:
            pass

    def disable_buttons(self):
        for btn in self.buttons:
            btn.configure(state="disabled")

    def enable_buttons(self):
        self.label_result.configure(text="") # Xóa kết quả ván cũ
        for btn in self.buttons:
            btn.configure(state="normal")

    def mainloop(self):
        self.root.mainloop()
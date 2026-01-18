import customtkinter as ctk
from PIL import Image
import os

class GameWindow:
    def __init__(self, player_name, opponent_name, on_send_move, master=None):
        self.root = ctk.CTkToplevel(master) if master else ctk.CTk()
        self.root.title(f"Bàn chơi: {player_name} vs {opponent_name}")
        self.root.geometry("550x580")
        self.root.configure(fg_color="#071020")

        # Load ảnh an toàn
        img_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
        def load(n):
            p = os.path.join(img_dir, n)
            try: return ctk.CTkImage(Image.open(p), size=(100, 100))
            except: return None

        self.img_bua = load("rock.png")
        self.img_bao = load("paper.png")
        self.img_keo = load("scissors.png")

        # UI
        header = ctk.CTkFrame(self.root, fg_color="#0d1624")
        header.pack(fill="x", pady=15, padx=15)
        ctk.CTkLabel(header, text=f"BẠN\n{player_name}", font=("Arial", 13, "bold"), text_color="#00f5ff").pack(side="left", padx=20)
        self.label_score = ctk.CTkLabel(header, text="0 - 0", font=("Arial", 28, "bold"), text_color="#ffffff")
        self.label_score.pack(side="left", expand=True)
        ctk.CTkLabel(header, text=f"ĐỐI THỦ\n{opponent_name}", font=("Arial", 13), text_color="#ffffff").pack(side="right", padx=20)

        self.label_status = ctk.CTkLabel(self.root, text="Chờ đối thủ...", font=("Arial", 14), text_color="#9feffb")
        self.label_status.pack(pady=10)

        btn_f = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_f.pack(pady=20)

        self.b1 = ctk.CTkButton(btn_f, text="BÚA", image=self.img_bua, compound="top", command=lambda: on_send_move("bua"), width=140, height=160, fg_color="#ff8c42")
        self.b2 = ctk.CTkButton(btn_f, text="BAO", image=self.img_bao, compound="top", command=lambda: on_send_move("bao"), width=140, height=160, fg_color="#6ee7ff")
        self.b3 = ctk.CTkButton(btn_f, text="KÉO", image=self.img_keo, compound="top", command=lambda: on_send_move("keo"), width=140, height=160, fg_color="#7cff8a")
        
        self.b1.grid(row=0, column=0, padx=10); self.b2.grid(row=0, column=1, padx=10); self.b3.grid(row=0, column=2, padx=10)
        self.btns = [self.b1, self.b2, self.b3]
        self.disable_buttons()

        self.label_res = ctk.CTkLabel(self.root, text="", font=("Arial", 20, "bold"))
        self.label_res.pack(pady=20)

    def update_result(self, status, my_m, opp_m, my_s, opp_s):
        n = {"bua": "BÚA", "bao": "BAO", "keo": "KÉO", "exit": "Thoát"}
        txt = "THẮNG 🎉" if status == "win" else "THUA 💀" if status == "lose" else "HÒA 🤝"
        clr = "#7cff8a" if status == "win" else "#ff6b6b" if status == "lose" else "#ffd86b"
        self.label_res.configure(text=f"{txt}\n({n.get(my_m)} vs {n.get(opp_m)})", text_color=clr)
        self.label_score.configure(text=f"{my_s} - {opp_s}")

    def enable_buttons(self):
        for b in self.btns: b.configure(state="normal")
        self.label_status.configure(text="MỜI CHỌN!")

    def disable_buttons(self):
        for b in self.btns: b.configure(state="disabled")
        self.label_status.configure(text="Đợi...")
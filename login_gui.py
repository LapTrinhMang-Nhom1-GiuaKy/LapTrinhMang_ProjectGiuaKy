import tkinter as tk
from tkinter import messagebox

# Dark neon theme colors
_BG = "#071020"
_ACCENT = "#00f5ff"
_INPUT_BG = "#0f1724"
_INPUT_FG = "#dffcff"
_BTN_BG = "#00d4ff"
_BTN_FG = "#041017"


class LoginWindow:
    def __init__(self, on_login_callback):
        self.root = tk.Tk()
        self.root.title("Kéo Búa Bao Online - Đăng Nhập")
        self.root.geometry("360x220")
        self.root.configure(bg=_BG)
        self.on_login = on_login_callback

        # Heading
        label = tk.Label(self.root, text="Nhập tên của bạn:", font=("Helvetica", 14, "bold"), bg=_BG, fg=_ACCENT)
        label.pack(pady=(20, 8))

        # Entry (styled)
        self.entry_name = tk.Entry(self.root, font=("Helvetica", 12), bg=_INPUT_BG, fg=_INPUT_FG, insertbackground=_INPUT_FG,
                                   bd=0, relief=tk.FLAT)
        self.entry_name.pack(pady=6, ipady=8, padx=28, fill=tk.X)

        # Login button (neon)
        btn_login = tk.Button(self.root, text="Vào Sảnh Chờ", command=self.start_game,
                              bg=_BTN_BG, fg=_BTN_FG, activebackground="#39faff", bd=0,
                              font=("Helvetica", 12, "bold"))
        btn_login.pack(pady=18)

        # small helper note
        hint = tk.Label(self.root, text="Gõ tên → nhấn 'Vào Sảnh Chờ'", font=("Helvetica", 9), bg=_BG, fg="#7feef7")
        hint.pack()

        self.root.mainloop()

    def start_game(self):
        player_name = self.entry_name.get()
        if player_name.strip() == "":
            messagebox.showwarning("Thông báo", "Vui lòng nhập tên của bạn!")
        else:
            print(f"Bắt đầu game với tên: {player_name}")
            # Gọi callback để kết nối tới server
            # Withdraw main login window and pass its root to client so
            # the Game window can be created as a Toplevel on the main Tk thread.
            self.root.withdraw()
            try:
                self.on_login(player_name, self.root)
            except TypeError:
                # backward compatibility: if callback expects single arg
                self.on_login(player_name)
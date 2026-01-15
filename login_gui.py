import customtkinter as ctk
from tkinter import messagebox

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Dark neon theme colors
_BG = "#071020"
_ACCENT = "#00f5ff"
_INPUT_BG = "#0f1724"
_INPUT_FG = "#dffcff"
_BTN_BG = "#00d4ff"
_BTN_FG = "#041017"


class LoginWindow:
    def __init__(self, on_login_callback):
        self.root = ctk.CTk()
        self.root.title("Kéo Búa Bao Online - Đăng Nhập")
        self.root.geometry("360x220")
        self.root.configure(bg=_BG)
        self.on_login = on_login_callback

        # Heading
        label = ctk.CTkLabel(self.root, text="Nhập tên của bạn:", font=("Helvetica", 14, "bold"), text_color=_ACCENT)
        label.pack(pady=(20, 8))

        # Entry (styled)
        self.entry_name = ctk.CTkEntry(self.root, font=("Helvetica", 12), fg_color=_INPUT_BG, text_color=_INPUT_FG, width=300)
        self.entry_name.pack(pady=6, ipady=8, padx=28)

        # Login button (neon)
        btn_login = ctk.CTkButton(self.root, text="Vào Sảnh Chờ", command=self.start_game,
                                  fg_color=_BTN_BG, text_color=_BTN_FG, hover_color="#39faff",
                                  font=("Helvetica", 12, "bold"))
        btn_login.pack(pady=18)

        # small helper note
        hint = ctk.CTkLabel(self.root, text="Gõ tên → nhấn 'Vào Sảnh Chờ'", font=("Helvetica", 9), text_color="#7feef7")
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
import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, on_login_callback):
        self.root = tk.Tk()
        self.root.title("Kéo Búa Bao Online - Đăng Nhập")
        self.root.geometry("300x200")
        self.on_login = on_login_callback

        # Nhãn hướng dẫn
        label = tk.Label(self.root, text="Nhập tên của bạn:", font=("Arial", 12))
        label.pack(pady=20)

        # Ô nhập tên
        self.entry_name = tk.Entry(self.root, font=("Arial", 12))
        self.entry_name.pack(pady=10)

        # Nút đăng nhập
        btn_login = tk.Button(self.root, text="Vào Sảnh Chờ", command=self.start_game, bg="green", fg="white")
        btn_login.pack(pady=20)

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
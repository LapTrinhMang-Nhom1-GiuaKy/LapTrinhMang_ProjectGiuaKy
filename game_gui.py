import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, on_login_callback):
        self.root = tk.Tk()
        self.root.title("Kéo Búa Bao Online - Đăng Nhập")
        self.root.geometry("350x250")
        self.on_login = on_login_callback

        tk.Label(self.root, text="CHÀO MỪNG BẠN", font=("Arial", 14, "bold")).pack(pady=20)
        self.entry_name = tk.Entry(self.root, font=("Arial", 12))
        self.entry_name.pack(pady=10)

        btn_login = tk.Button(self.root, text="VÀO GAME", bg="green", fg="white", 
                              command=self.handle_login)
        btn_login.pack(pady=20)

    def handle_login(self):
        name = self.entry_name.get().strip()
        if name:
            self.on_login(name)
            self.root.destroy()
        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên!")

    def run(self):
        self.root.mainloop()
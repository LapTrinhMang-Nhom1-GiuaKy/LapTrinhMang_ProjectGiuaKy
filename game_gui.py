import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, on_login_callback):
        self.root = tk.Tk()
        self.root.title("Đăng Nhập")
        self.root.geometry("300x200")
        self.on_login = on_login_callback

        tk.Label(self.root, text="Nhập tên:").pack(pady=10)
        self.entry_name = tk.Entry(self.root)
        self.entry_name.pack(pady=5)

        btn = tk.Button(self.root, text="Vào Game", command=self.handle_login)
        btn.pack(pady=20)

    def handle_login(self):
        name = self.entry_name.get().strip()
        if name:
            self.on_login(name)
            self.root.destroy()
        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên!")

    def run(self):
        self.root.mainloop()
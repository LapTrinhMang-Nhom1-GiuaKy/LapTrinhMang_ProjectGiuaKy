import tkinter as tk
from tkinter import messagebox
class LoginWindow: # <--- Kiểm tra kỹ dòng này, phải là LoginWindow
    def __init__(self, on_login_callback):

def start_game():
    player_name = entry_name.get()
    if player_name.strip() == "":
        messagebox.showwarning("Thông báo", "Vui lòng nhập tên của bạn!")
    else:
        print(f"Bắt đầu game với tên: {player_name}")
        # Ở đây sẽ gọi hàm kết nối tới server.py của bạn
        root.destroy() 

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Kéo Búa Bao Online - Đăng Nhập")
root.geometry("300x200")

# Nhãn hướng dẫn
label = tk.Label(root, text="Nhập tên của bạn:", font=("Arial", 12))
label.pack(pady=20)

# Ô nhập tên
entry_name = tk.Entry(root, font=("Arial", 12))
entry_name.pack(pady=10)

# Nút đăng nhập
btn_login = tk.Button(root, text="Vào Sảnh Chờ", command=start_game, bg="green", fg="white")
btn_login.pack(pady=20)

root.mainloop()
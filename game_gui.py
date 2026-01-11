import tkinter as tk
from tkinter import messagebox

class GameScene:
    def __init__(self, root, send_move_callback):
        self.root = root
        self.root.title("Kéo Búa Bao - Trận Đấu")
        self.root.geometry("400x300")
        self.send_move = send_move_callback # Hàm để gửi dữ liệu về client.py

        tk.Label(root, text="CHỌN NƯỚC ĐI CỦA BẠN", font=("Arial", 14, "bold")).pack(pady=20)

        # Khung chứa 3 nút
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="BÚA (Rock)", width=15, height=3, bg="gray", 
                  command=lambda: self.select_move("rock")).grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="BAO (Paper)", width=15, height=3, bg="white", 
                  command=lambda: self.select_move("paper")).grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="KÉO (Scissors)", width=15, height=3, bg="yellow", 
                  command=lambda: self.select_move("scissors")).grid(row=1, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(root, text="Đang đợi đối thủ...", fg="blue")
        self.status_label.pack(pady=10)

    def select_move(self, move):
        messagebox.showinfo("Thông báo", f"Bạn đã chọn: {move}")
        self.send_move(move) # Gọi hàm gửi về server
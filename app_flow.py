def switch_to_game(current_root, player_name):
    current_root.withdraw() # Ẩn màn hình Login
    new_window = tk.Toplevel()
    # Khởi tạo màn hình Game và truyền logic gửi move vào
    # (Đây là nơi bạn kết nối với socket của client.py)
    print(f"Người chơi {player_name} đã sẵn sàng!")
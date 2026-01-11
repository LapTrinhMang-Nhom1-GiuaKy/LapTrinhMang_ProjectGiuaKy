# client.py
# Client console cho game Oẳn Tù Tì online

import socket
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

def recv_line(sock):
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            return None
        if chunk == b"\n":
            break
        data += chunk
    return data.decode("utf-8", errors="ignore").strip()

def send_line(sock, msg):
    sock.sendall((msg + "\n").encode("utf-8"))

def main():
    host = input(f"Nhập IP server (mặc định {SERVER_HOST}): ").strip() or SERVER_HOST
    port_input = input(f"Nhập port server (mặc định {SERVER_PORT}): ").strip()
    try:
        port = int(port_input) if port_input else SERVER_PORT
    except ValueError:
        print(f"[ERROR] Port không hợp lệ. Sử dụng port mặc định {SERVER_PORT}")
        port = SERVER_PORT

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("[CLIENT] Đã kết nối đến server")
    except (socket.error, OSError) as e:
        print(f"[ERROR] Không thể kết nối đến server {host}:{port}: {e}")
        return

    try:
        # Nhận welcome
        msg = recv_line(sock)
        if not msg:
            print("[CLIENT] Mất kết nối server")
            sock.close()
            return
        print("[SERVER]:", msg)

        # Gửi HELLO
        name = input("Nhập tên của bạn: ").strip() or "Player"
        send_line(sock, f"HELLO {name}")

        while True:
            line = recv_line(sock)
            if not line:
                print("[CLIENT] Mất kết nối server")
                break

            if line.startswith("OK "):
                print("[SERVER]:", line)
            elif line.startswith("ERROR"):
                print("[SERVER]:", line)
                break
            elif line.startswith("START "):
                opponent = line.split(" ", 1)[1]
                print(f"[GAME] Bạn đang chơi với: {opponent}")
            elif line == "PROMPT_MOVE":
                print("[GAME] Chọn nước đi: rock / paper / scissors")
                move = ""
                while move not in ("rock", "paper", "scissors"):
                    move = input(">>> ").strip().lower()
                send_line(sock, f"MOVE {move}")
            elif line.startswith("RESULT "):
                parts = line.split()
                status = parts[1]   # win/lose/draw
                my_move = parts[2]
                opp_move = parts[3]
                print(f"[KẾT QUẢ] Bạn {status}! (Bạn: {my_move}, Đối thủ: {opp_move})")
            elif line == "ASK_PLAY_AGAIN":
                ans = ""
                while ans not in ("yes", "no"):
                    ans = input("Chơi lại? (yes/no): ").strip().lower()
                send_line(sock, f"PLAY_AGAIN {ans}")
                if ans == "no":
                    print("[GAME] Bạn chọn kết thúc trận sau ván này.")
            elif line == "GOODBYE":
                print("[SERVER]: GOODBYE")
                break
            else:
                print("[SERVER RAW]:", line)
    except (socket.error, OSError, BrokenPipeError) as e:
        print(f"[ERROR] Lỗi kết nối: {e}")
    finally:
        sock.close()
        print("[CLIENT] Thoát")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CLIENT] Đã thoát bằng Ctrl+C")
        sys.exit(0)

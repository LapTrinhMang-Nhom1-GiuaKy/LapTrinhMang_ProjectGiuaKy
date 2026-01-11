# server.py
# Server Oẳn Tù Tì nhiều người chơi dùng TCP Socket, mô hình multi client-server

import socket
import threading
from queue import Queue

HOST = "0.0.0.0"
PORT = 8000

# Hàng đợi các người chơi đang chờ
waiting_players = Queue()

clients_lock = threading.Lock()
clients = []  # để quản lý, nếu cần

def decide_winner(move1, move2):
    # move: "rock", "paper", "scissors"
    if move1 == move2:
        return 0
    if (move1 == "rock" and move2 == "scissors") or \
       (move1 == "scissors" and move2 == "paper") or \
       (move1 == "paper" and move2 == "rock"):
        return 1
    return -1

def recv_line(conn):
    """Đọc 1 dòng (kết thúc bằng \n) từ socket"""
    data = b""
    while True:
        chunk = conn.recv(1)
        if not chunk:
            return None
        if chunk == b"\n":
            break
        data += chunk
    return data.decode("utf-8", errors="ignore").strip()

def send_line(conn, msg):
    conn.sendall((msg + "\n").encode("utf-8"))

def handle_match(player1, player2):
    conn1, name1 = player1
    conn2, name2 = player2

    try:
        send_line(conn1, f"START {name2}")
        send_line(conn2, f"START {name1}")

        playing = True
        while playing:
            # Gửi yêu cầu chọn nước đi
            send_line(conn1, "PROMPT_MOVE")
            send_line(conn2, "PROMPT_MOVE")

            # Nhận MOVE từ 2 bên
            line1 = recv_line(conn1)
            line2 = recv_line(conn2)

            if not line1 or not line2:
                break

            # MOVE rock/paper/scissors
            try:
                _, m1 = line1.split(" ", 1)
                _, m2 = line2.split(" ", 1)
            except ValueError:
                break

            result = decide_winner(m1, m2)
            if result == 0:
                send_line(conn1, f"RESULT draw {m1} {m2}")
                send_line(conn2, f"RESULT draw {m2} {m1}")
            elif result == 1:
                send_line(conn1, f"RESULT win {m1} {m2}")
                send_line(conn2, f"RESULT lose {m2} {m1}")
            else:
                send_line(conn1, f"RESULT lose {m1} {m2}")
                send_line(conn2, f"RESULT win {m2} {m1}")

            # Hỏi chơi tiếp
            send_line(conn1, "ASK_PLAY_AGAIN")
            send_line(conn2, "ASK_PLAY_AGAIN")

            ans1 = recv_line(conn1)
            ans2 = recv_line(conn2)

            if not ans1 or not ans2:
                break

            play_again1 = ans1.lower().endswith("yes")
            play_again2 = ans2.lower().endswith("yes")

            if not (play_again1 and play_again2):
                playing = False

        send_line(conn1, "GOODBYE")
        send_line(conn2, "GOODBYE")
    except Exception as e:
        print("[ERROR match]", e)
    finally:
        conn1.close()
        conn2.close()
        print(f"[MATCH] Kết thúc trận giữa {name1} và {name2}")

def client_thread(conn, addr):
    print(f"[KẾT NỐI] {addr}")
    try:
        send_line(conn, "WELCOME Nhap lenh HELLO <ten_cua_ban>")
        line = recv_line(conn)
        if not line or not line.startswith("HELLO "):
            send_line(conn, "ERROR Ban phai gui: HELLO <ten>")
            conn.close()
            return

        name = line.split(" ", 1)[1].strip()
        send_line(conn, f"OK Xin chao {name}. Vui long cho, dang doi nguoi choi khac...")

        with clients_lock:
            clients.append(conn)

        waiting_players.put((conn, name))

    except Exception as e:
        print("[ERROR client_thread]", e)
        conn.close()

def match_maker():
    """Thread ghép cặp người chơi"""
    while True:
        p1 = waiting_players.get()
        p2 = waiting_players.get()
        print(f"[MATCH] Ghép {p1[1]} vs {p2[1]}")
        t = threading.Thread(target=handle_match, args=(p1, p2), daemon=True)
        t.start()

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    # Thread chuyên ghép cặp
    threading.Thread(target=match_maker, daemon=True).start()

    while True:
        conn, addr = server_sock.accept()
        t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    main()

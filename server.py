import socket
import threading
import time
from queue import Queue, Empty

HOST = "0.0.0.0"
PORT = 8000
clients = {}
clients_lock = threading.Lock()

def decide_winner(move1, move2):
    if move1 == move2: return 0
    wins = [("bua", "keo"), ("keo", "bao"), ("bao", "bua")]
    return 1 if (move1, move2) in wins else -1

def recv_line(conn):
    data = b""
    while True:
        try:
            chunk = conn.recv(1)
            if not chunk: return None
            if chunk == b"\n": break
            data += chunk
        except: return None
    return data.decode("utf-8", errors="ignore").strip()

def send_line(conn, msg):
    try: conn.sendall((msg + "\n").encode("utf-8"))
    except: pass

def broadcast_lobby():
    lobby_data = []
    with clients_lock:
        for c, info in clients.items():
            lobby_data.append(f"{info['name']}:{info['status']}")
    msg = "LOBBY_UPDATE " + ",".join(lobby_data)
    with clients_lock:
        for conn in list(clients.keys()):
            send_line(conn, msg)

def find_client_by_name(name):
    with clients_lock:
        for conn, info in clients.items():
            if info['name'] == name: return conn, info
    return None, None

def handle_match(conn1, name1, conn2, name2):
    with clients_lock:
        q1, q2 = clients[conn1]["queue"], clients[conn2]["queue"]
    try:
        send_line(conn1, f"START {name2}")
        send_line(conn2, f"START {name1}")
        playing, score1, score2 = True, 0, 0
        while playing:
            send_line(conn1, "PROMPT_MOVE"); send_line(conn2, "PROMPT_MOVE")
            m1, m2 = None, None
            while m1 is None or m2 is None:
                try:
                    while not q1.empty():
                        d = q1.get_nowait()
                        if d in ["EXIT", "MOVE EXIT"]: playing = False; raise Exception()
                        if d.startswith("MOVE "): m1 = d
                except Empty: pass
                try:
                    while not q2.empty():
                        d = q2.get_nowait()
                        if d in ["EXIT", "MOVE EXIT"]: playing = False; raise Exception()
                        if d.startswith("MOVE "): m2 = d
                except Empty: pass
                if not playing: break
                time.sleep(0.1)
            mv1, mv2 = m1.split()[1], m2.split()[1]
            res = decide_winner(mv1, mv2)
            if res == 0:
                send_line(conn1, f"RESULT draw {mv1} {mv2} {score1} {score2}")
                send_line(conn2, f"RESULT draw {mv2} {mv1} {score2} {score1}")
            elif res == 1:
                score1 += 1
                send_line(conn1, f"RESULT win {mv1} {mv2} {score1} {score2}")
                send_line(conn2, f"RESULT lose {mv2} {mv1} {score2} {score1}")
            else:
                score2 += 1
                send_line(conn1, f"RESULT lose {mv1} {mv2} {score1} {score2}")
                send_line(conn2, f"RESULT win {mv2} {mv1} {score2} {score1}")
            send_line(conn1, "ASK_PLAY_AGAIN"); send_line(conn2, "ASK_PLAY_AGAIN")
    except: pass
    finally:
        send_line(conn1, "GOODBYE"); send_line(conn2, "GOODBYE")
        with clients_lock:
            if conn1 in clients: clients[conn1]["status"] = "IDLE"
            if conn2 in clients: clients[conn2]["status"] = "IDLE"
        broadcast_lobby()

def client_thread(conn, addr):
    try:
        send_line(conn, "WELCOME")
        line = recv_line(conn)
        if not line or not line.startswith("HELLO "): return
        name = line.split(" ", 1)[1].strip()
        with clients_lock: clients[conn] = {"name": name, "status": "IDLE", "queue": Queue()}
        broadcast_lobby()
        while True:
            line = recv_line(conn)
            if line is None: break
            with clients_lock:
                if conn in clients and clients[conn]["status"] == "BUSY":
                    clients[conn]["queue"].put(line); continue
            if line.startswith("INVITE "):
                t_n = line.split(" ", 1)[1]
                t_c, _ = find_client_by_name(t_n)
                if t_c: send_line(t_c, f"INVITE_REQ {name}")
            elif line.startswith("INVITE_RESP "):
                p = line.split()
                s_n, ans = p[1], p[2]
                s_c, _ = find_client_by_name(s_n)
                if s_c and ans == "YES":
                    with clients_lock:
                        clients[conn]["status"] = "BUSY"
                        clients[s_c]["status"] = "BUSY"
                    broadcast_lobby()
                    threading.Thread(target=handle_match, args=(s_c, s_n, conn, name), daemon=True).start()
    finally:
        with clients_lock:
            if conn in clients: del clients[conn]
        broadcast_lobby(); conn.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT)); s.listen(); print("Server running...")
    while True:
        c, a = s.accept()
        threading.Thread(target=client_thread, args=(c, a), daemon=True).start()
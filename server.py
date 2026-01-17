# server.py
# Server Oẳn Tù Tì nhiều người chơi dùng TCP Socket, mô hình Lobby & Invite
# UPDATE: Router Pattern to fix race conditions

import socket
import threading
import json
import time
from queue import Queue, Empty

HOST = "0.0.0.0"
PORT = 8000

# Quản lý clients connected
# Format: 
# { 
#   conn: {
#       "name": "ABC", 
#       "status": "IDLE" | "BUSY", 
#       "queue": Queue()  # Data queue for Game Loop
#   } 
# }
clients = {}
clients_lock = threading.Lock()

def decide_winner(move1, move2):
    if move1 == move2: return 0
    if (move1 == "rock" and move2 == "scissors") or \
       (move1 == "scissors" and move2 == "paper") or \
       (move1 == "paper" and move2 == "rock"):
        return 1
    return -1

def recv_line(conn):
    """Đọc 1 dòng (kết thúc bằng \n) từ socket"""
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
    try:
        conn.sendall((msg + "\n").encode("utf-8"))
    except:
        pass

def get_lobby_list():
    lobby_data = []
    with clients_lock:
        for c, info in clients.items():
            lobby_data.append(f"{info['name']}:{info['status']}")
    return ",".join(lobby_data)

def broadcast_lobby():
    msg = "LOBBY_UPDATE " + get_lobby_list()
    with clients_lock:
        dead = []
        for conn in clients:
            try:
                send_line(conn, msg)
            except:
                dead.append(conn)
        for d in dead:
             if d in clients: del clients[d]

def find_client_by_name(name):
    with clients_lock:
        for conn, info in clients.items():
            if info['name'] == name:
                return conn, info
    return None, None

def handle_match(conn1, name1, conn2, name2):
    """Xử lý Logic Game - KHÔNG ĐỌC SOCKET TRỰC TIẾP"""
    print(f"[MATCH] Start: {name1} vs {name2}")
    
    score1 = 0
    score2 = 0
    
    # Get Queues
    with clients_lock:
        if conn1 not in clients or conn2 not in clients:
            return
        q1 = clients[conn1]["queue"]
        q2 = clients[conn2]["queue"]

    try:
        send_line(conn1, f"START {name2}")
        send_line(conn2, f"START {name1}")

        playing = True
        while playing:
            send_line(conn1, "PROMPT_MOVE")
            send_line(conn2, "PROMPT_MOVE")

            m1 = None
            m2 = None

            # --- WAIT FOR MOVES ---
            while m1 is None or m2 is None:
                # Check Q1
                try:
                    while not q1.empty():
                        data = q1.get_nowait()
                        if data == "EXIT" or data == "MOVE EXIT":
                            score2 += 1
                            send_line(conn2, f"RESULT win exit exit {score2} {score1}")
                            playing = False; raise Exception("EXIT_P1")
                        elif data is None: # Disconnect
                            raise Exception("DISCONNECT_P1")
                        elif data.startswith("MOVE "):
                            m1 = data
                except Empty: pass

                # Check Q2
                try:
                    while not q2.empty():
                        data = q2.get_nowait()
                        if data == "EXIT" or data == "MOVE EXIT":
                            score1 += 1
                            send_line(conn1, f"RESULT win exit exit {score1} {score2}")
                            playing = False; raise Exception("EXIT_P2")
                        elif data is None:
                             raise Exception("DISCONNECT_P2")
                        elif data.startswith("MOVE "):
                            m2 = data
                except Empty: pass

                if not playing: break
                time.sleep(0.05)

            if not playing: break

            # Process Moves
            mv1 = m1.split(" ", 1)[1]
            mv2 = m2.split(" ", 1)[1]
            
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

            # Ask Play Again
            send_line(conn1, "ASK_PLAY_AGAIN")
            send_line(conn2, "ASK_PLAY_AGAIN")

            # Wait for confirm
            ack1 = False
            ack2 = False
            start_w = time.time()
            while not (ack1 and ack2):
                if time.time() - start_w > 5: break # Timeout
                
                try:
                    while not q1.empty():
                        d = q1.get_nowait()
                        if d and "YES" in d: ack1 = True
                        elif d == "EXIT" or d == "MOVE EXIT": playing = False; raise Exception("EXIT_P1")
                        elif d is None: raise Exception("DISCONNECT_P1")
                    while not q2.empty():
                        d = q2.get_nowait()
                        if d and "YES" in d: ack2 = True
                        elif d == "EXIT" or d == "MOVE EXIT": playing = False; raise Exception("EXIT_P2")
                        elif d is None: raise Exception("DISCONNECT_P2")
                except: pass
                
                if not playing: break
                time.sleep(0.05)

    except Exception as e:
        print(f"[MATCH END] {e}")
    finally:
        send_line(conn1, "GOODBYE")
        send_line(conn2, "GOODBYE")
        
        with clients_lock:
            # Clear queues just in case
            while not q1.empty(): q1.get()
            while not q2.empty(): q2.get()
            
            if conn1 in clients: clients[conn1]["status"] = "IDLE"
            if conn2 in clients: clients[conn2]["status"] = "IDLE"
            
        broadcast_lobby()


def client_thread(conn, addr):
    print(f"[CONN] {addr}")
    name = ""
    try:
        send_line(conn, "WELCOME Nhap lenh HELLO <ten_cua_ban>")
        line = recv_line(conn)
        if not line or not line.startswith("HELLO "):
            send_line(conn, "ERROR Syntax")
            conn.close()
            return
        
        name = line.split(" ", 1)[1].strip()
        
        with clients_lock:
            clients[conn] = {
                "name": name, 
                "status": "IDLE", 
                "queue": Queue()
            }
        
        print(f"[LOGIN] {name}")
        send_line(conn, f"OK Welcome {name}")
        broadcast_lobby()

        # --- ROUTER LOOP ---
        while True:
            line = recv_line(conn) # Blocking read
            
            # Check disconnection
            if line is None:
                # Notify Game Loop if busy
                with clients_lock:
                    if conn in clients and clients[conn]["status"] == "BUSY":
                        clients[conn]["queue"].put(None)
                break
            
            # ROUTING
            status = "IDLE"
            with clients_lock:
                if conn in clients:
                    status = clients[conn]["status"]
            
            if status == "BUSY":
                # Forward to Game Loop
                with clients_lock:
                    if conn in clients:
                        clients[conn]["queue"].put(line)
            else:
                # Handle Lobby Commands
                if line.startswith("INVITE "):
                    t_name = line.split(" ", 1)[1]
                    if t_name == name: continue
                    
                    t_conn, t_info = find_client_by_name(t_name)
                    if t_conn and t_info["status"] == "IDLE":
                        send_line(t_conn, f"INVITE_REQ {name}")
                    else:
                        send_line(conn, f"ERROR {t_name} busy or offline")
                        
                elif line.startswith("INVITE_RESP "):
                    # INVITE_RESP <sender> <YES/NO>
                    parts = line.split()
                    if len(parts) >= 3:
                        sender = parts[1]
                        ans = parts[2]
                        s_conn, s_info = find_client_by_name(sender)
                        if s_conn:
                            if ans == "NO":
                                send_line(s_conn, f"INVITE_REJECT {name}")
                            elif ans == "YES" and s_info["status"] == "IDLE":
                                # START GAME
                                with clients_lock:
                                    clients[conn]["status"] = "BUSY"
                                    clients[s_conn]["status"] = "BUSY"
                                broadcast_lobby()
                                threading.Thread(target=handle_match, args=(s_conn, sender, conn, name), daemon=True).start()
                            else:
                                send_line(conn, "ERROR Too late")

    except Exception as e:
        print(f"[ERR] {name} {e}")
    finally:
        with clients_lock:
            if conn in clients: del clients[conn]
        broadcast_lobby()
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on {PORT}")
    
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()
        except: break

if __name__ == "__main__":
    main()

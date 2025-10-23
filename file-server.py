import socket
import threading
import os
import pathlib

HOST = "0.0.0.0"
PORT = 5001
BASE_DIR = pathlib.Path("/home/bigpoppa").resolve()


#helps the header to receive metadata
def recv_until(sock, delimiter=b"\n", max_bytes=8192):
    buf = bytearray()
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buf += chunk
        if len(buf) > max_bytes:
            raise ValueError("Header too large")
        if delimiter in buf:
            line, _, rest = buf.partition(delimiter)
            return line.decode("utf-8", errors="strict")
    raise ConnectionError("Connection closed before header received")


def client_handler(connection, address):
    print(f"{address} connected!")
    try:
        connection.sendall(b"where would you like to put the file? please include file metadata\n")
        dirs = [p.name for p in BASE_DIR.iterdir() if p.is_dir()]
        connection.sendall(("Dirs: " + ", ".join(dirs) + "\n").encode("utf-8"))
        #list directory
        with connection:
            while True:
                #gets header
                header = connection.recv_until(connection, b"\n")
                parts = [part.strip() for part in header.split('|')]
                #checks format
                if len(parts) !=3:
                    connection.sendall(b"ERR invalid header format\n")
                    return
                name, rel_dir, r_bytes = parts
                
                # makes sure there is actually a file being sent
                try:
                    remaining = int(r_bytes)
                    if remaining < 0:
                        raise ValueError
                except ValueError:
                    connection.sendall(b"ERR invalid size\n")
                    return
                
                #checks for correct file name
                if "/" in name or "\\" in name or not name:
                    connection.sendall(b"ERR invalid filename\n")
                    return
                #makes sure file location is valid and allowed
                dest_dir = (BASE_DIR / rel_dir).resolve() if rel_dir else BASE_DIR
                if not str(dest_dir).startswith(str(BASE_DIR)):
                    connection.sendall(b"ERR path outside base dir\n")
                    return
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = dest_dir / name
                
                connection.sendall(b"OK send file bytes now\n")
                
                
                with open(dest_path, "wb") as f:
                    while remaining > 0:
                        data = connection.recv(min(65536, remaining))
                        if not data:
                            connection.sendall(b"ERR connection closed early\n")
                            break
                        
                        f.write(data)
                        remaining -=len(data)
                connection.sendall(b"OK file received\n")
    except Exception as e:
        print(f"Handler error from {address}: {e}")
        try:
            connection.sendall(b"ERR server error\n")
        except Exception:
            pass
        
    finally:    
        print(f"{address} disconnected!")
    
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST,PORT))
        s.listen()
        print(f"file server listening on {HOST}:{PORT}")
        while True:
            connection,address = s.accept()
            threading.Thread(
                target=client_handler, args=(connection, address), daemon=True
            ).start()
            
if __name__ == "__main__":
    main()
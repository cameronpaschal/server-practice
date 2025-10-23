import socket
import sys
import os
from os.path import getsize,basename, expanduser

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 file-client.py <SERVER_IP_OR_NAME> [PORT] <filepath>")
        sys.exit(1)
        
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    
    file = expanduser(sys.argv[3])
    if not os.path.isfile(file):
        print(f"File not found: {file}")
        sys.exit(1)
        
    
    file_name = basename(file)
    
    file_size = getsize(file)
    
    
    
    with socket.create_connection((host, port), timeout=10) as s:
        
        try: 
            data = s.recv(4080)
            if data:
                
                print(data.decode("utf-8", errors="replace"), end="")
                print()
        except socket.timeout:
            pass
        try: 
            data = s.recv(4080)
            if data:
                
                print(data.decode("utf-8", errors="replace"), end="")
        except socket.timeout:
            pass
        dest_dir = input("> Destination directory on server, relative please (eg. photos)").strip()
        
        header = f"{file_name}|{dest_dir}|{file_size}\n"
        print(header)
        s.sendall(header.encode("utf-8"))
        
        response = s.recv(1024).decode("utf-8", errors="replace").strip()
        print(response)
        if not response.startswith("OK"):
            print("Server did not accept header; aborting.")
            return
        
        with open(file, "rb") as f:
            s.sendfile(f)
        
        final = s.recv(1024).decode("utf-8", errors="replace").strip()
        print(final)
        
        
if __name__ == "__main__":
    main()
        
        
            
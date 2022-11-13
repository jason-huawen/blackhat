import socket
import sys
import threading


class MyTCPProxy:
    def __init__(self) -> None:
        if len(sys.argv) < 5:
            print("Usage: ./%s local_ip local_port remote_ip remote_port" % sys.argv[0])
            sys.exit()
        self.local_ip = sys.argv[1]
        self.local_port = int(sys.argv[2])
        self.remote_ip = sys.argv[3]
        self.remote_port = int(sys.argv[4])
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.local_ip, self.local_port))
        self.server_socket.listen(5)
        self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote_socket.connect((self.remote_ip, self.remote_port))
    
    def proxy_handler(self,local_client_socket, local_client_addr):
        print("[+] Connected from: %s" % str(local_client_addr[0]))
        
        while True:
            buffer = b''
            while True:
                data = local_client_socket.recv(4096)
                if not data:
                    break
                buffer += data
            print(buffer)
            
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_socket,self.remote_port))
            remote_socket.send(buffer)
            remote_buffer = b''
            while True:
                remote_data = remote_socket.recv(4096)
                if not remote_data:
                    break
                remote_buffer += remote_data
            local_client_socket.send(remote_buffer)

    def run(self):
        while True:
            local_client_socket, local_client_addr = self.server_socket.accept()
            t = threading.Thread(target=self.proxy_handler, args=(local_client_socket, local_client_addr))
            t.start()

if __name__ == '__main__':
    proxy = MyTCPProxy()
    proxy.run()
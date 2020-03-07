#!/usr/bin/env python3

import socket
from eggshell import EggShell


class WsServer:
    def __init__(self, eggshell):
        self.host = '0.0.0.0'
        self.port = 5000
        self.eggshell = eggshell

    def __run__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(2)
        conn, addr = s.accept()
        if conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd_line = data.decode()
                cmd = cmd_line.split()
                if len(cmd) < 2:
                    continue
                else:
                    session_id, para = cmd[0], cmd[1]
                    session_id = int(session_id)
                    print(session_id, ": ", para)
        conn.sendall(b'bye')
        conn.close()


if __name__ == "__main__":
    eggshell = EggShell()
    eggshell.start_multi_handler()

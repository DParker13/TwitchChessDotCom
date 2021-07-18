import socket
from emoji import demojize

class TwitchController:

    def __init__(self):
        self.sock = socket.socket()
        self.chat = []
        self.queue_max = 100

        server = 'irc.chat.twitch.tv'
        port = 6667
        nickname = 'xonor1'
        token = 'oauth:vh1sroxs3ldryi0uj38zxwyl2v0az9'
        self.channel = '#shroud'

        self.Create_Socket(server, port, nickname, token, self.channel)

    def Create_Socket(self, server, port, token, nickname, channel):
        self.sock.connect((server, port))
        self.sock.send(f"PASS {token}\n".encode('utf-8'))
        self.sock.send(f"NICK {nickname}\n".encode('utf-8'))
        self.sock.send(f"JOIN {channel}\n".encode('utf-8'))

    def Run_Twitch_IRC(self):
        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            elif len(resp) > 0:
                print(demojize(resp).partition(self.channel + " :")[2])

    def Get_Latest_Chat(self):
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            elif len(resp) > 0:
                msg = demojize(resp).partition(self.channel + " :")[2]
                if len(self.chat) >= self.queue_max:
                    self.chat = []

                self.chat.append(msg)
                print(msg)

import socket
from emoji import demojize


class TwitchController:

    def __init__(self):
        self.sock = socket.socket()
        self.ALL_MOVES = self.Create_All_Moves()
        self.promotion_commands = ["promote b", "promote n", "promote q", "promote r", "undo"]

        server = 'irc.chat.twitch.tv'
        port = 6667
        nickname = 'xonor1'
        token = 'oauth:vclhm14dwtpgt31gglp2kenechnvb0'
        self.channel = '#xonor1'

        self.Create_Socket(server, port, nickname, token)

    def Create_Socket(self, server, port, nickname, token):
        print("Creating Socket...")
        self.sock.connect((server, port))
        self.sock.send(f"PASS {token}\n".encode('utf-8'))
        self.sock.send(f"NICK {nickname}\n".encode('utf-8'))
        self.sock.send(f"JOIN {self.channel}\n".encode('utf-8'))
        print("Socket Created - Listening to chat:", self.channel)

    def Run(self, current_turn, mode):
        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            elif len(resp) > 0:
                formatted_chat = demojize(resp).partition(self.channel + " :")[2]
                print(formatted_chat)
                self.Compile_Chat(current_turn, mode, formatted_chat.lower().strip())

    @staticmethod
    def Create_All_Moves():
        all_moves = []

        for row in range(1, 9):
            for col in range(97, 105):
                all_moves.append(chr(col) + str(row))

        return all_moves

    def Compile_Chat(self, current_turn, mode, current_chat_msg):
        move_count = 0
        user_moves = []

        # Main Loop
        if mode.value == 0:
            for move in self.ALL_MOVES:
                # Looks for current move in chat msg and excludes and duplicates
                if move in current_chat_msg != -1 and current_chat_msg.count(move) == 1:
                    move_count += 1
                    if move_count <= 2:
                        # Adds each move to a list with its index to make sure the moves are ordered correctly later on
                        user_moves.append((move, current_chat_msg.index(move)))

            if move_count == 2:
                # Checks if the index of the first move is larger than the second move (means they're out of order)
                if user_moves[0][1] > user_moves[1][1]:
                    user_moves_ordered = str(user_moves[1][0] + " " + user_moves[0][0])
                else:
                    user_moves_ordered = str(user_moves[0][0] + " " + user_moves[1][0])

                # Counts the current move with all others in dictionary
                if user_moves_ordered in current_turn:
                    current_turn[user_moves_ordered] += 1
                else:
                    current_turn[user_moves_ordered] = 1
        # Promotion Loop
        elif mode.value == 1:
            for command in self.promotion_commands:
                if command == current_chat_msg and command != "undo":
                    if command in current_turn != -1:
                        current_turn[command[-1]] += 1
                    else:
                        current_turn[command[-1]] = 1
                if command == current_chat_msg and command == "undo":
                    if command in current_turn != -1:
                        current_turn[command] += 1
                    else:
                        current_turn[command] = 1

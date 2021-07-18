import pyautogui
import time
import TwitchController


class GUIController:

    def __init__(self, top_left_coords=[376, 193], test_mode=False):
        self.SCREEN_SIZE = pyautogui.size()
        self.CHESS_TILE_SIZE = 100  # size of each tile on chessboard in pixels
        self.CHESS_BOARD_SIZE = [800, 800]  # size of the whole chess board for overlay approximation
        self.TOP_LEFT_COORDS = top_left_coords  # coordinates of the top left corner of the chess board
        self.chess_board = {}  # center coordinates of each tile with its associated board name
        self.PIECES = ['K', 'Q', 'R', 'B', 'N', 'P']
        self.piece_locations = {'P1': [0, 0], 'P2': [100, 0], 'P3': [200, 0], 'P4': [300, 0],
                                'P5': [400, 0], 'P6': [500, 0], 'P7': [600, 0], 'P8': [700, 0],
                                'R1': [0, 100], 'N1': [100, 100], 'B1': [200, 100], 'Q': [300, 100], 'K': [400, 100],
                                'B2': [500, 100], 'N2': [600, 100], 'R2': [700, 100]}

        self.Setup_Chess_Board(test_mode)

        pyautogui.PAUSE = 0.05

    def Setup_Chess_Board(self, test_mode=False):
        y = self.TOP_LEFT_COORDS[1] + self.CHESS_BOARD_SIZE[1] - (self.CHESS_TILE_SIZE / 2)

        for col in range(1, 9):
            x = self.TOP_LEFT_COORDS[0] + (self.CHESS_TILE_SIZE / 2)

            for row in range(97, 105):
                tile_name = chr(row) + str(col)

                # sets each tile_name with its appropriate coordinates
                self.chess_board[tile_name] = [x, y]

                if test_mode:
                    print(tile_name + str([x, y]))
                    pyautogui.moveTo(x, y)

                x += self.CHESS_TILE_SIZE

            y -= self.CHESS_TILE_SIZE

    def Move_Piece(self, chat_input):
        # checks for correct input
        if 0 < len(chat_input) <= 5:
            move = chat_input.split(" ")

            if len(move) == 2 and move[0] in self.chess_board and move[1] in self.chess_board:
                pyautogui.mouseDown(self.chess_board[move[0]][0], self.chess_board[move[0]][1], button="left")
                pyautogui.moveTo(self.chess_board[move[1]][0], self.chess_board[move[1]][1])
                pyautogui.mouseUp(self.chess_board[move[1]][0], self.chess_board[move[1]][1], button="left")
                # print(move[0], self.chess_board[move[0]][0], move[1], self.chess_board[move[1]][1])
            else:
                print("FAILED")

    def Pawn_Promotion(self):
        return None


# tc = TwitchController.TwitchController()
time.sleep(5)
GUIController([376, 193]).Move_Piece("d2 d4")

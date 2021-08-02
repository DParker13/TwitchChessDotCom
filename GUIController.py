import pyautogui
import time
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import TwitchController


class GUIController:

    def __init__(self, top_left_coords=[376, 193], test_mode=False, puzzle_mode=False):
        # puzzle top left coords for testing: [312, 143]
        # puzzle tile size: 114

        self.SCREEN_SIZE = pyautogui.size()
        # size of each tile on chessboard in pixels
        self.CHESS_TILE_SIZE = 100
        # size of the whole chess board for overlay approximation
        self.CHESS_BOARD_SIZE = [self.CHESS_TILE_SIZE * 8, self.CHESS_TILE_SIZE * 8]
        # coordinates of the top left corner of the chess board
        self.TOP_LEFT_COORDS = top_left_coords
        # center coordinates of each tile with its associated board name
        self.chess_board = {}
        self.PIECES = ['K', 'Q', 'R', 'B', 'N', 'P']
        self.COLS = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
        self.DRIVER = self.Create_Browser_Session()
        '''
        DEPRECATED
        self.piece_locations = {'P1': [0, 0], 'P2': [100, 0], 'P3': [200, 0], 'P4': [300, 0],
                                'P5': [400, 0], 'P6': [500, 0], 'P7': [600, 0], 'P8': [700, 0],
                                'R1': [0, 100], 'N1': [100, 100], 'B1': [200, 100], 'Q': [300, 100], 'K': [400, 100],
                                'B2': [500, 100], 'N2': [600, 100], 'R2': [700, 100]}
        '''
        self.white_pieces, self.black_pieces = self.Update_Piece_Locations()

        if puzzle_mode:
            self.TOP_LEFT_COORDS = [312, 143]
            self.CHESS_TILE_SIZE = 114
            self.CHESS_BOARD_SIZE = [self.CHESS_TILE_SIZE * 8, self.CHESS_TILE_SIZE * 8]

        self.Setup_Chess_Board(test_mode)

        pyautogui.PAUSE = 0.05

    def Create_Browser_Session(self):
        driver = webdriver.Firefox()

        # runs the browser session
        driver.get("https://www.chess.com/play/computer")

        # closes opening popup
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[7]/div/div/button"))).click()

        return driver

    def Update_Piece_Locations(self):
        white_pieces = []
        black_pieces = []
        # possible_moves = dict()

        # makes a list of all the pieces on the board
        pieces = WebDriverWait(self.DRIVER, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="board-vs-personalities"]/div')))

        for piece in pieces:

            # grabs all white pieces
            if piece.get_attribute("class").find("piece w") != -1:
                white_pieces.append(piece)

            # grabs all black pieces
            if piece.get_attribute("class").find("piece b") != -1:
                black_pieces.append(piece)

                '''
                (THIS WON'T WORK, TRY SOMETHING ELSE)
                Grabs all possible moves a piece can make
                Adds piece to dictionary as key
                
                try:
                    piece.click()
                    moves = (self.DRIVER.find_elements_by_css_selector('[data-test-element="hint"]'))
                    for move in moves:
                        location = self.Format_Location(move)
                        print("    " + location[0] + location[1])
                except exceptions.NoSuchElementException:
                    possible_moves[piece] = None
                '''

        return white_pieces, black_pieces

    def Move_Piece(self, selected_piece, move_to):
        action_chains = ActionChains(self.DRIVER)

        piece = self.Find_Piece(selected_piece)

        if piece is not None:
            piece.click()
            try:
                possible_moves = (self.DRIVER.find_elements_by_css_selector('[data-test-element="hint"]'))

                for move in possible_moves:
                    if self.Unformat_Location(move_to) in move.get_attribute('class'):
                        action_chains.drag_and_drop(piece, move).perform()

            except exceptions.NoSuchElementException:
                print("No moves exist")

    def Find_Piece(self, location):

        # gets updated piece locations
        self.Update_Piece_Locations()
        location = self.Unformat_Location(location)

        for piece in self.white_pieces:
            if location in piece.get_attribute('class'):
                return piece

        for piece in self.black_pieces:
            if location in piece.get_attribute('class'):
                return piece

        print("Failed to find piece: " + location)
        return None


    def Format_Location(self, piece):
        col = self.COLS[int(piece.get_attribute("class")[-2:-1])]
        row = piece.get_attribute("class")[-1:]

        return [col, row]

    def Unformat_Location(self, location):
        col = list(self.COLS.keys())[list(self.COLS.values()).index(location[0])]
        row = location[1]

        return str(col) + str(row)

    # ----- DEPRECATED CODE -----

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

    def Move_Piece_Old(self, chat_input):
        # checks for correct input
        if 0 < len(chat_input) <= 5:
            moves = chat_input.split(" ")

            if len(moves) == 2 and moves[0] in self.chess_board and moves[1] in self.chess_board:
                pyautogui.mouseDown(self.chess_board[moves[0]][0], self.chess_board[moves[0]][1], button="left")
                pyautogui.moveTo(self.chess_board[moves[1]][0], self.chess_board[moves[1]][1])
                pyautogui.mouseUp(self.chess_board[moves[1]][0], self.chess_board[moves[1]][1], button="left")

                # checks for pawn promotion chance
                if self.chess_board[moves[1]][1] == self.chess_board["a8"][1]:
                    self.Pawn_Promotion(moves, promotion_input="q")

            else:
                print("FAILED")

    def Pawn_Promotion(self, moves, promotion_input):
        print("Possible pawn promotion!")

        # OPTIONS
        # turn on overlay with new commands to chose promotion
        # randomly choose promotion if no one does
        # ask chat if pawn was promoted
        # assumes chat knows pawn is being promoted, initiates search in chat for new promotion commands

        if (promotion_input.lower() == "promote q"
                or promotion_input.lower() == "promote queen"
                or promotion_input.lower() == "q"):
            pyautogui.click(x=self.chess_board[moves[1]][0], y=self.chess_board[moves[1]][1], button="left")
            print(self.chess_board[moves[1]][0], self.chess_board[moves[1]][1])
        elif (promotion_input.lower() == "promote n"
              or promotion_input.lower() == "promote knight"
              or promotion_input.lower() == "n"):
            pyautogui.click(x=self.chess_board[moves[1]][0],
                            y=self.chess_board[moves[1]][1] + self.CHESS_TILE_SIZE, button="left")
        elif (promotion_input.lower() == "promote r"
              or promotion_input.lower() == "promote rook"
              or promotion_input.lower() == "r"):
            pyautogui.click(x=self.chess_board[moves[1]][0],
                            y=self.chess_board[moves[1]][1] + 2 * self.CHESS_TILE_SIZE, button="left")
        elif (promotion_input.lower() == "promote b"
              or promotion_input.lower() == "promote bishop"
              or promotion_input.lower() == "b"):
            pyautogui.click(x=self.chess_board[moves[1]][0],
                            y=self.chess_board[moves[1]][1] + 3 * self.CHESS_TILE_SIZE, button="left")


# tc = TwitchController.TwitchController()
# time.sleep(5)
# GUIController([376, 193], False, True).Move_Piece("h7 h8")
controller = GUIController()
controller.Move_Piece("e2", "e5")

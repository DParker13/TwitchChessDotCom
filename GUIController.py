import time
import operator
from multiprocessing import Process, Manager
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


class GUIController:

    def __init__(self):
        self.COLS = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
        self.DRIVER = self.Create_Browser_Session()
        self.white_pieces = []
        self.black_pieces = []
        self.wait_time = 5
        self.max_promotion_attempts = 5

    def Run(self, current_turn, mode):
        # main program loop
        while True:
            # waits n seconds for twitch user input
            time.sleep(self.wait_time)

            print("\nCompiling Votes!")
            user_selected_move = self.Get_Most_Voted_Move(current_turn)

            if user_selected_move is not None:
                user_selected_move = user_selected_move.split(" ")
                print("Attempting to move piece")
                successful_move = self.Move_Piece(user_selected_move[0], user_selected_move[1], current_turn, mode)
                if successful_move:
                    print("Moved", user_selected_move[0], "to", user_selected_move[1], "\n")
                else:
                    print("Move", user_selected_move[0], "to", user_selected_move[1], "was unsuccessful\n")
                    for piece in self.white_pieces:
                        print(piece.get_attribute('class'))
            else:
                print("No moves entered\n")

    @staticmethod
    def Create_Browser_Session():
        profile = webdriver.FirefoxProfile(r"C:\Users\danie\AppData\Roaming\Mozilla\Firefox\Profiles\t2kc6i54.Default User")
        driver = webdriver.Firefox(profile)

        # runs the browser session
        driver.get("https://www.chess.com/play/computer")

        # closes opening popup
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[2]/div[7]/div/div/button"))).click()
        except exceptions.TimeoutException:
            print("Opening popup likely not found: Timeout Exception")

        return driver

    def Update_Piece_Locations(self):
        white_pieces = []
        black_pieces = []

        # makes a list of all the pieces on the board
        coordinates = self.DRIVER.find_element_by_class_name("coordinates")
        board_menu = coordinates.find_element_by_xpath("..")
        pieces = board_menu.find_elements_by_tag_name("div")

        for piece in pieces:
            # grabs all white pieces
            if piece.get_attribute("class").find("piece w") != -1:
                white_pieces.append(piece)

            # grabs all black pieces
            if piece.get_attribute("class").find("piece b") != -1:
                black_pieces.append(piece)

        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

    def Move_Piece(self, selected_piece, move_to, current_turn, mode):
        action_chains = ActionChains(self.DRIVER)

        piece = self.Find_Piece(selected_piece)

        if piece is not None:
            piece.click()
            try:
                possible_moves = (self.DRIVER.find_elements_by_css_selector('[data-test-element="hint"]'))

                for move in possible_moves:
                    if self.Unformat_Location(move_to) in move.get_attribute('class'):
                        action_chains.drag_and_drop(piece, move).perform()
                        self.Check_Game_Over()
                        self.Check_Pawn_Promotion(current_turn, mode)
                        print("Completed")
                        return True
                return False

            except (exceptions.NoSuchElementException, exceptions.StaleElementReferenceException) as e:
                print("Exception Raised:", e)
                return False

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

    def Check_Pawn_Promotion(self, current_turn, mode):
        try:
            promotion_menu = self.DRIVER.find_element_by_css_selector(".promotion-window")
            x_button = promotion_menu.find_element_by_tag_name("i")
            promotions = promotion_menu.find_elements_by_tag_name("div")

            if len(promotions) > 0:
                self.Enter_Promotion_Mode(promotions, x_button, current_turn, mode)
        except (exceptions.TimeoutException, exceptions.NoSuchElementException) as e:
            print("No pawn promotion:", e)

    def Check_Game_Over(self):
        return None

    def Enter_Promotion_Mode(self, promotions, x_button, current_turn, mode):
        mode.value = 1
        for attempt in range(self.max_promotion_attempts):
            print("    Promotion Attempt:", attempt+1)
            time.sleep(self.wait_time)

            user_selected_promotion = self.Get_Most_Voted_Move(current_turn)

            # Presses X button when undo is selected
            if user_selected_promotion == "undo":
                print("    Undo Promotion Selected by Chat")
                try:
                    x_button.click()
                except exceptions.ElementNotInteractableException:
                    print("Failed to click x button")
                mode.value = 0
                break
            if user_selected_promotion is not None:
                self.Promote_Pawn(promotions, user_selected_promotion)
                mode.value = 0
                return

        # Presses X button when promotion fails
        try:
            x_button.click()
        except exceptions.ElementNotInteractableException:
            print("Failed to click x button")

        mode.value = 0

    @staticmethod
    def Promote_Pawn(promotions, user_selection):
        for promotion in promotions:
            if promotion.get_attribute('class')[-1] == user_selection:
                promotion.click()
                return
        print("Failed to click promotion")

    @staticmethod
    def Get_Most_Voted_Move(current_turn):
        try:
            max_key = max(current_turn.items(), key=operator.itemgetter(1))[0]
            print(max_key, current_turn[max_key])

            # clears the dictionary for next turn
            current_turn.clear()

            return max_key
        except ValueError as e:
            return None

from multiprocessing import Manager
from threading import Thread
from GUIController import GUIController
from TwitchController import TwitchController

if __name__ == '__main__':
    # Creates a shared queue between processes
    d = Manager().dict()

    # 0 - Main Loop
    # 1 - Promotion Loop
    mode = Manager().Value("i", 0)

    # Create new processes
    print("Starting GUI Controller...")
    process1 = Thread(target=GUIController().Run, args=(d, mode,))

    print("Starting Twitch Controller...")
    process2 = Thread(target=TwitchController().Run, args=(d, mode,))

    # Start new Processes
    process1.start()
    print("GUI Controller Started")
    process2.start()
    print("Twitch Controller Started")

    print("Exiting Main Thread")

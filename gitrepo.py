from gui import GUI
from logger import Logger

if __name__ == "__main__":
    Logger.write_log("Program started")
    app = GUI()
    app.mainloop()
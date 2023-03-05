import sys
from PyQt5.QtWidgets import QApplication
from gui import NoiserWindow

def main():
    """Runs the Noisr singleton instance"""

    App     = QApplication(sys.argv)
    Noiser  = NoiserWindow()
    Noiser.show()

    sys.exit(App.exec_())

if  __name__ == '__main__':
    main()
import sys
import os
from pathlib import Path

from GUI import GUI

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFile, QTextStream, Qt


class MainWindow(QMainWindow):
    def __init__(self, in_dir, out_dir):
        super().__init__()

        self.gui = GUI(in_dir, out_dir)
        self.setCentralWidget(self.gui)
        
        self.setGeometry(200, 100, 960, 540)
        self.setWindowTitle("Labeler")
        
        
def main():
    os.chdir(Path(__file__).parent)
    
    # enable high dpi scaling
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)

    
    # set stylesheet
    file = QFile("./assets/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    
    default_in = Path('..\imgs\in')
    default_out = Path('..\imgs\out')
    default_in.mkdir(parents=True, exist_ok=True)
    default_out.mkdir(parents=True, exist_ok=True)

    window = MainWindow(in_dir=default_in, out_dir=default_out)
    window.setWindowTitle('Segmentation Labeler')
    window.show()
    
    sys.exit(app.exec_())
    
    
    
    
    
if __name__ == '__main__':
    main()
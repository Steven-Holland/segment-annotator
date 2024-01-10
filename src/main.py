import sys
import os
from pathlib import Path

from GUI import GUI

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFile, QTextStream


class MainWindow(QMainWindow):
    def __init__(self, in_dir, out_dir):
        super().__init__()

        self.gui = GUI(in_dir, out_dir)
        self.setCentralWidget(self.gui)
        
        self.setGeometry(200, 100, 960, 540)
        self.setWindowTitle("Labeler")
        
        
def main():
    os.chdir(Path(__file__).parent)
    
    app = QApplication(sys.argv)
    
    # set stylesheet
    file = QFile("./assets/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    
    window = MainWindow(in_dir=Path('..\imgs\in'), out_dir=Path('..\imgs\out'))
    window.setWindowTitle('Segmentation Labeler')
    window.show()
    
    sys.exit(app.exec_())
    
    
    
    
    
if __name__ == '__main__':
    main()
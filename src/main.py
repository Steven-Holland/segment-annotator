import sys
import os
from pathlib import Path

from GUI import GUI
from config import CONFIG_PATH
from utils import write_config_file, read_config_file

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFile, QTextStream, Qt, QSize


class MainWindow(QMainWindow):
    def __init__(self, window_size, in_dir, out_dir):
        super().__init__()

        self.gui = GUI(in_dir, out_dir)
        self.setCentralWidget(self.gui)
        
        self.setGeometry(0, 0, *window_size)
        
        
def main():
    os.chdir(Path(__file__).parent)
    
    # enable high dpi scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    
    # set stylesheet
    file = QFile("./assets/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    
    if not Path.exists(CONFIG_PATH):
        in_dir = Path('..\imgs\in')
        out_dir = Path('..\imgs\out')
        in_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        ret = write_config_file({})
        ret &= write_config_file(str(in_dir), setting_name='input_folder')
        ret &= write_config_file(str(out_dir), setting_name='output_folder')
        if not ret: 
            print('Failed to initialize config file!')
    else:
        in_dir = Path(read_config_file('input_folder'))
        out_dir = Path(read_config_file('output_folder'))
    
    window = MainWindow((rect.width(), rect.height()), in_dir=in_dir, out_dir=out_dir)
    window.setWindowTitle('Segmentation Labeler')
    window.showMaximized()
    
    sys.exit(app.exec_())
    
    
    
    
    
if __name__ == '__main__':
    main()
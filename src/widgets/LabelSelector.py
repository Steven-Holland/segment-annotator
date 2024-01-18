from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize, QUrl
from PyQt5.QtGui import QColor, QIcon
from utils import set_attr, read_config_file, write_config_file

_icons_path = Path(__file__).parent.parent / 'assets/icons'

class LabelCheckBox(QCheckBox):
    def __init__(self, label, color, val):
        super().__init__()
        
        self.label = label
        self.color = color
        self.value = val
        
        self.initUI()
    
    def __call__(self):
        return {'label': self.label, 'color': self.color, 'value': self.value}

    def initUI(self):
        self.setText(f'{self.value} - {self.label}')
        self.setStyleSheet(f'''QCheckBox::indicator {{ 
                           background-color: {self.color}}};
                           font-size: 16pt;''')
        
        # url = QUrl().fromLocalFile(str(_icons_path / "checked.png"))
        # self.setStyleSheet(f'''QCheckBox::indicator:checked {{ 
        #                    image: url(:/assets/icons/checked.png); }}''')


class NewLabelBox(QWidget):
    label_ready = pyqtSignal(str, str)
    cancel = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        
        self.text_label = QLabel('Label Name:')
        self.text_field = QLineEdit()
        self.color_field = QColorDialog()
        self.color_indicator = QLabel('           ')
        self.add_btn = QPushButton('Add')
        self.cancel_btn = QPushButton('Cancel')
        
        self.color = '#ffffff'
        
        self.initUI()
        
    def initUI(self):
        self.top_layout.addWidget(self.text_label)
        self.top_layout.addWidget(self.text_field)
        self.color_indicator.setStyleSheet(f'background-color: {self.color}')
        self.top_layout.addWidget(self.color_indicator)
        self.top_layout.addWidget(self.add_btn)
        self.top_layout.addWidget(self.cancel_btn)
        
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.color_field)
        
        self.setLayout(self.main_layout)
        
        self.color_field.colorSelected.connect(self.set_color)
        self.add_btn.clicked.connect(self.ready)
        self.cancel_btn.clicked.connect(lambda: self.cancel.emit())
        
    def open(self):
        self.setHidden(False)
        self.color_field.open()
        
    def close(self):
        self.setHidden(True)
        self.color = '#ffffff'
        self.color_field.setCurrentColor(QColor(self.color))
        self.color_indicator.setStyleSheet(f'background-color: {self.color}')
        self.text_field.setText('')

    @pyqtSlot()
    def set_color(self):
        self.color = self.color_field.currentColor().name() # hex
        self.color_indicator.setStyleSheet(f'background-color: {self.color}')
        
    @pyqtSlot()
    def ready(self):
        label = self.text_field.text()
        if self.color and label:
            self.label_ready.emit(label, self.color)
        


# enforces mutual exclusion for checkboxes
class LabelSelector(QFrame):
    label_changed = pyqtSignal(dict)

    def __init__(self, title):
        super().__init__()
        
        self.main_layout = QVBoxLayout()
        self.header_layout = QHBoxLayout()
        self.title = QLabel(title)
        self.delete_btn = QPushButton()
        self.new_label_btn = QPushButton('New Label')
        self.new_label_box = NewLabelBox()
        self.labels = {}

        self.label_count = 0
        self.creating_label = False

        self.initUI()
        self.load_labels()
        
    def initUI(self):
        
        self.header_layout.addWidget(self.title)
        icon = QIcon(str(_icons_path / 'delete_button.png'))
        self.delete_btn.setIcon(icon)
        self.delete_btn.setFixedSize(self.delete_btn.iconSize() + QSize(10, 10))
        self.header_layout.addWidget(self.delete_btn)
        self.main_layout.addLayout(self.header_layout)
        self.new_label_box.setHidden(True)
        self.main_layout.addWidget(self.new_label_box)
        self.new_label_btn.setFixedWidth(150)
        self.main_layout.addWidget(self.new_label_btn)
        
        self.setLayout(self.main_layout)
        self.setObjectName('frame')
        text = f'#{self.objectName()} {{ border: 1px solid white; }}'
        self.setStyleSheet(text)
        
        self.new_label_btn.clicked.connect(self.new_label)
        self.new_label_box.cancel.connect(self.close_prompt)
        self.new_label_box.label_ready.connect(self.add_label)
        self.delete_btn.clicked.connect(self.remove_label)
    
    def load_labels(self):
        self.labels = read_config_file('labels')        
        for label, color in self.labels.items():
            self.add_label(label, color)
    
    def add_label(self, label, color):
        self.labels[label] = color
        self.label_count += 1

        checkbox = set_attr(self, label+'_btn', LabelCheckBox(label, color, self.label_count))
        self.main_layout.insertWidget(self.main_layout.count() - 1, checkbox)
        checkbox.clicked.connect(self.receive_check)
        
        self.close_prompt()
        write_config_file(self.labels, setting_name='labels')

    def remove_label(self):
        curr_label = self.activate_label()
        checkbox = getattr(self, curr_label+'_btn')
        self.main_layout.removeWidget(checkbox)
        checkbox.deleteLater()

        del self.labels[curr_label]
        self.label_count -= 1
        write_config_file(self.labels, setting_name='labels')
        
    def activate_label(self):
        for label, color in self.labels.items():
            checkbox = getattr(self, label+'_btn')
            if checkbox.isChecked(): return label
        return None
        
    @pyqtSlot()
    def receive_check(self):
        for label, color in self.labels.items():
            checkbox = getattr(self, label+'_btn')
            if checkbox is self.sender(): 
                self.label_changed.emit(checkbox())
                continue
            checkbox.setChecked(False)
    
    @pyqtSlot()
    def new_label(self):
        if self.creating_label: return
        self.creating_label = True
        self.new_label_box.open()
    
    def close_prompt(self):
        self.new_label_box.close()
        self.creating_label = False
        
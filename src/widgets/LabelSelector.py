from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from utils import set_attr
from PyQt5 import sip


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
        self.setStyleSheet(f'''QCheckBox::indicator {{ background-color: {self.color} }};
                           font-size: 14pt;''')
        #checkbox.setStyleSheet('QCheckBox::indicator:checked { image: url(:/../assets/checked.png); }')


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
        self.add_btn = QPushButton('Add')
        self.cancel_btn = QPushButton('Cancel')
        
        self.color = None
        
        self.initUI()
        
    def initUI(self):
        self.top_layout.addWidget(self.text_label)
        self.top_layout.addWidget(self.text_field)
        self.top_layout.addWidget(self.add_btn)
        self.top_layout.addWidget(self.cancel_btn)
        
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.color_field)
        
        self.setLayout(self.main_layout)
        
        self.color_field.colorSelected.connect(self.set_color)
        self.add_btn.clicked.connect(self.ready)
        self.cancel_btn.clicked.connect(lambda: self.cancel.emit())

    @pyqtSlot()
    def set_color(self):
        self.color = self.color_field.currentColor().name() # hex
        
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
        self.title = QLabel(title)
        self.new_label_btn = QPushButton('New Label')
        self.new_label_box = NewLabelBox()
        self.labels = []
        
        self.creating_label = False
        self.num_labels = 0

        self.initUI()
        
    def initUI(self):
        
        self.main_layout.addWidget(self.title)
        self.new_label_box.setHidden(True)
        self.main_layout.addWidget(self.new_label_box)
        self.main_layout.addWidget(self.new_label_btn)
        
        self.setLayout(self.main_layout)
        self.setObjectName('frame')
        text = f'#{self.objectName()} {{ border: 1px solid white; }}'
        self.setStyleSheet(text)
        
        self.new_label_btn.clicked.connect(self.new_label)
        self.new_label_box.cancel.connect(self.close_prompt)
        self.new_label_box.label_ready.connect(self.addLabel)
    
    
    def addLabel(self, label, color):
        self.num_labels += 1
        self.labels.append(label)
        
        checkbox = set_attr(self, label+'_btn', LabelCheckBox(label, color, self.num_labels))
        self.main_layout.insertWidget(self.main_layout.count() - 1, checkbox)
        checkbox.clicked.connect(self.receive_check)
        
        self.close_prompt()
        
    def activate_label(self):
        for label in self.labels:
            checkbox = getattr(self, label+'_btn')
            if checkbox.isActivate(): return label
        return None
        
    @pyqtSlot()
    def receive_check(self):
        #print('Sender:', self.sender())
        for i, label in enumerate(self.labels):
            checkbox = getattr(self, label+'_btn')
            if checkbox is self.sender(): 
                self.label_changed.emit(checkbox())
                continue
            checkbox.setChecked(False)
    
    @pyqtSlot()
    def new_label(self):
        if self.creating_label: return
        self.creating_label = True
        self.new_label_box.setHidden(False)
    
    def close_prompt(self):
        self.new_label_box.setHidden(True)
        self.creating_label = False
        
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox

class ListItem(QWidget):
    def __init__(self, text, options):
        super().__init__()
        self.options = list(options)
        self.initUI(text, self.options)

    def initUI(self, text, options):
        layout = QVBoxLayout()

        label = QLabel(text)
        self.combobox = QComboBox()
        for option in options:
            self.combobox.addItem(option[1])
 
        layout.addWidget(label)
        layout.addWidget(self.combobox)

        self.setLayout(layout)

    def getCurrentIndex(self):
        # Get the current value of the combobox
        return self.combobox.currentIndex()
    
    def getCurrentId(self):
        # Get the current value of the combobox
        return self.options[self.getCurrentIndex()][0]
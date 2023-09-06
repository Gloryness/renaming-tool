from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor
from PyQt5.QtWidgets import QDialog, QSizePolicy, QGridLayout, QLabel, QPushButton, QSpacerItem, QScrollArea, QWidget, QPlainTextEdit

class ButtonAdd(QPushButton):
    def __init__(self, episode_number, type_, parent):
        super().__init__(parent)
        self.win = parent
        self.episode_number = episode_number
        self.type = type_

        self.clicked.connect(self.onClick)

    def onClick(self):
        self.win.obj['result'] = (self.episode_number, self.type)
        self.win.close()


class ButtonRemove(QPushButton):
    def __init__(self, episode_number, parent):
        super().__init__(parent)
        self.win = parent
        self.episode_number = episode_number

        self.clicked.connect(self.onClick)

    def onClick(self):
        self.win.obj['result'] = self.episode_number
        self.win.close()

class AddEpisodeDialog(QDialog):
    def __init__(self, obj, episode_count, parent=None):
        super().__init__(parent)

        self.setModal(True)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.obj = obj
        self.episodes = episode_count

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Add Episode Slot")
        self.resize(350, 125)

        self.gridLayout_2 = QGridLayout(self)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setVerticalSpacing(2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer, 999, 0, 1, 1)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        for i in range(1, self.episodes + 1):
            setattr(self, f'label_{i}', QLabel(self))
            label = getattr(self, f'label_{i}')

            palette4 = QPalette()
            brush4 = QBrush(QColor(98, 118, 188, 255))
            brush4.setStyle(Qt.SolidPattern)
            palette4.setBrush(QPalette.Active, QPalette.WindowText, brush4)
            palette4.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
            label.setPalette(palette4)
            font5 = QFont()
            font5.setPointSize(10)
            font5.setBold(True)
            font5.setWeight(75)
            label.setFont(font5)
            label.setText(f"{i}")
            self.gridLayout.addWidget(label, i - 1, 0, 1, 1)

            setattr(self, f'insert_before_{i}', ButtonAdd(i, 'before', self))
            button_1 = getattr(self, f'insert_before_{i}')
            button_1.setText("INSERT BEFORE")
            sizePolicy.setHeightForWidth(button_1.sizePolicy().hasHeightForWidth())
            button_1.setSizePolicy(sizePolicy)
            self.gridLayout.addWidget(button_1, i - 1, 1, 1, 1)

            setattr(self, f'insert_after_{i}', ButtonAdd(i, 'after', self))
            button_2 = getattr(self, f'insert_after_{i}')
            button_2.setText("INSERT AFTER")
            sizePolicy.setHeightForWidth(button_2.sizePolicy().hasHeightForWidth())
            button_2.setSizePolicy(sizePolicy)
            self.gridLayout.addWidget(button_2, i - 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

class RemoveEpisodeDialog(QDialog):
    def __init__(self, obj, episode_count, parent=None):
        super().__init__(parent)

        self.setModal(True)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.obj = obj
        self.episodes = episode_count

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Remove Episode Slot")
        self.resize(810, 208)

        self.gridLayout_2 = QGridLayout(self)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer, 999, 0, 1, 1)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        for i in range(1, self.episodes + 1):
            setattr(self, f'label_{i}', QLabel(self))
            label = getattr(self, f'label_{i}')

            palette4 = QPalette()
            brush4 = QBrush(QColor(98, 118, 188, 255))
            brush4.setStyle(Qt.SolidPattern)
            palette4.setBrush(QPalette.Active, QPalette.WindowText, brush4)
            palette4.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
            label.setPalette(palette4)
            font5 = QFont()
            font5.setPointSize(12)
            font5.setBold(True)
            font5.setWeight(75)
            label.setFont(font5)
            label.setText(f"{i}")
            self.gridLayout.addWidget(label, i - 1, 0, 1, 1)

            setattr(self, f'remove_{i}', ButtonRemove(i, self))
            button = getattr(self, f'remove_{i}')
            button.setText("REMOVE")
            sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
            button.setSizePolicy(sizePolicy)
            self.gridLayout.addWidget(button, i - 1, 1, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

class CompletionDialog(QDialog):
    def __init__(self, renamed, description, parent=None):
        super().__init__(parent)

        self.renamed = renamed
        self.description = description

        self.setModal(True)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.setupUi()

        self.label.setText(f"Successfully renamed {self.renamed} file{'s' if self.renamed != 1 else ''}.")
        self.plainTextEdit.setPlainText(self.description)

    def setupUi(self):
        self.setWindowTitle("Operation completed")
        self.setMinimumSize(500, 350)

        self.gridLayout = QGridLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 380, 261))
        self.gridLayout_2 = QGridLayout(self.scrollAreaWidgetContents)
        self.plainTextEdit = QPlainTextEdit(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.plainTextEdit, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)

        self.label = QLabel(self)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
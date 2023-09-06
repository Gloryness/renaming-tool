from PyQt5.QtCore import QMetaObject, QRect, Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor, QPainter
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QFormLayout, QWidget, QTabWidget, QGridLayout, QLabel, QScrollArea, QMessageBox, QSpinBox, QFileDialog, \
    QHBoxLayout, QLineEdit, QPushButton, QToolButton, QSpacerItem, QApplication, QRadioButton, QVBoxLayout, QStyle, QStyleOption, QFrame, QSplitter, QCheckBox
from dialog import AddEpisodeDialog, RemoveEpisodeDialog, CompletionDialog
from bs4 import BeautifulSoup
import requests
import sys
import re
import os

def chunk(iterable, n):
    """
    Yield n-sized chunks from iterable.
    """
    for chunk in range(0, len(iterable), n):
        yield iterable[chunk:chunk+n]

class SearchWikipedia(QLineEdit):
    def __init__(self, win, parent):
        super().__init__(parent)
        self.win = win

    def keyPressEvent(self, event):
        if event != "":
            QLineEdit.keyPressEvent(self, event)

        key = event.key()
        if key in [Qt.Key_Return, Qt.Key_Enter]:
            self.win.ui.wikipedia_search_button.click()

class ThisOneButton(QPushButton):
    def __init__(self, win, parent):
        super().__init__(parent)
        self.win = win

        self.clicked.connect(lambda: self.win.its_this_one(parent))

class CustomWidget(QWidget):
    def __init__(self, win, parent):
        super().__init__(parent)
        self.win = win

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def mousePressEvent(self, a0):
        QWidget.mousePressEvent(self, a0)

        self.win.its_this_one(self)

class CustomCheckBox(QCheckBox):
    def __init__(self, win, file, parent):
        super().__init__(parent)
        self.win = win

        self.setStyleSheet("QCheckBox{spacing:3px}")
        self.setTristate(True)

        if file in self.win.excluded:
            self.setCheckState(self.win.excluded[file])
        else:
            self.setCheckState(2)

        self.stateChanged.connect(self.changed)

    def changed(self, state):
        black_palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        black_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        black_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)

        red_palette = QPalette()
        brush = QBrush(QColor(135, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        red_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        red_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)

        if state == 2:
            self.setPalette(black_palette)
            if self.text() in self.win.excluded:
                del self.win.excluded[self.text()]
        else:
            self.setPalette(red_palette)
            self.win.excluded[self.text()] = state

        self.win.load_filenames(self.win.ui.folder_location.text())

class WindowUI:
    def __init__(self, main_window: QMainWindow):
        self.win = main_window

    def setupUi(self):
        self.win.setWindowTitle("Batch Renaming Tool for TV Series'")
        self.win.resize(930, 550)
        self.centralwidget = QWidget(self.win)
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setStyleSheet(
            "QTabBar::tab {width: 0; height: 0; margin: 0; padding: 0; border: none;}\n"
            "QTabBar::tab:selected {background: #f0f0f0;}\n"
            "QTabWidget>QWidget>QWidget{background: #f0f0f0;}"
        )
        self.tab = QWidget()
        self.formLayout = QFormLayout(self.tab)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.nextButton = QPushButton(self.tab)
        self.nextButton.setCursor(Qt.PointingHandCursor)
        sizePolicy = sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        palette = QPalette()
        brush = brush2 = QBrush(QColor(46, 89, 158))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush = QBrush(QColor(120, 120, 120))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        self.nextButton.setPalette(palette)
        font = font1 = QFont()
        font.setFamily("Arial Black")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.nextButton.setFont(font)
        self.horizontalLayout.addWidget(self.nextButton)
        self.formLayout.setLayout(4, QFormLayout.SpanningRole, self.horizontalLayout)
        self.gridLayout = QGridLayout()
        self.radioButton_2 = QRadioButton(self.tab)
        self.radioButton_2.setChecked(True)
        self.gridLayout.addWidget(self.radioButton_2, 1, 0, 1, 1)
        self.radioButton = QRadioButton(self.tab)
        self.gridLayout.addWidget(self.radioButton, 0, 0, 1, 1)
        self.search_wikipedia = SearchWikipedia(self.win, self.tab)
        self.gridLayout.addWidget(self.search_wikipedia, 1, 1, 1, 1)
        self.wikipedia_search_button = QPushButton(self.tab)
        self.gridLayout.addWidget(self.wikipedia_search_button, 1, 2, 1, 1)
        self.wikipedia_url = QLineEdit(self.tab)
        self.gridLayout.addWidget(self.wikipedia_url, 0, 1, 1, 2)
        self.formLayout.setLayout(1, QFormLayout.SpanningRole, self.gridLayout)
        self.label = QLabel(self.tab)
        font = QFont()
        font.setFamily("Rockwell")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.label)


        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 851, 414))
        self.formLayout_2 = QFormLayout(self.scrollAreaWidgetContents)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.scrollArea)

        brush1 = QBrush(QColor(120, 120, 120, 255))
        brush1.setStyle(Qt.SolidPattern)

        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QWidget()

        self.gridLayout_5 = QGridLayout(self.tab_2)
        self.label_2 = QLabel(self.tab_2)
        self.label_2.setFont(font)

        self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 2)

        self.attention = QLabel(self.tab_2)
        palette7 = QPalette()
        brush4 = QBrush(QColor(135, 0, 0, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette7.setBrush(QPalette.Active, QPalette.WindowText, brush4)
        palette7.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
        self.attention.setPalette(palette7)

        self.gridLayout_5.addWidget(self.attention, 1, 0, 1, 2)

        self.scrollArea_2 = QScrollArea(self.tab_2)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 424, 471))
        self.formLayout_3 = QFormLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_7 = QHBoxLayout()
        self.filename_formatting_label = QLabel(self.scrollAreaWidgetContents_2)
        font2 = QFont()
        font2.setPointSize(10)
        self.filename_formatting_label.setFont(font2)

        self.horizontalLayout_7.addWidget(self.filename_formatting_label)

        self.filename_format = QLineEdit(self.scrollAreaWidgetContents_2)
        self.filename_format.setFont(font2)
        self.filename_format.setStyleSheet("QLineEdit{background-color:rgb(0, 0, 0, 0); border-bottom: 1px solid rgb(33, 138, 154); border-radius: 2px; padding: 1px}\n"
                                           "QLineEdit::hover{ border-bottom: 1px solid rgb(223, 145, 255);}")
        self.filename_format.setFrame(False)

        self.horizontalLayout_7.addWidget(self.filename_format)

        self.formLayout_3.setLayout(1, QFormLayout.SpanningRole, self.horizontalLayout_7)

        self.horizontalLayout_5 = QHBoxLayout()
        self.season_label = QLabel(self.scrollAreaWidgetContents_2)
        self.season_label.setFont(font2)

        self.horizontalLayout_5.addWidget(self.season_label)

        self.season_number = QSpinBox(self.scrollAreaWidgetContents_2)
        self.season_number.setMinimum(1)

        self.horizontalLayout_5.addWidget(self.season_number)

        self.formLayout_3.setLayout(0, QFormLayout.SpanningRole, self.horizontalLayout_5)

        self.gridLayout_6 = QGridLayout()
        self.filename_format_label = QLabel(self.scrollAreaWidgetContents_2)
        font4 = QFont()
        font4.setFamily("Nirmala UI")
        font4.setPointSize(20)
        font4.setBold(False)
        font4.setWeight(50)
        self.filename_format_label.setFont(font4)

        self.gridLayout_6.addWidget(self.filename_format_label, 0, 2, 1, 1)

        self.episodes_label = QLabel(self.scrollAreaWidgetContents_2)
        self.episodes_label.setFont(font4)

        self.gridLayout_6.addWidget(self.episodes_label, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.addButton = QPushButton(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_6.addWidget(self.addButton)

        self.removeButton = QPushButton(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_6.addWidget(self.removeButton)

        self.gridLayout_6.addLayout(self.horizontalLayout_6, 5, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_3, 0, 1, 1, 1)

        self.formLayout_3.setLayout(3, QFormLayout.SpanningRole, self.gridLayout_6)

        self.scrollArea_4 = QScrollArea(self.scrollAreaWidgetContents_2)
        self.scrollArea_4.setFrameShape(QFrame.NoFrame)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 406, 264))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 999, 2, 1, 1)

        brush4 = QBrush(QColor(98, 118, 188, 255))
        brush4.setStyle(Qt.SolidPattern)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)

        self.formLayout_3.setWidget(4, QFormLayout.SpanningRole, self.scrollArea_4)

        self.formatGrid = QGridLayout()
        self.formatGrid.setSpacing(8)
        self.formatGrid.setContentsMargins(-1, 6, -1, 6)
        self.format_help_6 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_6.setStyleSheet("border:1px solid green")

        self.formatGrid.addWidget(self.format_help_6, 2, 1, 1, 1)

        self.format_help_5 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_5.setStyleSheet("border:1px solid black")

        self.formatGrid.addWidget(self.format_help_5, 1, 1, 1, 1)

        self.format_help_4 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_4.setStyleSheet("border:1px solid black")

        self.formatGrid.addWidget(self.format_help_4, 0, 1, 1, 1)

        self.format_help_1 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_1.setStyleSheet("border:1px solid black")

        self.formatGrid.addWidget(self.format_help_1, 0, 0, 1, 1)

        self.format_help_3 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_3.setStyleSheet("border:1px solid black")

        self.formatGrid.addWidget(self.format_help_3, 2, 0, 1, 1)

        self.format_help_2 = QLabel(self.scrollAreaWidgetContents_2)
        self.format_help_2.setStyleSheet("border:1px solid black")

        self.formatGrid.addWidget(self.format_help_2, 1, 0, 1, 1)

        self.formLayout_3.setLayout(2, QFormLayout.SpanningRole, self.formatGrid)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_5.addWidget(self.scrollArea_2, 2, 0, 1, 1)

        self.scrollArea_3 = QScrollArea(self.tab_2)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 425, 471))
        self.formLayout_4 = QFormLayout(self.scrollAreaWidgetContents_3)
        self.folder_location_vertical = QVBoxLayout()
        self.folder_location_horizontal = QHBoxLayout()
        self.folder_location_label = QLabel(self.scrollAreaWidgetContents_3)
        self.folder_location_label.setFont(font2)

        self.folder_location_horizontal.addWidget(self.folder_location_label)

        self.folder_location = QLineEdit(self.scrollAreaWidgetContents_3)

        self.folder_location_horizontal.addWidget(self.folder_location)

        self.folder_location_button = QToolButton(self.scrollAreaWidgetContents_3)

        self.folder_location_horizontal.addWidget(self.folder_location_button)

        self.folder_location_vertical.addLayout(self.folder_location_horizontal)

        self.folder_location_description = QLabel(self.scrollAreaWidgetContents_3)
        palette6 = QPalette()
        palette6.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette6.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette6.setBrush(QPalette.Disabled, QPalette.WindowText, brush1)
        self.folder_location_description.setPalette(palette6)

        self.folder_location_vertical.addWidget(self.folder_location_description)

        self.formLayout_4.setLayout(0, QFormLayout.SpanningRole, self.folder_location_vertical)

        self.gridLayout_7 = QGridLayout()
        self.filename_label = QLabel(self.scrollAreaWidgetContents_3)
        self.filename_label.setFont(font4)

        self.gridLayout_7.addWidget(self.filename_label, 0, 0, 1, 1)

        self.new_filename_label = QLabel(self.scrollAreaWidgetContents_3)
        self.new_filename_label.setFont(font4)

        self.gridLayout_7.addWidget(self.new_filename_label, 0, 2, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_4, 0, 1, 1, 1)

        self.formLayout_4.setLayout(1, QFormLayout.SpanningRole, self.gridLayout_7)

        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)

        self.splitter = QSplitter(self.scrollAreaWidgetContents_3)
        self.splitter.setStyleSheet("QSplitter::handle{background-color: black}")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        sizePolicy4.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy4)

        self.scrollArea_5 = QScrollArea(self.splitter)
        self.scrollArea_5.setFrameShape(QFrame.NoFrame)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollArea_5.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sizePolicy4.setHeightForWidth(self.scrollArea_5.sizePolicy().hasHeightForWidth())
        self.scrollArea_5.setSizePolicy(sizePolicy4)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 201, 359))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents_5)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_5.insertSpacerItem(999, self.verticalSpacer_2)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_5)
        self.splitter.addWidget(self.scrollArea_5)

        self.scrollArea_6 = QScrollArea(self.splitter)
        self.scrollArea_6.setFrameShape(QFrame.NoFrame)
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollArea_6.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.scrollArea_6.sizePolicy().hasHeightForWidth())
        self.scrollArea_5.setSizePolicy(sizePolicy4)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 201, 359))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents_6)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.insertSpacerItem(999, self.verticalSpacer_3)

        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_6)
        self.splitter.addWidget(self.scrollArea_6)

        self.formLayout_4.setWidget(2, QFormLayout.SpanningRole, self.splitter)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout_5.addWidget(self.scrollArea_3, 2, 1, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.backButton = QPushButton(self.tab_2)
        sizePolicy3.setHeightForWidth(self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy3)
        palette8 = QPalette()
        palette8.setBrush(QPalette.Active, QPalette.ButtonText, brush2)
        palette8.setBrush(QPalette.Inactive, QPalette.ButtonText, brush2)
        palette8.setBrush(QPalette.Disabled, QPalette.ButtonText, brush1)
        self.backButton.setPalette(palette8)
        self.backButton.setFont(font1)
        self.backButton.setCursor(Qt.PointingHandCursor)

        self.horizontalLayout_4.addWidget(self.backButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.files_to_rename_label = QLabel(self.tab_2)
        self.files_to_rename_label.setFont(font2)
        self.horizontalLayout_4.addWidget(self.files_to_rename_label)

        self.renameButton = QPushButton(self.tab_2)
        sizePolicy3.setHeightForWidth(self.renameButton.sizePolicy().hasHeightForWidth())
        self.renameButton.setSizePolicy(sizePolicy3)
        palette9 = QPalette()
        palette9.setBrush(QPalette.Active, QPalette.ButtonText, brush2)
        palette9.setBrush(QPalette.Inactive, QPalette.ButtonText, brush2)
        palette9.setBrush(QPalette.Disabled, QPalette.ButtonText, brush1)
        self.renameButton.setPalette(palette9)
        self.renameButton.setFont(font1)
        self.renameButton.setCursor(Qt.PointingHandCursor)

        self.horizontalLayout_4.addWidget(self.renameButton)

        self.gridLayout_5.addLayout(self.horizontalLayout_4, 3, 0, 1, 2)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.win.setCentralWidget(self.centralwidget)

        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(self.win)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.episode_count = 0
        self.to_rename = {}
        self.new_filenames = []
        self.contents = []
        self.result = []
        self.excluded = {}
        self.should_probably_delete_these_later = []
        self.should_probably_delete_these_later_aswell = []
        self.should_probably_start_thinking_about_deleting_these = []
        self.these = []
        self.format = "S{sp}E{ep} {title}"

        self.ui = WindowUI(self)
        self.ui.setupUi()

        def formatTextChanged(text):
            self.format = text
            self.load_episodes(self.ui.season_number.value(), format_load=True)

        def addEpisode():
            res = {'result': (0, 'before')}
            if self.episode_count != 0:
                dialog = AddEpisodeDialog(res, self.episode_count)
                dialog.show()
                dialog.exec_()

            if res['result'][0] or self.episode_count == 0:
                if self.episode_count != 0:
                    index = max([int(re.search('\d+\Z', obj.objectName())[0]) for obj in self.should_probably_delete_these_later_aswell]) + 5
                else:
                    index = 1
                title = "..."

                dissected = re.findall("\{(sp|ep|s|e|title)(\+\d+|-\d+|)}", self.format)

                brush1 = QBrush(QColor(120, 120, 120, 255))
                brush1.setStyle(Qt.SolidPattern)

                font2 = QFont()
                font2.setPointSize(10)

                setattr(self.ui, f'label_1_{index}', QLabel(self.ui.scrollAreaWidgetContents_4))
                label_1 = getattr(self.ui, f'label_1_{index}')
                label_1.setObjectName(f'label_1_{index}')

                palette4 = QPalette()
                brush4 = QBrush(QColor(98, 118, 188, 255))
                brush4.setStyle(Qt.SolidPattern)
                palette4.setBrush(QPalette.Active, QPalette.WindowText, brush4)
                palette4.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
                label_1.setPalette(palette4)
                font5 = QFont()
                font5.setPointSize(12)
                font5.setBold(True)
                font5.setWeight(75)
                label_1.setFont(font5)
                label_1.setText(f"{index}")

                self.ui.gridLayout_4.addWidget(label_1, res['result'][0] - (1 if res['result'][1] == 'before' else 0), 0, 1, 1)

                setattr(self.ui, f'line_edit_1_{index}', QLineEdit(self.ui.scrollAreaWidgetContents_4))
                line_edit = getattr(self.ui, f'line_edit_1_{index}')
                line_edit.setObjectName(f'line_edit_1_{index}')
                font6 = QFont()
                font6.setPointSize(10)
                font6.setBold(False)
                font6.setWeight(50)
                line_edit.setFont(font6)
                line_edit.setStyleSheet("QLineEdit{background-color:rgb(0, 0, 0, 0)}\n"
                                        "QLineEdit::hover{background-color:rgb(255, 255, 255)}")
                line_edit.setFrame(False)
                line_edit.setText(title)
                line_edit.textChanged.connect(lambda k: self.load_episodes(self.ui.season_number.value(), format_load=True))

                self.ui.gridLayout_4.addWidget(line_edit, res['result'][0] - (1 if res['result'][1] == 'before' else 0), 1, 1, 1)

                setattr(self.ui, f'label_2_{index}', QLabel(self.ui.scrollAreaWidgetContents_4))
                label_2 = getattr(self.ui, f'label_2_{index}')
                label_2.setObjectName(f'label_2_{index}')
                palette5 = QPalette()
                palette5.setBrush(QPalette.Active, QPalette.WindowText, brush4)
                palette5.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
                label_2.setPalette(palette5)
                label_2.setFont(font2)
                label_2.setText(self.getFormatResult(dissected, self.ui.season_number.value(), index, title))

                self.ui.gridLayout_4.addWidget(label_2, res['result'][0] - (1 if res['result'][1] == 'before' else 0), 2, 1, 1)

                for i in list(reversed([label_1, line_edit, label_2])):
                    insert_index = (res['result'][0] - (1 if res['result'][1] == 'before' else 0)) * 3
                    self.should_probably_delete_these_later_aswell.insert(insert_index, i)

                self.load_episodes(self.ui.season_number.value(), format_load=True)

        def removeEpisode():
            res = {'result': 0}
            dialog = RemoveEpisodeDialog(res, self.episode_count)
            dialog.show()
            dialog.exec_()

            if res['result']:
                item = list(chunk(self.should_probably_delete_these_later_aswell, 3))[res['result'] - 1]
                for i in item:
                    index = self.should_probably_delete_these_later_aswell.index(i)
                    self.should_probably_delete_these_later_aswell.pop(index)
                    i.deleteLater()
                    del i
                self.load_episodes(self.ui.season_number.value(), format_load=True)

        self.ui.label_2.setText("STEP 2 - Formatting, Tweaking & Renaming")
        self.ui.attention.setText("*It seems their aren't any dedicated wikipedia pages for this TV series for each season, and instead are bundled onto one page.\n"
                                    "*Enter the correct season number you wish for manually in the spinbox below.")
        self.ui.attention.setVisible(False)
        self.ui.filename_formatting_label.setText("Filename Formatting")
        self.ui.filename_format.setText(self.format)
        self.ui.filename_format.textChanged.connect(formatTextChanged)
        self.ui.season_label.setText("Season Number: ")
        self.ui.season_number.setValue(1)
        self.ui.season_number.valueChanged.connect(lambda k: self.load_episodes(k, season_load=True))
        self.ui.filename_format_label.setText("Filename Format")
        self.ui.episodes_label.setText("Episodes")
        self.ui.addButton.setText("ADD")
        self.ui.addButton.clicked.connect(addEpisode)
        self.ui.removeButton.setText("REMOVE")
        self.ui.removeButton.clicked.connect(removeEpisode)
        self.ui.format_help_6.setText("{e+1}, {sp+1} - Addition, Subtraction")
        self.ui.format_help_5.setText("{title} - Episode Title")
        self.ui.format_help_4.setText("{ep} - Episode Number Zero-Padded (\"07\")")
        self.ui.format_help_1.setText("{s} - Season Number (\"7\")")
        self.ui.format_help_3.setText("{e} - Episode Number")
        self.ui.format_help_2.setText("{sp} - Season Number Zero-Padded")
        self.ui.folder_location_label.setText("Folder location")
        self.ui.folder_location_button.setText("...")
        self.ui.folder_location_description.setText("The folder location containing all of the season's episodes")
        self.ui.folder_location.setReadOnly(True)
        self.ui.filename_label.setText("Filename")
        self.ui.new_filename_label.setText("New Filename")
        self.ui.backButton.setText("BACK")
        self.ui.files_to_rename_label.setText("0 files will be renamed.")
        self.ui.renameButton.setText("RENAME")
        self.ui.renameButton.setEnabled(False)
        self.ui.nextButton.setText("NEXT")
        self.ui.nextButton.setEnabled(False)
        self.ui.radioButton_2.setText("Search wikipedia")
        self.ui.radioButton.setText("Wikipedia URL")
        self.ui.search_wikipedia.setPlaceholderText("Enter search prompt here. e.g. \"Lost season 1\"")
        self.ui.wikipedia_search_button.setText("Search")
        self.ui.wikipedia_url.setPlaceholderText("https://en.wikipedia.org/wiki/Lost_(season_1)")
        self.ui.label.setText("STEP 1 - Finding the wikipedia page that contains all the episode names")
        self.ui.wikipedia_url.setDisabled(True)

        def radioButtonOne(res):
            self.ui.wikipedia_url.setEnabled(res)
        def radioButtonTwo(res):
            self.ui.search_wikipedia.setEnabled(res)
            self.ui.wikipedia_search_button.setEnabled(res)
            self.ui.scrollArea.setEnabled(res)
        self.ui.radioButton.toggled.connect(radioButtonOne)
        self.ui.radioButton_2.toggled.connect(radioButtonTwo)

        def openFolderDialog():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            if self.ui.folder_location.text() != "":
                dialog.setDirectory(self.ui.folder_location.text())

            if dialog.exec_() == QFileDialog.Accepted:
                path = dialog.selectedFiles()[0]
                self.ui.folder_location.setText(path)

                self.excluded.clear()
                self.load_filenames(path)

        self.ui.folder_location_button.clicked.connect(openFolderDialog)

        self.ui.wikipedia_search_button.clicked.connect(self.search)
        self.ui.nextButton.clicked.connect(self.nextTab)
        self.ui.backButton.clicked.connect(lambda: self.ui.tabWidget.setCurrentIndex(0))
        self.ui.renameButton.clicked.connect(self.rename)

    def rename(self):
        path = self.ui.folder_location.text() + "/"
        detailed = []
        for (file, new_file) in self.to_rename.items():
            file = os.path.join(path, file)
            new_file = os.path.join(path, new_file)
            os.rename(file, new_file)
            detailed.append(f"Old: {file}\nNew: {new_file}")

        dialog = CompletionDialog(len(self.to_rename), "\n\n".join(detailed))
        dialog.show()
        dialog.exec_()

        if len(self.should_probably_delete_these_later_aswell):
            for item in self.should_probably_delete_these_later_aswell:
                if hasattr(item, 'deleteLater'):
                    item.deleteLater()
                del item

            self.should_probably_delete_these_later_aswell.clear()

        self.clearUp()

        self.episode_count = 0

        self.ui.folder_location.clear()
        self.to_rename.clear()
        self.new_filenames.clear()
        self.excluded.clear()
        return

    def onFocus(self, old, new):
        if old is None:
            if self.ui.tabWidget.currentIndex() == 1:
                self.load_filenames(self.ui.folder_location.text(), format_load=True)

    def getFormatResult(self, dissected, s, e, title):
        result = self.format

        for (key, other) in dissected:
            string = "".join([key, other])
            index = self.format.index("{" + string + "}")
            full = self.format[index:index + len(string) + 2]

            if key == "s":
                a = eval(f'{s}{other}')
                result = result.replace(full, f"{a}")
            elif key == "sp":
                a = eval(f'{s}{other}')
                result = result.replace(full, f"{a:02}")
            elif key == "e":
                a = eval(f'{e}{other}')
                result = result.replace(full, f"{a}")
            elif key == "ep":
                a = eval(f'{e}{other}')
                result = result.replace(full, f"{a:02}")
            elif key == "title":
                result = result.replace(full, title)

        return result

    def clearUp(self):
        if len(self.should_probably_start_thinking_about_deleting_these):
            self.ui.renameButton.setEnabled(False)
            self.ui.files_to_rename_label.setText("0 files will be renamed.")
            for item1, item2, in chunk(self.should_probably_start_thinking_about_deleting_these, 2):
                try:
                    self.ui.verticalLayout_5.removeWidget(item1)
                except:
                    pass

                try:
                    self.ui.verticalLayout_4.removeWidget(item2)
                except:
                    pass

                for item in [item1, item2]:
                    if hasattr(item, 'deleteLater'):
                        item.deleteLater()
                    if hasattr(item, 'setParent'):
                        item.setParent(None)

                del item

            self.should_probably_start_thinking_about_deleting_these.clear()

    def load_filenames(self, path, format_load=False):
        if not path or not len(self.new_filenames):
            self.clearUp()
            return

        path = path + "/"

        contents = list(filter(lambda k: k != "Thumbs.db" and os.path.isfile(path + k), os.listdir(path)))

        if not contents:
            self.clearUp()
            return

        if contents != self.contents and format_load:
            format_load = False

        self.contents = contents

        font2 = QFont()
        font2.setPointSize(10)

        already_added = {}
        new_filenames = iter(self.new_filenames)
        files_to_rename = 0

        dissected = re.findall("\{(sp|ep|s|e|title)(\+\d+|-\d+|)}", self.format)

        self.to_rename.clear()

        if format_load and len(self.should_probably_start_thinking_about_deleting_these):
            for index, (filename_widget, new_filename_widget) in enumerate(chunk(self.should_probably_start_thinking_about_deleting_these, 2)):

                file = filename_widget.text()
                filename = '.'.join(file.split('.')[:-1])
                extension = file.split('.')[-1]

                try:
                    if file in self.excluded:
                        if self.excluded[file] == 0:
                            new_filename = "SKIPPED"
                        elif self.excluded[file] == 1:
                            try:
                                new_filename = next(new_filenames)
                            except StopIteration:
                                pass
                            new_filename = "SKIPPED"
                    else:
                        new_filename = next(new_filenames)
                except StopIteration:
                    new_filename = self.getFormatResult(dissected, self.ui.season_number.value(), index + 1, "UNKNOWN")

                if file in self.excluded:
                    filename_new = new_filename
                else:
                    if filename in already_added:
                        filename_new = already_added[filename] + f".{extension}"
                    else:
                        filename_new = new_filename + f".{extension}"

                if file not in self.excluded:
                    palette = QPalette()
                    if file != filename_new:
                        files_to_rename += 1
                        brush = QBrush(QColor(0, 98, 135, 255))
                        self.to_rename[file] = filename_new
                    else:
                        brush = QBrush(QColor(0, 135, 44, 255))
                    brush.setStyle(Qt.SolidPattern)
                    palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                    palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)

                if file in self.excluded:
                    red_palette = QPalette()
                    brush = QBrush(QColor(135, 0, 0, 255))
                    brush.setStyle(Qt.SolidPattern)
                    red_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                    red_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                    filename_widget.setPalette(red_palette)
                    new_filename_widget
                else:
                    if file == filename_new:
                        filename_widget.setPalette(palette)
                    else:
                        black_palette = QPalette()
                        brush = QBrush(QColor(0, 0, 0, 255))
                        brush.setStyle(Qt.SolidPattern)
                        black_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                        black_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                        filename_widget.setPalette(black_palette)

                if file in self.excluded:
                    red_palette = QPalette()
                    brush = QBrush(QColor(135, 0, 0, 255))
                    brush.setStyle(Qt.SolidPattern)
                    red_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                    red_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                    new_filename_widget.setPalette(red_palette)
                else:
                    new_filename_widget.setPalette(palette)
                new_filename_widget.setText(filename_new)

                if filename not in already_added:
                    already_added[filename] = new_filename
            self.ui.files_to_rename_label.setText(f"{files_to_rename} file{'s' if files_to_rename != 1 else ''} will be renamed.")
            if files_to_rename > 0:
                self.ui.renameButton.setEnabled(True)
            else:
                self.ui.renameButton.setEnabled(False)
            return

        self.clearUp()

        for index, file in enumerate(contents):
            try:
                if file in self.excluded:
                    if self.excluded[file] == 0:
                        new_filename = "SKIPPED"
                    elif self.excluded[file] == 1:
                        try:
                            new_filename = next(new_filenames)
                        except StopIteration:
                            pass
                        new_filename = "SKIPPED"
                else:
                    new_filename = next(new_filenames)
            except StopIteration:
                new_filename = self.getFormatResult(dissected, self.ui.season_number.value(), index + 1, "UNKNOWN")

            filename = '.'.join(file.split('.')[:-1])
            extension = file.split('.')[-1]

            if file in self.excluded:
                filename_new = new_filename
            else:
                if filename in already_added:
                    filename_new = already_added[filename] + f".{extension}"
                else:
                    filename_new = new_filename + f".{extension}"

            setattr(self.ui, f'label_5_1_{index}', CustomCheckBox(self, file, self.ui.scrollAreaWidgetContents_5))
            label_1 = getattr(self.ui, f'label_5_1_{index}')
            if file in self.excluded:
                red_palette = QPalette()
                brush = QBrush(QColor(135, 0, 0, 255))
                brush.setStyle(Qt.SolidPattern)
                red_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                red_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                label_1.setPalette(red_palette)
            label_1.setFont(font2)
            label_1.setText(file)
            self.ui.verticalLayout_5.insertWidget(index, label_1)

            setattr(self.ui, f'label_5_2_{index}', QLabel(self.ui.scrollAreaWidgetContents_6))
            label_2 = getattr(self.ui, f'label_5_2_{index}')

            if file not in self.excluded:
                palette = QPalette()
                if file != filename_new:
                    files_to_rename += 1
                    brush = QBrush(QColor(0, 98, 135, 255))
                    self.to_rename[file] = filename_new
                else:
                    brush = QBrush(QColor(0, 135, 44, 255))
                brush.setStyle(Qt.SolidPattern)
                palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
            label_2.setFont(font2)
            label_2.setText(filename_new)

            if file in self.excluded:
                red_palette = QPalette()
                brush = QBrush(QColor(135, 0, 0, 255))
                brush.setStyle(Qt.SolidPattern)
                red_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                red_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                label_2.setPalette(red_palette)
            else:
                label_2.setPalette(palette)

            if file not in self.excluded:
                if file == filename_new:
                    label_1.setPalette(palette)
                else:
                    black_palette = QPalette()
                    brush = QBrush(QColor(0, 0, 0, 255))
                    brush.setStyle(Qt.SolidPattern)
                    black_palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
                    black_palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
                    label_1.setPalette(black_palette)

            self.ui.verticalLayout_4.insertWidget(index, label_2)

            if file not in self.excluded:
                if filename not in already_added:
                    already_added[filename] = new_filename

            self.should_probably_start_thinking_about_deleting_these.extend([label_1, label_2])

        self.ui.files_to_rename_label.setText(f"{files_to_rename} file{'s' if files_to_rename != 1 else ''} will be renamed.")
        if files_to_rename > 0:
            self.ui.renameButton.setEnabled(True)
        else:
            self.ui.renameButton.setEnabled(False)

    def nextTab(self):
        self.ui.tabWidget.setCurrentIndex(1)
        index = int(self.selectedResult.objectName().replace("widget_", "")) - 1

        data = self.result[index]

        try:
            website = requests.get(f"https://en.wikipedia.org/wiki/{data['key']}")
            status = website.status_code
            description = website.text
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as exception:
            status = 404
            description = f"{exception}"

        if status != 200:
            msg = QMessageBox()
            msg.setWindowTitle("Unexpected error")
            msg.setText("An error occured while attempting to retreive data from en.wikipedia.org")
            msg.setInformativeText(description)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            x = msg.exec_()
            return

        self.website = BeautifulSoup(website.text, 'lxml')

        tables = self.website.find_all(attrs={'class': 'wikiepisodetable'})
        if len(tables) == 0:
            self.ui.tabWidget.setCurrentIndex(0)
            msg = QMessageBox()
            msg.setWindowTitle("Ah.")
            msg.setText("It seems this wikipedia page does not contain any data for any episodes.\nTry another one.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            x = msg.exec_()
            return

        self.multiple_seasons_one_page = False

        if 'season' in data['title'].lower():
            season_number = int(re.search('season \d+', data['title'].lower())[0].replace("season ", ""))
        else:
            self.multiple_seasons_one_page = True
            self.ui.attention.setVisible(True)
            season_number = 1

        self.ui.season_number.setValue(season_number)

        self.ui.tabWidget.setCurrentIndex(1)

        self.load_episodes(season_number)

    def load_episodes(self, season_number=1, season_load=False, format_load=False):
        episode_tables = self.website.find_all(attrs={'class': 'wikiepisodetable'})

        if self.multiple_seasons_one_page:
            season = episode_tables[season_number - 1]
            self.ui.season_number.setMaximum(len(episode_tables))
        else:
            self.ui.season_number.setMaximum(999)
            season = episode_tables[0]
        headers = [header.text if 'title' not in header.text.lower() else 'title' for header in season.find_next('tr')]
        title_index = headers.index("title") - 1
        episodes = season.find_all(attrs={'class': 'vevent'})

        dissected = re.findall("\{(sp|ep|s|e|title)(\+\d+|-\d+|)}", self.format)

        self.new_filenames.clear()

        if format_load or (season_load and (not self.multiple_seasons_one_page)):
            iterator = list(chunk(self.should_probably_delete_these_later_aswell, 3))
            self.episode_count = len(iterator)
            for index, (number_widget, title_widget, filename_widget) in enumerate(iterator, start=1):
                title = title_widget.text()
                format_text = self.getFormatResult(dissected, season_number, index, title)

                if ': ' in format_text:
                    format_text = format_text.replace(": ", " - ")

                for illegal_char in ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]:
                    format_text = format_text.replace(illegal_char, '')

                number_widget.setText(f"{index}")
                filename_widget.setText(format_text)
                self.ui.gridLayout_4.addWidget(number_widget, index - 1, 0, 1, 1)
                self.ui.gridLayout_4.addWidget(title_widget, index - 1, 1, 1, 1)
                self.ui.gridLayout_4.addWidget(filename_widget, index - 1, 2, 1, 1)
                self.new_filenames.append(format_text)

            self.load_filenames(self.ui.folder_location.text(), format_load=True)
            return

        if len(self.should_probably_delete_these_later_aswell):
            for item in self.should_probably_delete_these_later_aswell:
                if hasattr(item, 'deleteLater'):
                    item.deleteLater()
                del item

            self.should_probably_delete_these_later_aswell.clear()

        episodes = list(filter(lambda episode: '"' in episode.find_all('td')[title_index].text, episodes))

        self.episode_count = len(episodes)

        for index, episode in enumerate(episodes, start=1):
            title = re.search('"[^"]+"', episode.find_all('td')[title_index].text)[0].replace('"', "")
            title = re.sub('\[[0-9]+]\Z', '', title)
            title = title.replace("†", "")

            if title == "?":
                title = "Question Mark"

            if ': ' in title:
                title = title.replace(": ", " - ")

            for illegal_char in ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]:
                title = title.replace(illegal_char, '')

            brush1 = QBrush(QColor(120, 120, 120, 255))
            brush1.setStyle(Qt.SolidPattern)

            font2 = QFont()
            font2.setPointSize(10)

            setattr(self.ui, f'label_1_{index}', QLabel(self.ui.scrollAreaWidgetContents_4))
            label_1 = getattr(self.ui, f'label_1_{index}')
            label_1.setObjectName(f'label_1_{index}')

            palette4 = QPalette()
            brush4 = QBrush(QColor(98, 118, 188, 255))
            brush4.setStyle(Qt.SolidPattern)
            palette4.setBrush(QPalette.Active, QPalette.WindowText, brush4)
            palette4.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
            label_1.setPalette(palette4)
            font5 = QFont()
            font5.setPointSize(12)
            font5.setBold(True)
            font5.setWeight(75)
            label_1.setFont(font5)
            label_1.setText(f"{index}")

            self.ui.gridLayout_4.addWidget(label_1, index - 1, 0, 1, 1)

            setattr(self.ui, f'line_edit_1_{index}', QLineEdit(self.ui.scrollAreaWidgetContents_4))
            line_edit = getattr(self.ui, f'line_edit_1_{index}')
            line_edit.setObjectName(f'line_edit_1_{index}')
            font6 = QFont()
            font6.setPointSize(10)
            font6.setBold(False)
            font6.setWeight(50)
            line_edit.setFont(font6)
            line_edit.setStyleSheet("QLineEdit{background-color:rgb(0, 0, 0, 0)}\n"
                                    "QLineEdit::hover{background-color:rgb(255, 255, 255)}")
            line_edit.setFrame(False)
            line_edit.setText(title)
            line_edit.textChanged.connect(lambda k: self.load_episodes(self.ui.season_number.value(), format_load=True))

            self.ui.gridLayout_4.addWidget(line_edit, index - 1, 1, 1, 1)

            setattr(self.ui, f'label_2_{index}', QLabel(self.ui.scrollAreaWidgetContents_4))
            label_2 = getattr(self.ui, f'label_2_{index}')
            label_2.setObjectName(f'label_2_{index}')
            palette5 = QPalette()
            palette5.setBrush(QPalette.Active, QPalette.WindowText, brush4)
            palette5.setBrush(QPalette.Inactive, QPalette.WindowText, brush4)
            label_2.setPalette(palette5)
            label_2.setFont(font2)

            format_text = self.getFormatResult(dissected, season_number, index, title)
            label_2.setText(format_text)

            self.ui.gridLayout_4.addWidget(label_2, index - 1, 2, 1, 1)

            self.should_probably_delete_these_later_aswell.extend([label_1, line_edit, label_2])
            self.new_filenames.append(format_text)
        self.load_filenames(self.ui.folder_location.text(), format_load=True)

    def widgetMousePressEvent(self, widget, a0):
        if a0 != "":
            QWidget.mousePressEvent(widget, a0)

        self.its_this_one(widget)

    def its_this_one(self, widget):
        if len(self.these):
            should_return = False
            if "rgb(145, 232, 176)" in widget.styleSheet():
                should_return = True
            item = self.these[0]
            objectName = re.search('#[a-z0-9_]+', item.styleSheet())[0]
            item.setStyleSheet(objectName + "::hover {background-color: rgb(234, 234, 234)}")
            self.these.pop(0)

            if should_return:
                self.ui.nextButton.setEnabled(False)
                return
        objectName = re.search('#[a-z0-9_]+', widget.styleSheet())[0]
        widget.setStyleSheet(f"{objectName}" + " {background-color: rgb(145, 232, 176)}\n"
                             f"{objectName}" + "::hover {}")
        self.these.append(widget)

        self.ui.nextButton.setEnabled(True)
        self.selectedResult = widget

    def search(self):
        text = self.ui.search_wikipedia.text()
        try:
            req = requests.get(f'https://en.wikipedia.org/w/rest.php/v1/search/title?q={text}&limit=25',
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'})
            status = req.status_code
            description = req.text
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as exception:
            status = 404
            description = f"{exception}"

        if status != 200:
            msg = QMessageBox()
            msg.setWindowTitle("Unexpected error")
            msg.setText("An error occured while attempting to retreive data from en.wikipedia.org")
            msg.setInformativeText(description)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            x = msg.exec_()
            return

        self.result = req.json()['pages']

        for (a, b, c, d, e, f, widget) in chunk(self.should_probably_delete_these_later, 7):
            for item in [a, b, c, d, e, f]:
                if hasattr(item, 'deleteLater'):
                    item.deleteLater()
                del item
            self.ui.formLayout_2.removeWidget(widget)
            widget.deleteLater()

        self.should_probably_delete_these_later.clear()
        self.these.clear()
        self.selectedResult = None
        ref = {}

        for index, res in enumerate(self.result, start=1):
            setattr(self.ui, f'widget_{index}', CustomWidget(self, self.ui.scrollAreaWidgetContents))
            widget = getattr(self.ui, f'widget_{index}')
            widget.setObjectName(f"widget_{index}")
            widget.setCursor(Qt.PointingHandCursor)
            widget.setStyleSheet(f"#widget_{index}" + "::hover {background-color: rgb(234, 234, 234)}")

            sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy1.setHorizontalStretch(0)
            sizePolicy1.setVerticalStretch(0)
            sizePolicy1.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
            widget.setSizePolicy(sizePolicy1)

            setattr(self.ui, f'horizontal_{index}', QHBoxLayout(widget))
            horizontal = getattr(self.ui, f'horizontal_{index}')

            setattr(self.ui, f'vertical_{index}', QVBoxLayout())
            vertical = getattr(self.ui, f'vertical_{index}')

            setattr(self.ui, f'title_{index}', QLabel(widget))
            title = getattr(self.ui, f'title_{index}')
            title.setText(res['title'])

            vertical.addWidget(title)

            setattr(self.ui, f'description_{index}', QLabel(widget))
            description = getattr(self.ui, f'description_{index}')
            description.setText(res['description'])

            palette = QPalette()
            brush = QBrush(QColor(97, 97, 97, 255))
            brush.setStyle(Qt.SolidPattern)
            palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
            palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
            brush1 = QBrush(QColor(120, 120, 120, 255))
            brush1.setStyle(Qt.SolidPattern)
            palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush1)
            description.setPalette(palette)

            vertical.addWidget(description)

            horizontal.addLayout(vertical)

            setattr(self.ui, f'spacer_{index}', QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            spacer = getattr(self.ui, f'spacer_{index}')

            horizontal.addItem(spacer)

            setattr(self.ui, f'this_one_{index}', ThisOneButton(self, widget))
            this_one = getattr(self.ui, f'this_one_{index}')
            this_one.setCursor(Qt.PointingHandCursor)
            this_one.setText("It's this one!")

            sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            sizePolicy2.setHorizontalStretch(0)
            sizePolicy2.setVerticalStretch(0)
            sizePolicy2.setHeightForWidth(this_one.sizePolicy().hasHeightForWidth())
            this_one.setSizePolicy(sizePolicy2)

            horizontal.addWidget(this_one)

            self.ui.formLayout_2.setWidget(index - 1, QFormLayout.SpanningRole, widget)
            self.should_probably_delete_these_later.extend([title, description, spacer, vertical, horizontal, this_one, widget])

def changedFocusSlot(old, now):
    print(old, now)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = Window()
    app.focusChanged.connect(win.onFocus)
    win.show()

    sys.exit(app.exec_())
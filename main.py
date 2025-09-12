import sys
import json, time
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import qdarktheme

class FlashcardApp(QWidget):
    def __init__(self, flashcards):
        super().__init__()
        self.flashcards = flashcards
        self.index = -1
        self.language_choice = 'e'
        self.show_known_values_only = True
        self.guessed_word_incorrectly = False

        self.initUI()

    def initUI(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #2d2e2e;")
        self.setWindowOpacity(0.9)
        self.resize(100, 10)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        screen = QGuiApplication.screens()[3]
        geometry = screen.availableGeometry()
        self.move(geometry.x() + 40, geometry.y() + int((geometry.height() - self.height()) / 2) + 200)

        self.layout = QVBoxLayout()

        self.langCheckbox = QCheckBox('lang')
        self.langCheckbox.setChecked(True)
        self.langCheckbox.stateChanged.connect(self.switchLanguage)
        # self.layout.addWidget(self.langCheckbox)

        self.wordLabel = QLabel()
        self.layout.addWidget(self.wordLabel)

        self.inputField = QLineEdit()
        self.inputField.returnPressed.connect(self.checkAnswer)
        self.inputField.setStyleSheet("border: none;")
        self.layout.addWidget(self.inputField)

        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("color: white; font-size: 14px;")
        self.layout.addWidget(self.desc_label)

        buttonLayout = QHBoxLayout()

        self.layout.addLayout(buttonLayout)

        self.setLayout(self.layout)

        self.nextWord()

    def writeToFile(self):
        with open('C:/Users/soliman-nicholas/OneDrive - AirbusDSGS/Documents/etc/k/data/all.json', 'w', encoding='utf-8') as f:
            json.dump(self.flashcards, f, ensure_ascii=False, indent=2)

    def switchLanguage(self, state):
        if state == 2:
            self.language_choice = 'k'
        else:
            self.language_choice = 'e'
        self.updateCard()

    def updateCard(self):
        self.desc_label.setText("")
        card = self.flashcards[self.index]
        if self.language_choice == 'k':
            self.wordLabel.setText(f"{card['word']}")
        else:
            self.wordLabel.setText(f"{card['english_translation']}")

    def checkAnswer(self):
        card = self.flashcards[self.index]
        user_input = self.inputField.text().strip()

        if self.language_choice == 'k':
            correct_answer = card['english_translation']
        else:
            correct_answer = card['romanization']

        self.inputField.clear()
        # self.desc_label.setWordWrap(False)
        if user_input.lower() == '':
            if self.desc_label.text() == f"{card['word']}":
                self.desc_label.setText(f"{card['romanization']}")
                return
            self.guessed_word_incorrectly = True
            self.desc_label.setText(f"{card['word']}")
        elif user_input.lower() == 'e':
            self.showExampleEng()
            self.guessed_word_incorrectly = True
        elif user_input.lower() == 'k':
            self.showExample()
            self.guessed_word_incorrectly = True
        elif user_input.lower() == 'ls':
            self.openListWindow()
        elif user_input.lower() == 'f': #f ilter
            self.show_known_values_only = not self.show_known_values_only
            if self.show_known_values_only:
                self.desc_label.setText("Skipping known words.")
            else:
                self.desc_label.setText("Showing all words.")
        elif user_input.lower() == 'lang':
            self.language_choice = 'e' if self.language_choice == 'k' else 'k'
            self.updateCard()
        elif user_input.lower() == 'r':
            self.index = -1
            self.nextWord()
        elif user_input.lower() == 'clear':
            self.setAllKnownToFalse()
        elif user_input.lower() == 'q':
            self.close()
        elif user_input.lower() == 'help' or user_input.lower() == 'h' or user_input.lower() == '?':
            self.desc_label.setText(
                "''        : Ans\n"
                "'r'       : Restart\n"
                "'e'       : Example in EN\n"
                "'k'       : Example in KR\n"
                "'ls'      : Open List Windw\n"
                "'f'       : Filter Knowns\n"
                "'lang'    : Switch Language\n"
                "'clear'   : Reset Knowns\n"
                "'esc'/'q' : Quit"
            )
            # self.desc_label.setWordWrap(True)
        elif user_input.lower() == correct_answer.lower():
            if not self.guessed_word_incorrectly:
                self.flashcards[self.index]['known'] = True
                self.writeToFile()
            self.nextWord()
        else:
            self.guessed_word_incorrectly = True
            self.desc_label.setText(f"Incorrect. Try again.")

        self.resize(10, 10)

    def showExample(self):
        card = self.flashcards[self.index]
        self.desc_label.setText(f"{card['example_sentence_native']}")

    def showExampleEng(self):
        card = self.flashcards[self.index]
        self.desc_label.setText(f"{card['example_sentence_english']}")

    def nextWord(self):
        self.guessed_word_incorrectly = False
        self.index += 1
        if self.show_known_values_only:
            while (self.flashcards[self.index]['known'] and self.index < len(self.flashcards) - 1):
                self.index += 1
        else:
            if self.index >= len(self.flashcards):
                QMessageBox.information(self, "Info", "No more words. Restarting from first word.")
                self.index = 0
        self.updateCard()

    def openListWindow(self):
        self.listWindow = ListWindow(self)
        self.listWindow.show()

    def setAllKnownToFalse(self):
        for card in self.flashcards:
            card['known'] = False
        self.writeToFile()
        self.index = -1
        self.nextWord()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Down:
            current_pos = self.pos()
            new_pos = current_pos + QPoint(0, 10)
            self.move(new_pos)
        elif event.key() == Qt.Key.Key_Up:
            current_pos = self.pos()
            new_pos = current_pos - QPoint(0, 10)
            self.move(new_pos)
        super().keyPressEvent(event)
    
class ListWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.flashcards = parent.flashcards
        self.initUI()
        self.resize(420, 320)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #2d2e2e;")

    def initUI(self):
        self.setWindowTitle('')
        self.layout = QGridLayout()

        self.knownListWidget = QListWidget(self)
        self.unknownListWidget = QListWidget(self)

        for card in self.flashcards:
            if card['known']:
                self.knownListWidget.addItem(card['word'])
            else:
                self.unknownListWidget.addItem(card['word'])

        self.knownListWidget.itemClicked.connect(self.handleItemClicked)
        self.unknownListWidget.itemClicked.connect(self.handleItemClicked)

        knownLabel = QLabel(f"Known Words ({self.knownListWidget.count()}):")
        unknownLabel = QLabel(f"Unknown Words ({self.unknownListWidget.count()}):")
        self.detailLabel = QLabel('')

        self.switchButton = QPushButton("Switch Known/Unknown", self)
        self.switchButton.clicked.connect(self.switchCardStatus)

        self.layout.addWidget(knownLabel, 0, 0)
        self.layout.addWidget(self.knownListWidget, 1, 0)
        self.layout.addWidget(unknownLabel, 0, 1)
        self.layout.addWidget(self.unknownListWidget, 1, 1)
        self.layout.addWidget(self.detailLabel, 2, 0, 1, 2)
        self.layout.addWidget(self.switchButton, 3, 0, 1, 2)

        self.setLayout(self.layout)

    def handleItemClicked(self, item):
        if self.sender() == self.knownListWidget:
            self.unknownListWidget.clearSelection()
            self.switchButton.setText("I don't know this word")
            self.switcher = False
        elif self.sender() == self.unknownListWidget:
            self.knownListWidget.clearSelection()
            self.switchButton.setText("I know this word")
            self.switcher = True

        self.showWordDetails(item)

    def switchCardStatus(self):
        current_item = None

        if not self.switcher:
            current_item = self.knownListWidget.currentItem()
        else:
            current_item = self.unknownListWidget.currentItem()

        if current_item:
            matching_card = next((card for card in self.flashcards if card['word'] == current_item.text()), None)
            if matching_card:
                matching_card['known'] = not matching_card['known']

        self.parent.writeToFile()
        self.knownListWidget.clear()
        self.unknownListWidget.clear()

        for card in self.flashcards:
            if card['known']:
                self.knownListWidget.addItem(card['word'])
            else:
                self.unknownListWidget.addItem(card['word'])

    def showWordDetails(self, item):
        matching_card = next((card for card in self.flashcards if card['word'] == item.text()), None)
        if matching_card:
            details = (f"Word: {matching_card['word']}\n"
                       f"English Translation: {matching_card['english_translation']}\n"
                       f"Romanization: {matching_card['romanization']}\n"
                       f"Example (Native): {matching_card['example_sentence_native']}\n"
                       f"Example (English): {matching_card['example_sentence_english']}")
            self.detailLabel.setText(details)
        self.resize(420, 320)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

def load_flashcards():
    with open('C:/Users/soliman-nicholas/OneDrive - AirbusDSGS/Documents/etc/k/data/all.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    flashcards = load_flashcards()
    ex = FlashcardApp(flashcards)
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
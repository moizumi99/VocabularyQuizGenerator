# -*- coding: utf-8 -*-

"""
This little program extracts words from Kindle Bookmark
and associate them with corresponding Japanese words to 
create an Anki test deck.

You need csv file exported from Eijiro to execute this.

Last edited: August 2018
"""

import sys, codecs
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidgetItem
from PyQt5.QtWidgets import QAction, qApp, QMessageBox, QFileDialog, QTableWidget
import log

class VocabularyFiles:
    """Stores file related information"""

    def __init__(self):
        self.word_list = []
        self.dictionary_text = ""
        self.quiz = {}
        self.unused_words = []
        self.error_message = ""
        self.report_text = ""

    def ReadKindleBookmakFile(self, fname):
        if fname:
            try:
                with open(fname, 'r', encoding="utf8") as f:
                    vocab_html = f.readlines()
            except (FileNotFoundError, UnicodeDecodeError, IOError) as e:
                self.error_message = "Error reading " + fname
                self.error_message += "\n" + str(e)
                return False
            self.word_list = ExtractWords(vocab_html)
        return True

    def ReadDictionaryFile(self, fname):
        try:
            with codecs.open(fname, 'r', 'utf-16') as eijiro_file:
                self.dictionary_text = eijiro_file.readlines()
        except (FileNotFoundError, IOError) as e:
            self.error_message = "Error opening " + fname
            self.error_message += "\n" + str(e)
            return False
        if self.dictionary_text:
            return True
        else:
            return False

    def CreateTest(self, statusBar):
        start_point = 0
        self.quiz = {}
        undefined = 0
        word_list = []
        total_number = len(self.word_list)
        word_count = 0
        self.report_text = ""
        statusBar.showMessage("{:4d} out of {:4d} words processed".format(word_count, total_number))
        for word in self.word_list:
            variations = makeVariations(word)
            for search_word in variations:
                defs, found_word, start_point = FindDefinitions(search_word, self.dictionary_text, start_point)
                if defs:
                    break
            if defs:
                self.quiz[found_word] = defs
                word_list.append(found_word)
                if word != found_word:
                    self.report_text += found_word + " is used instead of " + word + ".\n"
            else:
                self.quiz[word] = [""]
                word_list.insert(0, word)
                self.report_text += word + " was not found.\n"
                undefined += 1
            word_count += 1
            statusBar.showMessage("{:4d} out of {:4d} words processed".format(word_count, total_number))
        self.word_list = word_list
        self.report_text = "Quiz Created Successfully\n\n" + self.report_text
        self.report_text += "\n Total " + str(word_count - undefined) + " words found.\n"
        self.report_text += "Definitions for " + str(undefined) + " words not found.\n"
        self.report_text += "\n You can export the test now"
        log.log(self.report_text)
        return True
    
    def ExportQuizFile(self, fname):
        try:
            with codecs.open(fname, 'w', 'utf-8') as fout:
                for word in self.word_list:
                    defs = self.quiz[word]
                    if defs:
                        outtxt = word.strip() + "\t" + ('<br>'.join(defs)) + "\n"
                        fout.write(outtxt)
            return True
        except IOError as e:
            self.error_message = "Error opening " + fname
            self.error_message += "\n" + str(e)
            return False
        return False

def makeVariations(word):
    word_list = [word]
    if word[-1] == "s" and 1 < len(word):
        word_list.append(word[:-1])
    if word[-2:] == "es" and 2 < len(word):
        word_list.append(word[:-2])
    word_list.extend([switchCapitalization(x) for x in word_list])
    if word_list[0].find('-') >= 0:
        word_list.extend([x.replace('-', ' ') for x in word_list])
    
    return word_list

def switchCapitalization(word):
    if word[0].isupper():
        result = word.lower()
    else:
        result = word.capitalize()
    return result

def FindDefinitions(word, dic, start_point=0, remove_hints=False):
    REMOVE_LIST = [u'◆', u'\ ・', u'【変化】', u'【分節】', u'【＠】']
    
    deflist = []
    # find the first element that meets the condition
    # Don't want to evaluate all elements, so starting from 'startpoint'
    index = start_point
    end_point = (start_point - 1) % len(dic)
    while (index != end_point) and (not dic[index].startswith(word+' ///')):
        index = (index + 1) % len(dic)
    if not dic[index].startswith(word+' ///'): # not found
        return deflist, word, start_point
    # found 
    l = dic[index][len(word)+4:]
    for r in REMOVE_LIST:
        ii = l.find(r)
        l = l[:ii] if (ii >= 0) else l
    if remove_hints:
        # remove << >> that contains English words as they may be plural forms
        # remove () that contains English words as they may be a big hint
        for letter_index in range(2):
            left, right = [(u'《', u'》'), ('(', ')')][letter_index]
            search_pos = 0
            while(True):
                i1, i2 = l.find(left, search_pos), l.find(right, search_pos)
                if not (0 <= i1 < i2):
                    break
                if l[i1+1:i2].isalpha():
                    l = l[:i1] + l[i2+1:]
                search_pos = i2 + 2
    replaced_word_list = []
    for d in l.split('\\'):
        # reference to another definition
        i1, i2 =  d.find(u'<→'), d.find(u'>')
        if 0 <= i1 < i2:
            new_word = d[i1 + 2:i2]
            if new_word not in replaced_word_list:
                log.log(word + " is referred to " + new_word)
                dl, _, _ = FindDefinitions(d[i1 + 2:i2], dic, start_point)
                deflist.extend(dl)
                replaced_word_list.append(new_word)
        elif d.strip():
            deflist.append(d.strip())
    new_start_point = (index + 1) % len(dic) # next starting point
    return deflist, word, new_start_point


def ExtractWords(html_text):
    """Extract English words from html text"""

    word_list = []
    for line in html_text:
        index = line.find(u'<div class=\'noteText\'>')
        if index < 0:
            continue
        line = line[index + 22:]
        index = line.find(u'</')
        if index < 0:
            continue
        word = line[:index].rstrip(',').rstrip('.').rstrip()
        word_list.append(word)
    log.log(str(len(word_list)) + " words extracted from " + str(len(html_text)) + " lines")
    return word_list

def validate_dir(target_dir):
    try:
        new_path = Path(target_dir)
        if new_path.is_dir():
            return True
    except IOError:
        return False
    return False

def validate_file(target_file):
    try:
        new_path = Path(target_file)
        if new_path.is_file():
            return True
    except IOError:
        return False
    return False

class IniFile:
    """Stores initial values"""
    
    INIT_FILE_NAME = ".vocab.ini"
    
    def __init__(self):
        self.cur_dir = str(Path.home())
        self.dic_file = ""
        self.exp_dir = str(Path.home())
        self.x = 800
        self.y = 800
        self.width = 640
        self.height = 480

    def SetShape(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def readIniFile(self):
        ini_file_name = str(Path.cwd()) + "/" + self.INIT_FILE_NAME
        try:
            with open(ini_file_name, 'r') as f:
                self.set_new_cur_dir(f.readline().strip())
                self.set_new_dic_file(f.readline().strip())
                self.set_new_exp_dir(f.readline().strip())
                self.x = int(f.readline())
                self.y = int(f.readline())
                self.width = int(f.readline())
                self.height = int(f.readline())
            log.log("Inifile read.")
        except (FileNotFoundError, ValueError, IOError) as e:
            self.writeIniFile()
            log.warn(str(e))

    def writeIniFile(self):
        ini_file_name = str(Path.cwd()) + "/" + self.INIT_FILE_NAME
        try:
            with open(ini_file_name, 'w') as f:
                f.write(self.cur_dir + "\n")
                f.write(self.dic_file + "\n")
                f.write(self.exp_dir + "\n")
                f.write(str(self.x) + "\n")
                f.write(str(self.y) + "\n")
                f.write(str(self.width) + "\n")
                f.write(str(self.height) + "\n")
            log.log("Inifile written.")
        except IOError as e:
            log.warn(str(e))

    def set_new_cur_dir(self, new_dir):
        if validate_dir(new_dir):
            self.cur_dir = new_dir
        log.log("New cur_dir = " + self.cur_dir)
    
    def set_new_dic_file(self, new_file):
        if validate_file(new_file):
            self.dic_file = new_file
        log.log("New dic_file = " + self.dic_file)

    def set_new_exp_dir(self, new_dir):
        if validate_dir(new_dir):
            self.exp_dir = new_dir
        log.log("New exp_dir = " + self.exp_dir)

class CreateTestMainWindow(QMainWindow):
    """Main Window for creating vocabulary test"""
    
    vocab_html = ""
    dictionary_text = ""
    
    def __init__(self):
        super().__init__()
        log.date()
        log.log("Application started.")
        self.ini_file = IniFile()
        try:
            self.ini_file.readIniFile()
        except IOError as e:
            self.ShowErrorMessage("Ini File Access Error", str(e))
        self.vocabulary_files = VocabularyFiles()
        self.initUI()
        self.tryToReadDictionary()

    def initUI(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(4)
        self.setCentralWidget(self.tableWidget)
        self.statusBar = self.statusBar()
        
        self.openAct = QAction('&OpenKindleBookmark', self)
        self.openAct.setShortcut('Ctrl+O')
        self.openAct.setStatusTip('Open Kindle Bookmark File')
        self.openAct.triggered.connect(self.openBookmark)
        
        openDictAct = QAction('&OpenDictionary', self)
        openDictAct.setStatusTip('Open Dictionary Text File')
        openDictAct.triggered.connect(self.openDictionary)

        self.exportQuizAct = QAction('&Export', self)
        self.exportQuizAct.setStatusTip('Export Quiz to a file')
        self.exportQuizAct.triggered.connect(self.exportQuiz)
        
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(openDictAct)
        fileMenu.addAction(self.exportQuizAct)
        fileMenu.addAction(exitAct)

        self.createAct = QAction('&CreateAnkiTest', self)
        self.createAct.setStatusTip('Create Anki test')
        self.createAct.triggered.connect(self.createTest)

        createMenu = menubar.addMenu('&CreateTest')
        createMenu.addAction(self.createAct)
        
        self.setGeometry(self.ini_file.width, self.ini_file.height, self.ini_file.x, self.ini_file.y)
        self.setWindowTitle('Vocab Quiz')
        # self.setWindowIcon(QIcon('web.png'))
        self.updateStatus()
        self.show()

    def openBookmark(self):
        fname = QFileDialog.getOpenFileName(self, 'Please Open Kindle Bookmark File', self.ini_file.cur_dir, "HTML files (*.html)")

        if not fname[0]:
            self.updateStatus()
            return
        parent_path = str(Path(fname[0]).parent.absolute())
        self.ini_file.set_new_cur_dir(parent_path)
        if not self.vocabulary_files.ReadKindleBookmakFile(fname[0]):
            self.ShowErrorMessage("Book Mark Open Fail", self.vocabulary_files.error_message)
            self.updateStatus()
            return
        log.log("Bookmark file " + fname[0] + " read.")
        self.showTable()
        if not self.vocabulary_files.word_list:
            self.ShowErrorMessage("Vocabulary list empty", "The read file had no vocabulary words. Possibly you read a wrong file");
            self.updateStatus()
            return
        self.createTest()
        self.updateStatus()

    def openDictionary(self):
        fname = QFileDialog.getOpenFileName(self, 'Please open a dictionary file exported from Eijiro', self.ini_file.dic_file, "Text files (*.txt | *.csv)")
        if not fname[0]:
            self.updateStatus()
            return False
        if not self.vocabulary_files.ReadDictionaryFile(fname[0]):
            self.ShowErrorMessage("Dictionary Open Fail", self.vocabulary_files.error_message)
            self.updateStatus()
            return False
        self.ini_file.set_new_dic_file(fname[0])
        log.log("Dictionary file " + fname[0] + " read.")
        self.updateStatus()
        return True

    def createTest(self):
        if not (self.vocabulary_files.dictionary_text):
            log.warn("Dictionary is empty when createTest was called.")
            self.updateStatus()
            return
        self.vocabulary_files.word_list = self.getWordsFromTable()
        self.vocabulary_files.CreateTest(self.statusBar)
        self.showQuiz()
        self.updateStatus()
        log.log("Quiz created successfully.")
        QMessageBox.information(self, "Quiz Creation Report", self.vocabulary_files.report_text)

    def exportQuiz(self):
        word_list, quiz = self.getQuizFromTable()
        self.vocabulary_files.word_list = word_list
        self.vocabulary_files.quiz = quiz
        if not word_list:
            self.showErrorMessage("Vocabulary word list is empty")
            self.updateStatus()
            return
        fname = QFileDialog.getSaveFileName(self, 'Export Anki Test File', self.ini_file.exp_dir)
        if not fname[0]:
            return
        if not self.vocabulary_files.ExportQuizFile(fname[0]):
            self.ShowErrorMessage("Quiz Export Fail", self.vocabulary_files.error_message)
            return
        parent_path = str(Path(fname[0]).parent.absolute())
        self.ini_file.set_new_exp_dir(parent_path)
        self.updateStatus()
        log.log("Quiz exported to " + fname[0])

    def getWordsFromTable(self):
        rows = self.tableWidget.rowCount()
        word_list = []
        for row in range(rows):
            word = self.tableWidget.item(row, 0).text()
            word.strip(' ')
            if word:
                word_list.append(word)
        return word_list

    def getQuizFromTable(self):
        rows = self.tableWidget.rowCount()
        columns = self.tableWidget.columnCount()
        word_list = []
        quiz = {}
        for row in range(rows):
            word = self.tableWidget.item(row, 0).text()
            word_list.append(word)
            defs = []
            for column in range(1, columns):
                cell = self.tableWidget.item(row, column)
                if cell is None:
                    continue
                definition = cell.text()
                if definition:
                    defs.append(definition)
            quiz[word] = defs
        return word_list, quiz
    
    def ShowErrorMessage(self, title, error_text):
        log.warn("Message box shown.\n" + title + ": " + error_text)
        QMessageBox.warning(self, title, error_text)

    def updateStatus(self):
        if not self.vocabulary_files.dictionary_text:
            self.statusBar.showMessage("Please load dictionary file.")
            self.exportQuizAct.setDisabled(True)
            self.createAct.setDisabled(True)
        elif not self.vocabulary_files.word_list:
            self.statusBar.showMessage("Please load the vocabulary list file.")
            self.exportQuizAct.setDisabled(True)
            self.createAct.setDisabled(True)
        elif not self.vocabulary_files.quiz:
            self.statusBar.showMessage("You can run create test.")
            self.createAct.setDisabled(False)
            self.exportQuizAct.setDisabled(True)
        else:
            self.statusBar.showMessage("You can export the quiz now.")
            self.createAct.setDisabled(False)
            self.exportQuizAct.setDisabled(False)

    def showTable(self):
        rows = len(self.vocabulary_files.word_list)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(2)
        for index, word in enumerate(self.vocabulary_files.word_list):
            self.tableWidget.setItem(index, 0, QTableWidgetItem(word))
        self.update()
 
    def showQuiz(self):
        rows = len(self.vocabulary_files.quiz.keys())
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(2)
        for index, word in enumerate(self.vocabulary_files.word_list):
            self.tableWidget.setItem(index, 0, QTableWidgetItem(word))
            defs = self.vocabulary_files.quiz[word]
            if (len(defs) + 1 > self.tableWidget.columnCount()):
                self.tableWidget.setColumnCount(len(defs) + 1)
            for def_index, definition in enumerate(defs):
                self.tableWidget.setItem(index, 1 + def_index, QTableWidgetItem(definition))
        self.update()
    
    def tryToReadDictionary(self):
        if not self.vocabulary_files.ReadDictionaryFile(self.ini_file.dic_file):
            self.openDictionary()
        self.updateStatus()

    def myExitHandler(self):
        try:
            self.ini_file.writeIniFile()
        except IOError as e:
            log.warn("Ini File Access Error\n" + str(e))
        log.log("Application end.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CreateTestMainWindow()
    app.aboutToQuit.connect(ex.myExitHandler)
    sys.exit(app.exec_())
    

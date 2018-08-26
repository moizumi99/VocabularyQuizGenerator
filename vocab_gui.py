#!/usr/bin/python3
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
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtWidgets import QAction, qApp, QMessageBox, QFileDialog, QTextBrowser

class VocabularyFiles:
    """Stores file related information"""

    def __init__(self):
        self.vocab_list = []
        self.dictionary_text = ""
        self.quiz = {}
        self.unused_words = []
        self.error_message = ""

    def ReadKindleBookmakFile(self, fname):
        if fname:
            try:
                with open(fname, 'r') as f:
                    vocab_html = f.readlines()
            except (FileNotFoundError, UnicodeDecodeError, IOError) as e:
                self.error_message = "Error reading " + fname
                self.error_message += "\n" + str(e)
                return False
            self.vocab_list = ExtractWords(vocab_html)
        return True

    def ReadDictionaryFile(self, fname):
        try:
            with codecs.open(fname, 'r', 'utf-16') as eijiro_file:
                self.dictionary_text = eijiro_file.readlines()
        except (FileNotFoundError, IOError) as e:
            self.error_message = "Error opening " + fname
            self.error_message += "\n" + str(e)
            return False
        cnt = 0
        for line in self.dictionary_text:
            print(line)
            cnt += 1
            if (cnt > 100):
                break
        return True

    def CreateTest(self):
        start_point = 0
        self.quiz = {}
        self.unused_words = []
        for word in self.vocab_list:
            defs, word, start_point = FindDefinitions(word, self.dictionary_text, start_point)
            if defs:
                self.quiz[word] = defs
            else:
                self.unused_words.append(word)
        print(str(len(self.vocab_list) - len(self.unused_words)) + " words found")
        print(str(len(self.unused_words)) + " words not found")
    
    def ExportQuizFile(self, fname):
        try:
            with codecs.open(fname, 'w', 'utf-8') as fout:
                for word, defs in self.quiz.items():
                    outtxt = word.strip() + "\t" + ('<br>'.join(defs)) + "\n"
                    fout.write(outtxt)
            return True
        except IOError as e:
            self.error_message = "Error opening " + fname
            self.error_message += "\n" + str(e)
            return False
        return False

def FindDefinitions(word, dic, start_point=0):
    REMOVE_LIST = [u'◆', u'\ ・', u'【変化】', u'【分節】', u'【＠】']
    
    deflist = []
    # find the first element that meets the condition
    # Don't want to evaluate all elements, so starting from 'startpoint'
    index = start_point
    prev_start_point = (index - 1 + len(dic)) % len(dic)
    while(index != prev_start_point and (not dic[index].startswith(word+' ///'))):
        index = (index + 1) % len(dic)
    if index != prev_start_point: # found
        l = dic[index][len(word)+4:]
        for r in REMOVE_LIST:
            ii = l.find(r)
            l = l[:ii] if (ii >= 0) else l
        for d in l.split('\\'):
            if 0 <= d.find(u'＝<→') < d.find(u'>'):
                dl, _, _ = FindDefinitions(d[d.find(u'＝<→') + 3:d.find(u'>')], dic)
                deflist.extend(dl)
            elif d.strip():
                deflist.append(d.strip())
    else: # word not found, try plural
        if (word[-1] == 's'):
            deflist, plural, _ = FindDefinitions(word[:-1], dic)
            if (len(deflist)>0):
                print(word+' not found. ' + plural + ' is used instead.')
                word = plural
    prev_start_point = (index + 1) % len(dic) # next starting point
    return deflist, word, prev_start_point


def ExtractWords(html_text):
    """Extract English words from html text"""

    word_list = []
    for line in html_text:
        index = line.find(u'<div class=\'noteText\'>')
        if index < 0:
            continue
        line = line[index + 22:]
        index = line.find(u'</div>')
        if index < 0:
            continue
        word = line[:index].rstrip(',').rstrip('.').rstrip()
        word_list.append(word)
    print(str(len(word_list)) + " words extracted from " + str(len(html_text)) + " lines")
    return word_list

def validate_dir(target_dir):
    try:
        new_path = Path(target_dir)
        if new_path.is_dir():
            return True
    except IOError:
        return False
    return False

class IniFile:
    """Stores initial values"""
    
    INIT_FILE_NAME = ".vocab.ini"
    
    def __init__(self):
        self.cur_dir = str(Path.home())
        self.dic_dir = str(Path.home())
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
        ini_file_name = str(Path.home()) + "/" + self.INIT_FILE_NAME
        try:
            with open(ini_file_name, 'r') as f:
                self.set_new_cur_dir(f.readline().strip())
                self.set_new_dic_dir(f.readline().strip())
                self.set_new_exp_dir(f.readline().strip())
                self.x = int(f.readline())
                self.y = int(f.readline())
                self.width = int(f.readline())
                self.height = int(f.readline())
        except (FileNotFoundError, ValueError, IOError) as e:
            self.writeIniFile()
            print(str(e))

    def writeIniFile(self):
        ini_file_name = str(Path.home()) + "/" + self.INIT_FILE_NAME
        try:
            with open(ini_file_name, 'w') as f:
                f.write(self.cur_dir + "\n")
                f.write(self.dic_dir + "\n")
                f.write(self.exp_dir + "\n")
                f.write(str(self.x) + "\n")
                f.write(str(self.y) + "\n")
                f.write(str(self.width) + "\n")
                f.write(str(self.height) + "\n")
        except IOError as e:
            print(str(e))

    def set_new_cur_dir(self, new_dir):
        if validate_dir(new_dir):
            self.cur_dir = new_dir
        print("New cur_dir = " + self.cur_dir)
    
    def set_new_dic_dir(self, new_dir):
        if validate_dir(new_dir):
            self.dic_dir = new_dir
        print("New dir_dir = " + self.dic_dir)

    def set_new_exp_dir(self, new_dir):
        if validate_dir(new_dir):
            self.exp_dir = new_dir
        print("New exp_dir = " + self.exp_dir)


class CreateTestMainWindow(QMainWindow):
    """Main Window for creating vocabulary test"""
    
    vocab_html = ""
    dictionary_text = ""
    
    def __init__(self):
        super().__init__()
        self.ini_file = IniFile()
        try:
            self.ini_file.readIniFile()
        except IOError as e:
            self.ShowErrorMessage("Ini File Access Error", str(e))
        self.vocabulary_files = VocabularyFiles()
        self.initUI()

        
    def initUI(self):

        self.textBrowser = QTextBrowser()
        self.setCentralWidget(self.textBrowser)
        self.statusBar()
        
        openAct = QAction('&OpenKindleBookmark', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open Kindle Bookmark File')
        openAct.triggered.connect(self.openBookmark)
        
        openDictAct = QAction('&OpenDictionary', self)
        openDictAct.setStatusTip('Open Dictionary Text File')
        openDictAct.triggered.connect(self.openDictionary)

        exportQuizAct = QAction('&Export', self)
        exportQuizAct.setStatusTip('Export Quiz to a file')
        exportQuizAct.triggered.connect(self.exportQuiz)
        
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAct)
        fileMenu.addAction(openDictAct)
        fileMenu.addAction(exportQuizAct)
        fileMenu.addAction(exitAct)

        createAct = QAction('&CreateAnkiTest', self)
        createAct.setStatusTip('Create Anki test')
        createAct.triggered.connect(self.createTest)

        createMenu = menubar.addMenu('&CreateTest')
        createMenu.addAction(createAct)
        
        self.setGeometry(self.ini_file.width, self.ini_file.height, self.ini_file.x, self.ini_file.y)
        self.setWindowTitle('Vocab Quiz')
        # self.setWindowIcon(QIcon('web.png'))        
        self.show()

    def openBookmark(self):
        fname = QFileDialog.getOpenFileName(self, 'Kindle Bookmark File', self.ini_file.cur_dir)

        if not fname[0]:
            return
        if not self.vocabulary_files.ReadKindleBookmakFile(fname[0]):
            self.ShowErrorMessage("Book Mark Open Fail", self.vocabulary_files.error_message)
            return
        self.textBrowser.setText("\n".join(self.vocabulary_files.vocab_list))
        p = Path(fname[0]).parent
        self.ini_file.set_new_cur_dir(str(p.absolute() ))

    def openDictionary(self):
        fname = QFileDialog.getOpenFileName(self, 'Eijiro csv file', self.ini_file.dic_dir)
        if not fname[0]:
            return
        if not self.vocabulary_files.ReadDictionaryFile(fname[0]):
            self.ShowErrorMessage("Dictionary Open Fail", self.vocabulary_files.error_message)
            return
        p = Path(fname[0]).parent
        self.ini_file.set_new_dic_dir(str(p.absolute() ))

    def exportQuiz(self):
        fname = QFileDialog.getSaveFileName(self, 'Export Anki Test File', self.ini_file.exp_dir)
        if not fname[0]:
            return
        if not self.vocabulary_files.ExportQuizFile(fname[0]):
            self.ShowErrorMessage("Quiz Export Fail", self.vocabulary_files.error_message)
            return
        p = Path(fname[0]).parent
        self.ini_file.set_new_exp_dir(str(p.absolute() ))
        
    def ShowErrorMessage(self, title, error_text):
        QMessageBox.warning(self, title, error_text)

    def createTest(self):
        self.vocabulary_files.CreateTest()

    def myExitHandler(self):
        try:
            self.ini_file.writeIniFile()
        except IOError as e:
            self.ShowErrorMessage("Ini File Access Error", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CreateTestMainWindow()
    app.aboutToQuit.connect(ex.myExitHandler)
    sys.exit(app.exec_())
    

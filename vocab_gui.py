#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This example shows an icon
in the titlebar of the window.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, qApp, QMessageBox, QFileDialog, QTextBrowser
from PyQt5.QtGui import QIcon

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 800
        self.x = 600
        self.y = 400
        self.initUI()
        
    def initUI(self):

        self.textBrowser = QTextBrowser()
        self.setCentralWidget(self.textBrowser)
        self.statusBar()
        
        openAct = QAction('&Open', self)
        openAct.setShortcut('Ctrl+F')
        openAct.setStatusTip('Open Kindle Bookmark File')
        openAct.triggered.connect(self.openMessage)
        
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAct)
        fileMenu.addAction(exitAct)
        
        self.setGeometry(self.width, self.height, self.x, self.y)
        self.setWindowTitle('Vocab Quiz')
        # self.setWindowIcon(QIcon('web.png'))        
        self.show()

    def openMessage(self):
        fname = QFileDialog.getOpenFileName(self, 'Kindle Bookmark File', '/home')

        if fname[0]:
            try:
                with open(fname[0], 'r') as f:
                    data = f.read()
                    self.textBrowser.setText(data)
            except:
                print("Error reading " + fname[0])
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    

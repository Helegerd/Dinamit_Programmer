# Coding:utf-8
# pip install xlwt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextBrowser
from PyQt5.QtGui import QFont
from random import randint, choice
import xlwt
import sys

def getTextDirection(axis='x', direct='+'):
    '''для того, чтобы обыяснять по-человечески, куда может двигаться исполнитель'''
    if axis == 'x':
        return {'+': 'вправо', '-': 'влево'}[direct]
    if axis == 'y':
        return {'+': 'вверх', '-': 'вниз'}[direct]

def getTextStartPos(movex='+', movey='+'):
    '''по тому, как движется, возвращает по-русски, где начально находился исполнитель'''
    if movey == '+':
        return 'нижний ' + {'+': 'левый', '-': 'правый'}[movex]
    if movey == '-':
        return 'верхний ' + {'+': 'левый', '-': 'правый'}[movex]

def getTextEndPos(movex='+', movey='+'):
    '''по тому, как движется, возвращает по-русски, где в итоге окажется исполнитель'''
    if movey == '+':
        return 'верхний ' + {'+': 'правый', '-': 'левый'}[movex]
    if movey == '-':
        return 'нижний ' + {'+': 'правый', '-': 'левый'}[movex]


class MW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 800)
        self.setWindowTitle('Ячейки тоже плотют нологи')
        self.dist = self.height() // 80 # основное расстояние между виджетами в px
        self.possibleModsarr = ['ЧИСЛОВАЯ СТРОКА', 'ПРОСТО РОБОТ', 'РОБОТ С ПЕРЕГОРОДКАМИ', 'ЛАДЬЯ', 'ЧЕЛЯБИНСКИЙ САМОКАТИК', 'РАНДОМ']  # кнопки для выбора режима
        self.currMod = 0  # номер режима, соответсвующий self.possibleModsarr
        self.answer = 0  # ответ на вопрос
        
        # основной экран
        #
        # кнопка, чтобы перейти к тренажёру
        self.nextbtn = QPushButton(self)
        self.nextbtn.resize(400, 70)
        self.nextbtn.move(200, 710)
        self.nextbtn.setFont(QFont('Arial', 15))
        self.nextbtn.setText('НАЧАТЬ')
        self.nextbtn.clicked.connect(self.changeWin)
        #
        # кнопки выбора режима
        self.chooseModbuttons = []
        for mod in self.possibleModsarr:
            self.chooseModbuttons.append(QPushButton(self))
            self.chooseModbuttons[-1].resize(self.width() // 2, self.height() // 16)
            self.chooseModbuttons[-1].move(self.width() // 4, (self.height() // 16) * (len(self.chooseModbuttons) - 1) + self.dist * len(self.chooseModbuttons))
            self.chooseModbuttons[-1].setFont(QFont('Arial', 12))
            self.chooseModbuttons[-1].clicked.connect(self.chooseMode)
            self.chooseModbuttons[-1].setText(mod)
        self.chooseModbuttons[0].setStyleSheet('background-color: rgb(150, 250, 150)')
        self.chooseModbuttons[1].setStyleSheet('background-color: rgb(150, 250, 150)')
        self.chooseModbuttons[2].setStyleSheet('background-color: rgb(50, 200, 50)')
        self.chooseModbuttons[3].setStyleSheet('background-color: rgb(250, 250, 50)')
        self.chooseModbuttons[4].setStyleSheet('background-color: rgb(250, 50, 50)')
        
        # экран обучения
        #
        # кнопка возврата в основной экран
        self.backbtn = QPushButton(self)
        self.backbtn.resize(400, 70)
        self.backbtn.move(200, 710)
        self.backbtn.setFont(QFont('Arial', 15))
        self.backbtn.clicked.connect(self.changeWin)
        self.backbtn.setText('НАЗАД')
        #
        # виджет для условия
        self.tasktext = QTextBrowser(self)
        self.tasktext.resize((self.width() // 100) * 90, (self.height() // 100) * 70)
        self.tasktext.move((self.width() // 100) * 5, self.dist)
        self.tasktext.setFont(QFont('Arial', 10))
        #
        # кнопка обновлений
        self.refreshbtn = QPushButton(self)
        self.refreshbtn.resize(self.width() // 5, self.height() // 16)
        self.refreshbtn.move(self.width() // 10, self.tasktext.y() + self.tasktext.height() + self.dist)
        self.refreshbtn.setFont(QFont('Arial', 15))
        self.refreshbtn.setText('ОБНОВИТЬ')
        self.refreshbtn.clicked.connect(self.refresh)
        #
        # поле ввода ответа
        self.ansedit = QLineEdit(self)
        self.ansedit.resize(self.width() // 5, self.height() // 16)
        self.ansedit.move(self.refreshbtn.width() + self.refreshbtn.x() + self.dist,
                             self.tasktext.y() + self.tasktext.height() + self.dist)
        self.ansedit.setFont(QFont('Arial', 15))
        #
        # кнопка проверки
        self.checkbtn = QPushButton(self)
        self.checkbtn.resize(self.width() // 5, self.height() // 16)
        self.checkbtn.move(self.ansedit.width() + self.ansedit.x() + self.dist,
                              self.tasktext.y() + self.tasktext.height() + self.dist)
        self.checkbtn.setFont(QFont('Arial', 15))
        self.checkbtn.clicked.connect(self.check)
        self.checkbtn.setText('ПРОВЕРИТЬ')
        #
        # лабел верно/неверно
        self.checklab = QLabel(self)
        self.checklab.resize(self.width() // 5, self.height() // 16)
        self.checklab.move(self.checkbtn.width() + self.checkbtn.x() + self.dist,
                              self.tasktext.y() + self.tasktext.height() + self.dist)
        self.checklab.setFont(QFont('Arial', 15))
        #
        self.widgets2 = [self.backbtn, self.tasktext, self.refreshbtn, self.ansedit, self.checkbtn, self.checklab]  # виджеты, которые на экране обучения
        for wid in self.widgets2:
            wid.hide()
            
    def chooseMode(self):
        '''выбор режима'''
        if self.sender() == self.chooseModbuttons[-1]:
            self.currMod = randint(0, len(self.chooseModbuttons) - 2)
        else:
            for i in range(len(self.chooseModbuttons) - 1):
                if self.chooseModbuttons[i] == self.sender():
                    self.currMod = i
                    break
        
    def changeWin(self):
        '''для смены окон'''
        if self.sender() == self.nextbtn:
            for wid in [self.nextbtn] + self.chooseModbuttons:
                wid.hide()
            
            for wid in self.widgets2:
                wid.show()
        if self.sender() == self.backbtn:
            for wid in [self.nextbtn] + self.chooseModbuttons:
                wid.show()
            
            for wid in self.widgets2:
                wid.hide()
        self.refresh()
        
    def refresh(self):
        '''обновляет задание текущего режима'''
        taskText = ''  # текст условия для показа
        try:
            if self.currMod == 0:  # числовая строка
                taskText = taskText + 'Имеется последовательность натуральных чисел, записанная в виде строки таблицы в файле info18.xls. '
                line = [randint(1, 100) for _i in range(randint(20, 40))]  # рассматриваемая строка
                # запись в info18.xls
                wb = xlwt.Workbook()
                ws = wb.add_sheet('18')
                for i in range(len(line)):
                    ws.write(0, i, line[i])
                wb.save('info18.xls')
                task = choice(['dist+>', 'dist+<', 'next>', 'next<'])  # что ищем
                if task[0] == 'n':  # если ищем длинейшую цепочку
                    if task[-1] == '<':
                        taskText = taskText + 'Укажите наибольшую длину последовательности из идущих подряд чисел, где каждое последущее меньше предыдущего.'
                    elif task[-1] == '>':
                        taskText = taskText + 'Укажите наибольшую длину последовательности из идущих подряд чисел, где каждое последущее больше предыдущего.'
                    maxque = 1  # максимальная последовательность
                    currque = 1  # текущая последовательность
                    for i in range(1, len(line)):
                        if task[-1] == '<' and line[i] < line[i - 1] or\
                           task[-1] == '>' and line[i] > line[i - 1]:
                            currque += 1
                        else:
                            currque = 1
                            continue
                        if currque > maxque:
                            maxque = currque
                    self.answer = maxque
                if task[0] == 'd':  # если ищем количество пар
                    dist = randint(3, 5)  # минимальное расстояние между членами строки, из которых состовляются пары
                    modelnum = randint(80, 160)
                    taskText = taskText + f'Рассматриваются суммы чисел, чьи порядковые номера различаются не менее чем на {dist}. '
                    if task[-1] == '<':
                        taskText = taskText + f'Укажите количество тех рассматриваемых сумм, которые меньше {modelnum}.'
                    elif task[-1] == '>':
                        taskText = taskText + f'Укажите количество тех рассматриваемых сумм, которые больше {modelnum}.'
                    pairnum = 0  # количество искомых пар
                    for i in range(len(line) - dist):
                        for j in range(i + dist, len(line)):
                            if task[-1] == '<' and line[i] + line[j] < modelnum or\
                               task[-1] == '>' and line[i] + line[j] > modelnum:
                                pairnum += 1
                    self.answer = pairnum
            
            if self.currMod == 1:  # просто робот
                taskText = taskText + 'Исполнитель робот перемещается по прямоугольному полю, состоящему из ячеек, в которых находятся монеты номиналом от 1 до 100. '
                n = randint(10, 30)  # ширина
                m = randint(10, 30)  # высота
                field = [[randint(1, 100) for _i in range(n)] for _j in range(m)]  # поле для робота
                # запись в info18.xls
                wb = xlwt.Workbook()
                ws = wb.add_sheet('18')
                for i in range(m):
                    for j in range(n):
                        ws.write(i, j, field[i][j])
                wb.save('info18.xls')
                taskText = taskText + 'Ячейки этого поля записаны в таблицу info18.xls. '
                movements = [choice(['+', '-']), choice(['+', '-'])]  # возвожные движения робота; "+" -- вверх/вправо, "-" -- вниз/влево
                movements.append(movements[0] + movements[1])  # диагональ
                taskText = taskText + 'Начальная позиция робота: ' + getTextStartPos(movements[0], movements[1]) + ' угол. '
                taskText = taskText + f'Робот может перемещаться в следующих направлениях: {getTextDirection("x", movements[0])}, {getTextDirection("y", movements[1])} и по диагонали {getTextDirection("y", movements[1])}-{getTextDirection("x", movements[0])}. '
                taskText = taskText + 'Робот не может выходить за пределы поля. '
                taskText = taskText + 'Оказавшись на любой ячейке (включая начальную и конечную), робот собирает все находящиеся в ней монеты. '
                startcell = {'++': (0, m - 1), '+-': (0, 0), '-+': (n - 1, m - 1), '--': (n - 1, 0)}[movements[-1]]  # начальная позиция робота
                task = choice(['min', 'max'])  # что надо найти
                taskText = taskText + 'Укажите ' + {'min': 'минимальную', 'max': 'максимальную'}[task] + ' сумму, которую робот соберёт, достигнув ' + getTextEndPos(movements[0], movements[1]) + ' угол. '
                helpfield = [[0 for _i in range(n)] for _k in range(m)]  # вспомогательное поле
                helpfield[startcell[1]][startcell[0]] = field[startcell[1]][startcell[0]]
                # заполнение строки, в которой находится стартовая позиция
                if movements[0] == '+':
                    for i in range(1, n):
                        helpfield[startcell[1]][i] = field[startcell[1]][i] + helpfield[startcell[1]][i - 1]
                elif movements[0] == '-':
                    for i in range(n - 2, -1, -1):
                        helpfield[startcell[1]][i] = field[startcell[1]][i] + helpfield[startcell[1]][i + 1]
                # заполнение столбца, в котором находится стартовая позиция
                if movements[1] == '+':
                    for i in range(m - 2, -1, -1):
                        helpfield[i][startcell[0]] = field[i][startcell[0]] + helpfield[i + 1][startcell[0]]
                if movements[1] == '-':
                    for i in range(1, m):
                        helpfield[i][startcell[0]] = field[i][startcell[0]] + helpfield[i - 1][startcell[0]]
                # заполнение полей
                rangex = {'+': range(1, n), '-': range(n - 2, -1, -1)}[movements[0]]  # в каком порядке смотреть в строках
                rangey = {'+': range(m - 2, -1, -1), '-': range(1, m)}[movements[1]]  # в каком порядке смотреть строки
                changex = {'+': 1, '-': -1}[movements[0]]  # как ходят по абциссе
                changey = {'+': -1, '-': 1}[movements[1]]  # как ходят по ординате
                for rownum in rangey:
                    for colomnnum in rangex:
                        if task == 'min':
                            helpfield[rownum][colomnnum] = field[rownum][colomnnum] + min([helpfield[rownum - changey][colomnnum],
                                                                                           helpfield[rownum][colomnnum - changex],
                                                                                           helpfield[rownum - changey][colomnnum - changex]])
                        if task == 'max':
                            helpfield[rownum][colomnnum] = field[rownum][colomnnum] + max([helpfield[rownum - changey][colomnnum],
                                                                                           helpfield[rownum][colomnnum - changex],
                                                                                           helpfield[rownum - changey][colomnnum - changex]])
                endcell = {'++': (n - 1, 0), '+-': (n - 1, m - 1), '-+': (0, 0), '--': (0, m - 1)}[movements[-1]]  # конечная позиция робота
                for row in helpfield:
                    print(row)
                self.answer = helpfield[endcell[1]][endcell[0]]
        except:
            taskText = 'Закройте таблицу info18.xls и обновите.'
        self.tasktext.setText(taskText)  # записываем условие в браузер
    
    def check(self):
        '''проверяем, правильный ли ответ введён'''
        try:
            if self.answer == int(self.ansedit.text()):
                self.checklab.setText('<p style="color: rgb(100, 250, 100);">ВЕРНО!</p>')
            else:
                self.checklab.setText(f'<p style="color: rgb(250, 100, 100);">{self.answer}!</p>')
        except:
            self.checklab.setText('повторите ввод')
                
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec_())
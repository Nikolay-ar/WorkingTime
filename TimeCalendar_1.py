from PyQt5.QtWidgets import QApplication, QDialog, QTableView, QStyledItemDelegate,\
    QLCDNumber,QPushButton ,QVBoxLayout, QHBoxLayout, QLabel, QLayout, QHeaderView
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTime, QTimer, Qt, QModelIndex
from time import strftime
from PyQt5.QtSql import QSqlQuery, QSqlDatabase, QSqlTableModel
from datetime import datetime, timedelta

box_style = ("border: 4px solid \'#2DACEB\';\n"
                                       "border-radius: 9px;\n"
                                       "font-size: 16px;\n"
                                    #    "margin: 10px;\n"
                                       "background: #FFFFFF")
bt_style = ("QPushButton {\n"
            "border: 0;\n"
            "border-radius: 8px;\n"
            "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
            "stop:0 rgb(45, 172, 235), stop:1 rgb(72,102,175));\n"
            "color: #FFFFFF;\n"
            "padding: 8px 16px;\n"
            "font: 16px; }\n"
            "QPushButton:pressed {background-color:rgb(31,101,163) ; }"
            )
lb_style = ("font: 14px; color: green")

tableName = "timing_1"

HEIGHT_ROW = 30
# HEIGHT_ROW = 32

class AlignDelegate(QStyledItemDelegate):
    """Выравнивает текст в ячейке по центру."""
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class NameDwDelegate(AlignDelegate):   # Унаследован от AlignDelegate с выравниванием
    """Заменяет возвращаемый номер названием дня недели."""
    def __init__(self):  # Инициализация класса NameDwDelegate
        super().__init__()  # Инициализация родительского класса QStyledItemDelegate
        self.dw = ["ВС", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]

    def displayText(self, text, locale):
        return self.dw[text]
        # return str(text)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("customdb.sqlite")
db.open()
query = QSqlQuery()

def createFirstData():
    # query.exec_(f"DROP TABLE {tableName}")
    query.exec_(f"CREATE TABLE IF NOT EXISTS {tableName}( \n"
        "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, \n"
        "dw INTEGER, \n"      
        "day DATETIME, \n"     
        "startTime DATETIME, \n" # дата и время в формате DATETIME
        "endTime DATETIME) "      
        )
    query.exec_(f"INSERT INTO {tableName} (id, dw, day, startTime) \n"
                "VALUES(1, strftime('%w', 'now'), strftime('%d-%m', 'now'), \n"
                "strftime('%H:%M', 'now', 'localtime'))")
createFirstData()

def getCountLastDW():                               # количество выше id где dw >= 1
    query.exec(f"SELECT COUNT(*) FROM {tableName} WHERE id >= (SELECT MAX(id) FROM {tableName} WHERE dw = 1)")
    query.last()
    query.value
    countLastDW, = range(1)
    return query.value(countLastDW)

def getCountRecordsDB():
    query.exec(f"SELECT COUNT(*) FROM {tableName}")
    query.last()
    query.value
    res, = range(1)
    return query.value(res)

# numFinalRow = datetime.today().isoweekday()
# if 
countRowsDW = getCountLastDW()
# numFinalRow = 2
numRecordsDB = getCountRecordsDB()

if countRowsDW == 0:    # Если нет ни одного дня недели
    countRowsDW = numRecordsDB


class Model(QSqlTableModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setTable(tableName)
        self.workedOvertime = []


    def columnCount(self, parent=QModelIndex()):
        # this is probably obvious
        # since we are adding a virtual column, we need one more column
        return super(Model, self).columnCount()+1

    def rowCount(self, parent=QModelIndex()):
        return super(Model, self).rowCount()+1


    def data(self, index, role=Qt.DisplayRole):

        if role == Qt.DisplayRole and index.column()==5:
            # 2nd column is our virtual column.
            # if we are there, we need to calculate and return the value
            # we take the first two columns, get the data, turn it to integer and sum them
            # [0] at the end is necessary because pyqt returns value and a bool
            # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qvariant.html#toInt
            # return sum(self.data(self.index(index.row(), i)) for i in range(2))
            
            numColumnStart = 3
            numColumnEnd = 4
            a = index.row()
            if index.row() < countRowsDW: # to do
                dataStart, dataEnd = self.data(self.index(index.row(), numColumnStart)), self.data(self.index(index.row(), numColumnEnd))
                if (dataStart and dataEnd) not in ['', None]:
                    hours = balanceTimeStrHM( "-" + dataStart, dataEnd, "-0:45")
                    timeOverNorm = balanceTimeStrHM('-8:00', hours)
                    if len(self.workedOvertime) == a:
                        self.workedOvertime.append(timeOverNorm)

                    print(type(timeOverNorm))
                    print(timeOverNorm)
                    return hours
                else:
                    return ''
                # return hours
            else:
                print (self.workedOvertime)
                res = balanceTimeStrHM(*self.workedOvertime)
                # return "dflg"
                return res
            
        elif role == Qt.DisplayRole and index.column()==4 :
            if index.row() == countRowsDW:  # to do
                return "Time Balance:"
        if index.column() > 5:
            # if we are past 2nd column, we need to shift it to left by one
            # to get the real value
            index = self.index(index.row(), index.column()-1)
        # get the value from base implementation
        return super(Model, self).data(index, role)

    def submit(self):
        if self.editStrategy() == QSqlTableModel.OnRowChange or self.editStrategy() == QSqlTableModel.OnFieldChange:
            self.workedOvertime = []
            res = self.submitAll()
            return res
        return True

class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.opn = False

        self.setWindowTitle("Work mode")
        self.setWindowIcon(QIcon("python.png"))
        self.move(850,80)
        self.timeStartFromBD = datetime.strptime(getLastRecord(), "%H:%M")
 
        # create QLCDNumber object
        self.lcd = QLCDNumber()
        # self.lcd.setStyleSheet('color: green')
        self.lcd.setMinimumHeight(130)
        self.lcd.display(self.timeStartFromBD.strftime("%H:%M"))     # Отображаем время начала работы
        lb_lcd = QLabel("Начало рабочего времени",self.lcd)
        lb_lcd.setStyleSheet(lb_style)
        lb_lcd.move(13, 3)

        self.lcd_1 = QLCDNumber()
        # self.lcd_1.setStyleSheet('color: red')
        self.lcd_1.setMinimumHeight(130)

        # "2024-04-03 07:53:41" в таком формате хранится время в бд
        self.endWorkTime = self.timeStartFromBD + timedelta(hours = 8, minutes = 45)
        self.lcd_1.display(self.endWorkTime.strftime("%H:%M"))   

        lb_lcd_1 = QLabel("Окончание рабочего дня",self.lcd_1)
        lb_lcd_1.setStyleSheet(lb_style)
        lb_lcd_1.move(13, 3)

        self.lcdTime = QLCDNumber()
        self.lcdTime.display(strftime("%H"+":"+"%M"))
        self.lcdTime.setMinimumHeight(130)
        lb_lcdTime = QLabel("Текущее время",self.lcdTime)
        lb_lcdTime.setStyleSheet(lb_style)
        lb_lcdTime.move(13, 3)

        self.lcdWorkedHours = QLCDNumber()
        self.lcdWorkedHours.setMinimumHeight(130)
        self.lcdWorkedHours.setStyleSheet('color: blue')

        lb_lcdWorkedHours = QLabel("Отработано часов",self.lcdWorkedHours)
        lb_lcdWorkedHours.setStyleSheet(lb_style)
        lb_lcdWorkedHours.move(13, 3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Time)
        self.timer.start(1000)
 # -------------------------------------------------------------------------------------------
        #this is our button with the stylesheet
        self.button = QPushButton("Календарь")
        self.button.setStyleSheet(bt_style)
        self.button.clicked.connect(self.viewTable)

        self.fixStart = QPushButton("Record start -5 min", self)
        self.fixStart.setStyleSheet(bt_style)
        self.fixStart.resize(140, 50)
        self.fixStart.clicked.connect(self.addStartTime)
        self.fixEnd = QPushButton("Record end +5 min", self)
        self.fixEnd.setStyleSheet(bt_style)
        self.fixEnd.resize(140, 50)
        self.fixEnd.clicked.connect(self.addEndTime)
 # -------------------------------------------------------------------------------------------

        VleftBox = QVBoxLayout()
        VleftBox.addWidget(self.lcd)
        VleftBox.addWidget(self.lcdWorkedHours)

        VrightBox = QVBoxLayout()
        VrightBox.addWidget(self.lcd_1)
        VrightBox.addWidget(self.lcdTime)


        HdispleyBox = QHBoxLayout()
        HdispleyBox.addLayout(VleftBox)
        HdispleyBox.addLayout(VrightBox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.button)
        hbox.addWidget(self.fixStart)
        hbox.addWidget(self.fixEnd)

        self.model = Model(self)
        # self.model.setTable(tableName)

        # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.setHeaderData(5, Qt.Horizontal, "hours [8:00]")
        # позволяет использовать автопрокрутку при большем чем 256 строк
        self.model.rowsInserted.connect(lambda: QTimer.singleShot(0, self.view.scrollToBottom))

        self.model.setFilter(f"id in(select id from {tableName} ORDER BY id DESC LIMIT {countRowsDW}) " )
        
        
        
        self.model.select()
        countRowsInModel = self.model.rowCount()
        print(f"Количество строк в модели: {countRowsInModel}")


        self.view = QTableView()
        self.view.setModel(self.model)

        delegate = AlignDelegate(self.view)
        self.view.setItemDelegate(delegate)

        delegateRenderDw = NameDwDelegate()
        self.view.setItemDelegateForColumn(1, delegateRenderDw)

        # self.view.resizeColumnsToContents()

        self.view.setStyleSheet(box_style)
        self.view.horizontalHeader().setStyleSheet("border-width : 0px 0px 2px 0px; \n"
                                                   "border-radius: 0px;")
        self.view.setColumnHidden(0, True)
        self.view.setColumnWidth(1, 45)
        self.view.setColumnWidth(2, 50)
        # self.view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # растяуть секцию на всю рамку
        self.view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # растяуть секцию на всю рамку
        self.view.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) # растяуть секцию на всю рамку
        self.view.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch) # растяуть секцию на всю рамку

        self.view.verticalHeader().setVisible(False)
        # self.view.setFixedHeight(127)
        aa = self.model.rowCount()
        self.view.setFixedHeight((HEIGHT_ROW + 7) + HEIGHT_ROW * (countRowsDW + 1) )

        # self.view.setFixedHeight(HEIGHT_ROW * (countRowsDW + 2) +4)
        self.view.setSpan(countRowsDW, 1, 1, 3)  # row, column, rowCount, columnCount to do
        
      
       
        # vbox layout object
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(HdispleyBox)
        self.vbox.addLayout(hbox)
        self.vbox.addWidget(self.view)

        self.vbox.setSizeConstraint(QLayout.SetFixedSize)
        # self.vbox.update()
        self.view.hide()

        self.setLayout(self.vbox)

    def viewTable(self):
        if self.opn == False:
            self.view.show()
            self.view.scrollToBottom()

            self.opn = True
        else:
            self.view.hide()
            self.opn = False

    def Time(self):
        time = QTime.currentTime()
        text = time.toString('hh:mm')
        self.lcdTime.display(text)

        self.timeStartFromBD = datetime.strptime(getLastRecord(), "%H:%M")
        self.endWorkTime = self.timeStartFromBD + timedelta(hours = 8, minutes = 45)
        delta_45 = timedelta(minutes=45)
        difference = datetime.now() - self.timeStartFromBD
        if difference.seconds > 60 * 45:
            difference -= delta_45
        seconds = difference.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        self.lcdWorkedHours.display(f'{hours}:{minutes}')
        self.lcd.display(self.timeStartFromBD.strftime("%H:%M"))    # Обновляем отображение времени начала работы
        self.lcd_1.display(self.endWorkTime.strftime("%H:%M"))      # Обновляем отображение времени конца работы
        if 8 <= hours < 9 :
            if 0 <= minutes < 15:
                self.lcdWorkedHours.setStyleSheet('color: green')
            elif 15 <= minutes < 30:
                self.lcdWorkedHours.setStyleSheet('color: yellow')
            else:
                self.lcdWorkedHours.setStyleSheet('color: red')
        elif hours < 8:
            self.lcdWorkedHours.setStyleSheet('color: blue')
        else:
            self.lcdWorkedHours.setStyleSheet('color: red')
        
    
    def addStartTime(self):
        global countRowsDW
        DayFromBD = datetime.strptime(getLastRecordDate(), "%d-%m").date().replace(year=2000)
        DayMonthNow = datetime.now().date().replace(year=2000)
        if DayFromBD != DayMonthNow:
            query.exec_(f"INSERT INTO {tableName} (dw, day, startTime) VALUES(strftime('%w', 'now'), strftime('%d-%m', 'now'), strftime('%H:%M', 'now', '-5 minutes', 'localtime'))")
            countRowsDW = getCountLastDW()
            numRecordsDB = getCountRecordsDB()
            if countRowsDW == 0:    # Если нет ни одного дня недели
                countRowsDW = numRecordsDB

            self.model.setFilter(f"id in(select id from {tableName} ORDER BY id DESC LIMIT {countRowsDW}) " )

            self.model.select()
            self.view.setFixedHeight((HEIGHT_ROW + 7) + HEIGHT_ROW * (countRowsDW + 1) )          
            self.view.setSpan(countRowsDW-1, 1, 1, 1)  # row, column, rowCount, columnCount to do
            self.view.setSpan(countRowsDW, 1, 1, 3)  # row, column, rowCount, columnCount to do
            self.view.scrollToBottom()
            print("adding row")
        else:
            print("Сегодняшняя дата начала рабочего времени уже проставлена")

    def addEndTime(self):        
        query.exec_(f"UPDATE {tableName} SET endTime = strftime('%H:%M', 'now', '+5 minutes', 'localtime') \n"
                    f"WHERE id = (SELECT MAX(ID)  FROM {tableName})")
        self.model.workedOvertime = []
        self.model.select()
        self.view.scrollToBottom()
        print("UPDATing row")

        # shutdown()

import os
def shutdown():
    return os.system("shutdown /s /t 1")

def balanceTimeStrHM(*args):
    mysum = timedelta()

    for i in args:
        (h, m) = i.split(':')
        if i.startswith('-'):
            d = timedelta(hours = int(h), minutes = -int(m))
        else:
            d = timedelta(hours=int(h), minutes=int(m))
        mysum += d
    total_seconds = mysum.total_seconds()
    if mysum < timedelta(0):
        hours = str(int(-total_seconds // 3600)).zfill(2)
        minutes = str(int((-total_seconds % 3600) // 60)).zfill(2)
        return f"-{hours}:{minutes}"
    else:
        hours = str(int(total_seconds // 3600)).zfill(2)
        minutes = str(int((total_seconds % 3600) // 60)).zfill(2)
        return f"{hours}:{minutes}"


def getLastRecord():
    query.exec(f"SELECT startTime FROM {tableName} WHERE id = (SELECT MAX(ID) FROM {tableName})")
    query.last()
    query.value
    startTime, = range(1)
    stime = query.value(startTime)
    if stime == "":
        return '00:00'
    return stime

def getLastRecordDate():
    query.exec(f"SELECT day FROM {tableName} WHERE id = (SELECT MAX(ID) FROM {tableName})")
    query.last()
    query.value
    startTime, = range(1)
    stime = query.value(startTime)
    return stime
    # return '00-00'

App = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(App.exec())

# Сгенерировать exe файл: $ pyinstaller TimeCalendar_1.py --onefile --windowed

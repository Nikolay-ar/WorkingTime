from PyQt5.QtWidgets import QApplication, QDialog, QTableView, QStyledItemDelegate,\
    QLCDNumber,QPushButton ,QVBoxLayout, QHBoxLayout, QLabel, QLayout, QHeaderView, QItemDelegate
import sys, os, sqlite3
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTime, QTimer, Qt
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


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.opn = False
        self.setWindowTitle("  Work mode")
        self.setWindowIcon(QIcon("hammer-shape_icon-icons.com_70718.png"))
        self.move(850,80)
        self.timeStartFromBD = datetime.strptime(getLastRecord(), "%H:%M")

        # create QLCDNumber object
        self.lcd = QLCDNumber()
        self.lcd.setStyleSheet('color: green')
        self.lcd.setMinimumHeight(145)
        self.lcd.display(self.timeStartFromBD.strftime("%H:%M"))     # Отображаем время начала работы
        lb_lcd = QLabel("Начало рабочего времени",self.lcd)
        lb_lcd.setStyleSheet(lb_style)
        lb_lcd.move(13, 3)

        self.lcd_1 = QLCDNumber()
        self.lcd_1.setStyleSheet('color: red')
        self.lcd_1.setMinimumHeight(145)

        # "2024-04-03 07:53:41" в таком формате хранится время в бд
        endWorkTime = self.timeStartFromBD + timedelta(hours = 8, minutes = 45)
        self.lcd_1.display(endWorkTime.strftime("%H:%M"))

        lb_lcd_1 = QLabel("Окончание рабочего дня",self.lcd_1)
        lb_lcd_1.setStyleSheet(lb_style)
        lb_lcd_1.move(13, 3)

        self.lcdTime = QLCDNumber()
        self.lcdTime.display(strftime("%H"+":"+"%M"))
        self.lcdTime.setMinimumHeight(145)
        lb_lcdTime = QLabel("Текущее время",self.lcdTime)
        lb_lcdTime.setStyleSheet(lb_style)
        lb_lcdTime.move(13, 3)

        self.lcdWorkedHours = QLCDNumber()
        self.lcdWorkedHours.setMinimumHeight(145)
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
        self.fixStart = QPushButton("Record start", self)
        self.fixStart.setStyleSheet(bt_style)
        self.fixStart.resize(140, 50)
        self.fixStart.clicked.connect(self.addStartTime)
        self.fixEnd = QPushButton("Record end and shutdown", self)
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

        self.model = QSqlTableModel(self)
        self.model.setTable(tableName)
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.setQuery(QSqlQuery(f"SELECT id, dw, day, startTime, endTime, numHours, strftime('%H:%M', 'now') FROM {tableName}"))
        # self.model.setHeaderData(0, Qt.Horizontal, "id")
        # self.model.setHeaderData(1, Qt.Horizontal, "dw")
        # self.model.setHeaderData(2, Qt.Horizontal, "Начало рабочего дня")
        # self.model.setHeaderData(3, Qt.Horizontal, "Конец рабочего дня")
        # позволяет использовать автопрокрутку при большем чем 256 строк
        self.model.rowsInserted.connect(lambda: QTimer.singleShot(0, self.view.scrollToBottom))
        self.model.setFilter(f"id in(select id from {tableName} ORDER BY id DESC \n"    # Кол-во отображаемых строк
                             f"LIMIT (select dw from {tableName} where id = (SELECT MAX(ID) FROM {tableName}))) " )
        # print(self.model.filter())
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)

        delegateAlign = AlignDelegate(self.view)
        self.view.setItemDelegate(delegateAlign)

        delegateRenderDw = NameDwDelegate()
        self.view.setItemDelegateForColumn(1, delegateRenderDw)


        self.view.setStyleSheet(box_style)
        self.view.horizontalHeader().setStyleSheet("border-width : 0px 0px 2px 0px; \n"
                                                   "border-radius: 0px;")
        self.view.setColumnWidth(0, 45)
        self.view.setColumnWidth(1, 45)
        self.view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # растяуть секцию на всю рамку
        self.view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # растяуть секцию на всю рамку
        self.view.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) # растяуть секцию на всю рамку

        self.view.verticalHeader().setVisible(False)
        self.view.setMinimumHeight(200)

        # vbox layout object
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(HdispleyBox)
        self.vbox.addLayout(hbox)
        self.vbox.addWidget(self.view)
        self.vbox.setSizeConstraint(QLayout.SetFixedSize)
        self.view.hide()

        self.setLayout(self.vbox)

    def viewTable(self):
        """Вкл - Выкл отображения таблицы"""
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
        difference = datetime.now() - self.timeStartFromBD
        seconds = difference.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        self.lcdWorkedHours.display(f'{hours}:{minutes}')

    def addStartTime(self):
        query = QSqlQuery()
        query.exec_(f"INSERT INTO {tableName} (dw, day, startTime) \n"
                    f"VALUES(strftime('%w', 'now'), strftime('%d-%m', 'now'), strftime('%H:%M', 'now', 'localtime'))")
        self.model.select()
        self.view.scrollToBottom()
        # print("adding row")


#  time('now', 'localtime') \n"
    def addEndTime(self):
        query = QSqlQuery()
        query.exec_(f"UPDATE {tableName} SET endTime = strftime('%H:%M', 'now', 'localtime') \n"
                    f"WHERE id = (SELECT MAX(ID)  FROM {tableName})")
        self.model.select()
        self.view.scrollToBottom()
        # print("UPDATing row")

        # shutdown()

def shutdown():
    return os.system("shutdown /s /t 1")

def createFakeData():
    # db = QSqlDatabase.addDatabase("QSQLITE")
    # db.setDatabaseName("customdb.sqlite")
    # db.open()

    query = QSqlQuery()
    query.exec_(f"DROP TABLE {tableName}")
    query.exec_(f"CREATE TABLE IF NOT EXISTS {tableName}( \n"
        "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, \n"
        "dw INTEGER, \n"
        "day DATETIME, \n"
        "startTime DATETIME, \n" # дата и время в формате DATETIME
        "endTime DATETIME, \n"
        "numHours)"
        )
    query.exec_(f"INSERT INTO {tableName} (id, dw, day, startTime) \n"
                "VALUES(1, strftime('%w', 'now'), day('now'), \n"
                "strftime('%H:%M', 'now', 'localtime'))")
    db.close()

def getLastRecord():
    query = QSqlQuery()
    query.exec(f"SELECT startTime FROM {tableName} \n"
               f"WHERE id = (SELECT MAX(ID) FROM {tableName})")
    query.last()
    startTime, = range(1)
    stime = query.value(startTime)
    return stime


App = QApplication(sys.argv)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("customdb.sqlite")
db.open()
createFakeData()

window = Window()
window.show()
sys.exit(App.exec())

# Сгенерировать exe файл: $ pyinstaller TimeCalendar.py --onefile --windowed

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QStatusBar, QMenuBar, QTextBrowser, \
    QTextEdit, QPushButton, QTableWidget, QLineEdit, QTableWidgetItem, QLabel
import sqlite3


class MyWidget(QMainWindow):  # главный экран, на нем находится экран авторизации, это необходимо для того,
    def __init__(self, *args):  # что бы базой данных владели только больницы
        super().__init__()
        self.initUI(args)
        self.con = sqlite3.connect("Medecine.db")

    def initUI(self, args):
        self.setGeometry(300, 300, 499, 527)
        self.setWindowTitle('Электронная карта')

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setGeometry(80, 30, 341, 111)
        self.textBrowser.setText(
            'Приветствуем Вас, пользователь!\nПожалуйста, авторизируйтесь,\nвведя номер больницы и персональный код больницы')

        self.textBrowser_2 = QTextBrowser(self)
        self.textBrowser_2.setGeometry(110, 160, 61, 31)
        self.textBrowser_2.setText('Номер')

        self.textBrowser_3 = QTextBrowser(self)
        self.textBrowser_3.setGeometry(340, 160, 41, 31)
        self.textBrowser_3.setText('Код')

        self.textEdit = QLineEdit(self)
        self.textEdit.setGeometry(40, 210, 191, 31)

        self.textEdit_2 = QLineEdit(self)
        self.textEdit_2.setGeometry(270, 210, 191, 31)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(0, 0, 499, 21)
        self.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(self)

        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(150, 250, 201, 41)
        self.pushButton.setText('Авторизация')
        self.pushButton.clicked.connect(self.avtorizate)

    def avtorizate(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT number FROM Hospitals
                    WHERE key = ?""", (self.textEdit_2.text(),)).fetchall()
        if result:
            if self.textEdit.text() == result[0][0]:
                self.lookingWindow = LookingWindow(self)
                self.lookingWindow.show()
                self.close()
            else:
                valid = QMessageBox.question(self, '', "Неверный логин или пароль", QMessageBox.Ok)
        elif (self.textEdit.text() == 'Hell') and (self.textEdit_2.text() == '666'):
            self.dead = Dead(self)
            self.dead.show()
        else:
            valid = QMessageBox.question(self, '', "Неверный логин или пароль", QMessageBox.Ok)


class LookingWindow(QWidget):  # Второе окно - тут пользователь видит саму базу данных пациентов
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)
        self.con = sqlite3.connect("Medecine.db")

    def initUI(self, args):
        self.setWindowTitle('Список пациентов')
        self.setGeometry(300, 300, 499, 527)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(0, 120, 501, 371)

        self.textEdit = QLineEdit(self)
        self.textEdit.setGeometry(0, 50, 90, 31)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Поиск')
        self.pushButton.clicked.connect(self.update_result)
        self.pushButton.setGeometry(10, 90, 481, 21)

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setText('Выйти')
        self.pushButton_2.clicked.connect(self.back)
        self.pushButton_2.setGeometry(440, 0, 61, 41)

        self.pushButton_3 = QPushButton(self)
        self.pushButton_3.setText('Войти в профиль')
        self.pushButton_3.clicked.connect(self.openProfile)
        self.pushButton_3.setGeometry(210, 50, 110, 31)

        self.pushButton_4 = QPushButton(self)
        self.pushButton_4.setText('Добавить пациента')
        self.pushButton_4.clicked.connect(self.add_profile)
        self.pushButton_4.setGeometry(330, 50, 110, 31)

        self.pushButton_5 = QPushButton(self)
        self.pushButton_5.setText('Удалить пациента')
        self.pushButton_5.clicked.connect(self.del_profile)
        self.pushButton_5.setGeometry(100, 50, 100, 31)

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setText('Введите СНИЛС пациента для поиска\nнажмите на \'поиск\', что бы обновить список')
        self.textBrowser.setGeometry(0, 0, 431, 41)

        self.titles = None

    def update_result(self):
        cur = self.con.cursor()
        if self.textEdit.text() == '':
            result = cur.execute("""SELECT СНИЛС, Имя, Фамилия, Отчество, Телефон FROM Profile""").fetchall()
        else:
            result = cur.execute("""SELECT СНИЛС, Имя, Фамилия, Отчество, Телефон FROM Profile WHERE СНИЛС = ?""",
                                 (self.textEdit.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['СНИЛС', 'Имя', 'Фамилия', 'Отчество', 'Номер тел.'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def openProfile(self):  # Функция для открытия профиля с расширенной информацией пациента
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if len(ids) == 1:
            self.check = Check(self, ids[0])
            self.check.show()
        else:
            pass

    def add_profile(self):  # функиция для добавления профиля
        self.addProf = AddProfile(self)
        self.addProf.show()

    def del_profile(self):  # функция для удаления профиля(в крайних случаях)
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if len(ids) == 1:
            self.delProf = DelProfile(self, ids[0])
            self.delProf.show()
        else:
            pass

    def back(self):
        self.myWidg = MyWidget(self)
        self.myWidg.show()
        self.close()


class DelProfile(QWidget):  # окно для удаления профиля пациента
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Удалить профиль')
        self.setGeometry(300, 300, 300, 300)
        self.con = sqlite3.connect("Medecine.db")
        cur = self.con.cursor()

        self.snils = QLabel(args[-1], self)
        self.snils.setGeometry(0, 0, 0, 0)

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setText('Введите свидетельство о смерти для продолжения')
        self.textBrowser.setGeometry(0, 0, 300, 49)

        self.textEdit = QLineEdit(self)
        self.textEdit.setGeometry(0, 50, 91, 31)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Подтвердить')
        self.pushButton.clicked.connect(self.del_profile)
        self.pushButton.setGeometry(0, 90, 300, 50)

    def del_profile(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT Имя, Фамилия, Отчество FROM Profile WHERE СНИЛС = ?""",
                             (self.snils.text(),)).fetchall()
        cur.execute(
            """INSERT INTO deleted(СНИЛС, Свидетельство, Имя, Фамилия, Отчество) VALUES(?, ?, ?, ?, ?)""",
            (self.snils.text(), self.textEdit.text(), result[0][0], result[0][1], result[0][2]))
        self.con.commit()
        cur.execute("""DELETE from Profile WHERE СНИЛС =?""", (self.snils.text(),))
        cur.execute("""DELETE from Relative WHERE СНИЛС =?""", (self.snils.text(),))
        cur.execute("""DELETE from MedHosp WHERE СНИЛС =?""", (self.snils.text(),))
        cur.execute("""DELETE from Analysis WHERE СНИЛС =?""", (self.snils.text(),))
        # cur.execute("""DELETE from Diagnosis WHERE СНИЛС =?""", (self.snils.text(),))
        self.con.commit()
        self.close()
        valid = QMessageBox.question(self, '', "Профиль удален", QMessageBox.Ok)


class AddProfile(QWidget):  # окно для добавления профиля пациента
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Добавить профиль')
        self.setGeometry(300, 300, 499, 527)
        self.con = sqlite3.connect("Medecine.db")

        self.textEdit = QLineEdit(self)
        self.textEdit.setText('СНИЛС')
        self.textEdit.setGeometry(0, 50, 91, 31)

        self.textEdit_2 = QLineEdit(self)
        self.textEdit_2.setText('Имя')
        self.textEdit_2.setGeometry(100, 50, 81, 31)

        self.textEdit_3 = QLineEdit(self)
        self.textEdit_3.setText('Фамилия')
        self.textEdit_3.setGeometry(190, 50, 91, 31)

        self.textEdit_4 = QLineEdit(self)
        self.textEdit_4.setText('Отчество')
        self.textEdit_4.setGeometry(290, 50, 111, 31)

        self.textEdit_5 = QLineEdit(self)
        self.textEdit_5.setText('Дата рождения в формате 00.00.0000')
        self.textEdit_5.setGeometry(290, 150, 201, 31)

        self.textEdit_6 = QLineEdit(self)
        self.textEdit_6.setText('Паспортные данные')
        self.textEdit_6.setGeometry(0, 100, 111, 31)

        self.textEdit_7 = QLineEdit(self)
        self.textEdit_7.setText('Прописка')
        self.textEdit_7.setGeometry(0, 150, 251, 31)

        self.textEdit_8 = QLineEdit(self)
        self.textEdit_8.setText('Номер телефона в формате +70000000000')
        self.textEdit_8.setGeometry(120, 100, 300, 31)

        self.pushButtonn = QPushButton(self)
        self.pushButtonn.setText('Добавить профиль')
        self.pushButtonn.clicked.connect(self.add)

    def add(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT * FROM Profile WHERE СНИЛС = ?""", (self.textEdit.text(),)).fetchall()
        if result:
            valid = QMessageBox.question(self, '', "Профиль уже есть в базе данных", QMessageBox.Ok)
        else:
            cur.execute(
                """INSERT INTO Profile(СНИЛС, Имя, Фамилия, Отчество, Дата, Паспорт, Адрес, Телефон) VALUES (?, ?, ?, ?, 
                ?, ?, ?, ?)""",
                (self.textEdit.text(), self.textEdit_2.text(), self.textEdit_3.text(), self.textEdit_4.text(),
                 self.textEdit_5.text(), self.textEdit_6.text(), self.textEdit_7.text(), self.textEdit_8.text()))
            self.con.commit()
            self.close()
            valid = QMessageBox.question(self, '', "Профиль добавлен", QMessageBox.Ok)


class Check(QWidget):  # окно для подтверждения перехода в профиль пациента
    def __init__(self, *args):  # необходимо, так как в профиле находтся личная информация
        super().__init__()  # проверка осуществляется с помощью кода, высланного на номер
        self.initUI(args)  # пациента. здесь это не реализоованно до конца
        # код доступа - 1234

    def initUI(self, args):
        self.setWindowTitle('Проверка')
        self.setGeometry(300, 300, 300, 300)
        self.con = sqlite3.connect("Medecine.db")
        cur = self.con.cursor()

        self.snils = QLabel(args[-1], self)
        self.snils.setGeometry(0, 0, 0, 0)

        result = cur.execute("""SELECT * FROM Profile WHERE СНИЛС = ?""", (self.snils.text(),)).fetchall()

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setText(
            'На номер {} было отправлено сообщение для подтверждения\nвведите код из сообщения для продолжения'.format(
                result[0][7]))
        self.textBrowser.setGeometry(0, 0, 300, 49)

        self.textEdit = QLineEdit(self)
        self.textEdit.setGeometry(0, 50, 91, 31)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Подтвердить')
        self.pushButton.clicked.connect(self.check_result)
        self.pushButton.setGeometry(0, 90, 300, 50)

    def check_result(self):
        if self.textEdit.text() == '1234':
            self.profileWindow = ProfileWindow(self, self.snils.text())
            self.profileWindow.show()
            self.close()
        else:
            valid = QMessageBox.question(self, '', "Неверный код", QMessageBox.Ok)


class ProfileWindow(QWidget):  # окно для отображения профиля пациента
    def __init__(self, *args):  # можно выбрать один из типов информации
        super().__init__()  # (реализовано не всё)
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Профиль пациента')
        self.setGeometry(300, 300, 730, 530)
        self.con = sqlite3.connect("Medecine.db")
        cur = self.con.cursor()

        self.snils = QLabel(args[-1], self)
        self.snils.setGeometry(0, 0, 0, 0)

        self.table = QLabel(self)
        self.snils.setGeometry(0, 0, 0, 0)

        result = cur.execute("""SELECT * FROM Profile WHERE СНИЛС = ?""", (self.snils.text(),)).fetchall()

        self.fio = [result[0][1], result[0][2], result[0][3]]
        self.textEdit = QTextBrowser(self)
        self.textEdit.setText(' '.join(self.fio))
        self.textEdit.setGeometry(0, 0, 431, 41)

        self.tableWidget = QTableWidget(self)
        # self.tableWidget.itemChanged.connect(self.item_changed)
        self.tableWidget.setGeometry(0, 81, 730, 389)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Личные данные')
        self.pushButton.clicked.connect(self.update_profile)
        self.pushButton.setGeometry(0, 46, 142, 30)

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setText('Родственники')
        self.pushButton_2.clicked.connect(self.update_relative)
        self.pushButton_2.setGeometry(147, 46, 142, 30)

        self.pushButton_3 = QPushButton(self)
        self.pushButton_3.setText('Мед учреждения')
        self.pushButton_3.clicked.connect(self.update_medHosp)
        self.pushButton_3.setGeometry(294, 46, 142, 30)

        self.pushButton_4 = QPushButton(self)
        self.pushButton_4.setText('Анализы')
        self.pushButton_4.clicked.connect(self.update_analysis)
        self.pushButton_4.setGeometry(441, 46, 142, 30)

        self.pushButton_5 = QPushButton(self)
        self.pushButton_5.setText('Диагнозы')
        self.pushButton_5.clicked.connect(self.nooooooo)
        self.pushButton_5.setGeometry(588, 46, 142, 30)

        self.pushButton_6 = QPushButton(self)
        self.pushButton_6.setText('Обновить')
        self.pushButton_6.clicked.connect(self.nooooooo)
        self.pushButton_6.setGeometry(0, 475, 730, 25)

        self.pushButton_7 = QPushButton(self)
        self.pushButton_7.setText('Сохранить')
        self.pushButton_7.clicked.connect(self.nooooooo)
        self.pushButton_7.setGeometry(0, 505, 730, 25)

        self.modified = {}
        self.titles = None

    def nooooooo(self):
        valid = QMessageBox.question(self, '', "Функция в разработке", QMessageBox.Ok)

    def update_profile(self):
        self.table.setText('Profile')
        cur = self.con.cursor()
        result = cur.execute("Select Дата, Паспорт, Адрес, Телефон from Profile WHERE СНИЛС=?",
                             (self.snils.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Дата рождения', 'Паспорт', 'Адрес', 'Номер тел.'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def update_relative(self):
        self.table.setText('Relative')
        cur = self.con.cursor()
        result = cur.execute("Select Роль, Имя, Фамилия, Отчество, снилс from Relative WHERE СНИЛС=?",
                             (self.snils.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Роль', 'Имя', 'Фамилия', 'Отчество', 'СНИЛС'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def update_medHosp(self):
        self.table.setText('MedHosp')
        cur = self.con.cursor()
        result = cur.execute("Select Название, Когда, Врач, Диагноз, Лечение, Запись from MedHosp WHERE СНИЛС=?",
                             (self.snils.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(
            ['мед. учреждение', 'Дата', 'Врач', 'Диагноз', 'Лечение', 'Запись врача'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def update_diagnosis(self):
        self.table.setText('Diagnosis')
        cur = self.con.cursor()
        result = cur.execute("Select Диагноз, Где, Когда, Лечение from Diagnosis WHERE СНИЛС=?",
                             (self.snils.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Диагноз', 'Мед.учреждение', 'Дата', 'Лечение'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def update_analysis(self):
        self.table.setText('Analysis')
        cur = self.con.cursor()
        result = cur.execute("Select Зачем, Где, Когда, Результаты from Analysis WHERE СНИЛС=?",
                             (self.snils.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['Тема анализа', 'Мед.учреждение', 'Дата', 'Результаты'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            cur = self.con.cursor()
            que = "UPDATE {} SET\n".format(self.table.text())
            for key in self.modified.keys():
                que += "{}='{}'\n".format(key, self.modified.get(key))
            que += "WHERE id = ?"
            cur.execute(que, (self.spinBox.text(),))
            self.con.commit()


class Dead(QWidget):  # а сюда Вам не надо. это уже задел на рут права
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Мертвые Души')
        self.setGeometry(300, 300, 530, 530)
        self.con = sqlite3.connect("Medecine.db")
        cur = self.con.cursor()

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(0, 0, 530, 530)

        result = cur.execute("""Select * from deleted""").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['СНИЛС?', 'Свидетельство?', 'Имя?', 'Фамилия?', 'Отчество?'])
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())

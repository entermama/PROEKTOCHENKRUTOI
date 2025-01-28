import sys
import io
import sqlite3
import datetime

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QLabel, QDialog, QLineEdit, QMessageBox, QTextEdit, QPushButton
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap

global like

template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="enabled">
   <bool>true</bool>
  </property>
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1582</width>
    <height>863</height>
   </rect>
  </property>
  <property name="font">
   <font>
    <weight>50</weight>
    <italic>false</italic>
    <bold>false</bold>
    <underline>false</underline>
    <strikeout>false</strikeout>
    <stylestrategy>PreferDefault</stylestrategy>
   </font>
  </property>
  <property name="cursor">
   <cursorShape>ArrowCursor</cursorShape>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <property name="autoFillBackground">
   <bool>true</bool>
  </property>
  <widget class="QCalendarWidget" name="calendarWidget">
   <property name="geometry">
    <rect>
     <x>360</x>
     <y>170</y>
     <width>451</width>
     <height>541</height>
    </rect>
   </property>
  </widget>
  <widget class="QComboBox" name="comboBox">
   <property name="geometry">
    <rect>
     <x>820</x>
     <y>170</y>
     <width>401</width>
     <height>31</height>
    </rect>
   </property>
  </widget>
  <widget class="QPushButton" name="button_like">
   <property name="enabled">
    <bool>true</bool>
   </property>
   <property name="geometry">
    <rect>
     <x>820</x>
     <y>510</y>
     <width>191</width>
     <height>91</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <weight>75</weight>
     <bold>true</bold>
    </font>
   </property>
   <property name="text">
    <string>Избранное</string>
   </property>
  </widget>
  <widget class="QPushButton" name="button_reboot">
   <property name="enabled">
    <bool>true</bool>
   </property>
   <property name="geometry">
    <rect>
     <x>1020</x>
     <y>510</y>
     <width>201</width>
     <height>91</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <weight>75</weight>
     <bold>true</bold>
    </font>
   </property>
   <property name="text">
    <string>Обновить</string>
   </property>
  </widget>
  <widget class="QLabel" name="label">
   <property name="geometry">
    <rect>
     <x>820</x>
     <y>250</y>
     <width>391</width>
     <height>251</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <pointsize>50</pointsize>
    </font>
   </property>
   <property name="text">
    <string/>
   </property>
  </widget>
  <widget class="QPushButton" name="add_to_like_button">
   <property name="geometry">
    <rect>
     <x>1090</x>
     <y>610</y>
     <width>131</width>
     <height>101</height>
    </rect>
   </property>
   <property name="text">
    <string>Добавить в избранное</string>
   </property>
  </widget>
  <widget class="QPushButton" name="del_from_like_button">
   <property name="geometry">
    <rect>
     <x>820</x>
     <y>610</y>
     <width>131</width>
     <height>101</height>
    </rect>
   </property>
   <property name="text">
    <string>Удалить из избранного</string>
   </property>
  </widget>
  <widget class="QPushButton" name="add_to_news">
   <property name="geometry">
    <rect>
     <x>960</x>
     <y>610</y>
     <width>121</width>
     <height>101</height>
    </rect>
   </property>
   <property name="text">
    <string>Добавить новость</string>
   </property>
  </widget>
  <widget class="QLabel" name="label_2">
   <property name="geometry">
    <rect>
     <x>820</x>
     <y>190</y>
     <width>401</width>
     <height>91</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <pointsize>16</pointsize>
     <weight>75</weight>
     <italic>false</italic>
     <bold>true</bold>
     <underline>false</underline>
     <strikeout>false</strikeout>
    </font>
   </property>
   <property name="text">
    <string>Ниже будет отображаться новость</string>
   </property>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

#класс для добавления новостей
class News(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новость")
        self.setMinimumSize(400, 300)
        self.setupUI()
        self.conn = sqlite3.connect("data_base")

    def setupUI(self):
        layout = QVBoxLayout()


        self.theme_label = QLabel("Тема:")
        self.theme_input = QLineEdit()
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_input)

        self.date_label = QLabel("Дата(дд мм гг):")
        self.date_input = QLineEdit()
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_input)

        self.news_label = QLabel("Новость:")
        self.news_input = QTextEdit()
        layout.addWidget(self.news_label)
        layout.addWidget(self.news_input)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить новость")
        self.save_button.clicked.connect(self.save_news)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_news(self):
       theme = self.theme_input.text()
       date = self.date_input.text()
       news_text = self.news_input.toPlainText()

       cursor = self.conn.cursor()
       users = cursor.execute(f"SELECT data FROM news WHERE theme = '{theme}'").fetchall()
       for i in users:
           if str(date) == str(i[0]):
               QMessageBox.critical(self, "Ошибка БД", f"Новость на эту дату уже добавлена")
               exit()

       if not all([theme, news_text]):
            QMessageBox.warning(self, "Предупреждение", "Заполните все поля")
            return

       try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO news (newss, data, theme) VALUES ('%s', '%s', '%s')" % (str(news_text), str(date), str(theme)))
            self.conn.commit()
            QMessageBox.information(self, "Успех", "Новость сохранена")

            self.theme_input.clear()
            self.date_input.clear()
            self.news_input.clear()


       except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при сохранении: {e}")


#класс для избранного
class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.sizeHint()

    def initUI(self):
        self.setWindowTitle("Избранное")
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        conn = sqlite3.connect('data_base')
        cur = conn.cursor()
        result = cur.execute("SELECT like_news FROM like")

        count = 0
        for row in result:
            count += 1
            news_text = row[0]
            label = QLabel(f'Новость номер {count}: {news_text}')
            self.layout.addWidget(label)

        conn.close()


#основной класс
class Proekt(QMainWindow):
    def __init__(self):
        # база
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)

        # иконка
        icon = QIcon("icon.png")
        self.setWindowIcon(icon)

        # размер
        self.sizeHint()
        if hasattr(QtCore.Qt, 'icon.png'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        # коннекты и виджеты
        self.button_like.clicked.connect(self.action_button_like)
        self.button_reboot.clicked.connect(self.action_dat_base)
        self.add_to_like_button.clicked.connect(self.action_add_button_like)
        self.del_from_like_button.clicked.connect(self.action_del_button_like)
        self.add_to_news.clicked.connect(self.action_add_news)

        self.comboBox.addItems(["Политика", "Спорт", "Экономика", "Яндекс-лицей"])
        self.label.setWordWrap(True)

        # дизайн
        self.add_to_news.setStyleSheet("""
                            QPushButton {
                                background-color: #f0f0f0;  /* Светло-серый фон */
                                border: 2px solid #ddd;  /* Светло-серая граница */
                                border-radius: 5px; /* Скругленные углы */
                                padding: 10px;
                                min-width: 50px; /* Минимальный размер */
                                min-height: 50px; /* Минимальный размер */
                                font-family: Arial, sans-serif; /* Шрифт */
                                font-size: 11px;
                            }

                            QPushButton:hover {
                                background-color: #e0e0e0; /* Светлее при наведении */
                                border-color: #ccc;
                            }

                            QPushButton:pressed {
                                background-color: #d0d0d0; /* Еще светлее при нажатии */
                            }

                            QPushButton:disabled {
                                background-color: #f5f5f5;
                                border-color: #eee;
                            }


                        """)

        self.add_to_like_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 500px 200px; border-radius: 5px;")
        self.del_from_like_button.setStyleSheet(
            "background-color: #cb2821; color: white; padding: 500px 200px; border-radius: 5px;")
        self.button_reboot.setStyleSheet("""
                            QPushButton {
                                background-color: #f0f0f0;  /* Светло-серый фон */
                                border: 2px solid #ddd;  /* Светло-серая граница */
                                border-radius: 5px; /* Скругленные углы */
                                padding: 10px;
                                min-width: 50px; /* Минимальный размер */
                                min-height: 50px; /* Минимальный размер */
                                font-family: Arial, sans-serif; /* Шрифт */
                                font-size: 14px;
                            }

                            QPushButton:hover {
                                background-color: #e0e0e0; /* Светлее при наведении */
                                border-color: #ccc;
                            }

                            QPushButton:pressed {
                                background-color: #d0d0d0; /* Еще светлее при нажатии */
                            }

                            QPushButton:disabled {
                                background-color: #f5f5f5;
                                border-color: #eee;
                            }


                        """)

        self.button_like.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;  /* Светло-серый фон */
                        border: 2px solid #ddd;  /* Светло-серая граница */
                        border-radius: 5px; /* Скругленные углы */
                        padding: 10px;
                        min-width: 50px; /* Минимальный размер */
                        min-height: 50px; /* Минимальный размер */
                        font-family: Arial, sans-serif; /* Шрифт */
                        font-size: 14px;
                    }

                    QPushButton:hover {
                        background-color: #e0e0e0; /* Светлее при наведении */
                        border-color: #ccc;
                    }

                    QPushButton:pressed {
                        background-color: #d0d0d0; /* Еще светлее при нажатии */
                    }

                    QPushButton:disabled {
                        background-color: #f5f5f5;
                        border-color: #eee;
                    }


                """)

        self.comboBox.setStyleSheet("""
            QComboBox {
                border: 2px solid #555; /* Тёмно-серая граница */
                border-radius: 5px; /* Скругленные углы */
                padding: 5px;
                background-color: white; /* Белый фон */
                font-family: Arial, sans-serif; /* Шрифт без засечек */
            }
            QComboBox:hover {
                border-color: #888; /* Более светлая граница при наведении */
            }
            QComboBox::drop-down {
                border: none; /* Убираем границу выпадающего списка */
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #555; /* Граница выпадающего списка */
                border-radius: 5px; /* Скругленные углы выпадающего списка */
                background-color: white;
                selection-background-color: #ddd; /* Цвет выделенного элемента */
                padding: 5px;
                font-family: Arial, sans-serif;
            }
        """)

        self.calendarWidget.setStyleSheet("""
                   QCalendarWidget QAbstractItemView:enabled {
                       background-color: white;
                       color: black;
                       font-family: Arial, sans-serif;
                       font-size: 12px;
                       selection-background-color: #90EE90; /* Светло-зеленый при выделении */
                       selection-color: black;
                   }
                   QCalendarWidget QAbstractItemView:disabled {
                       color: #ccc; /* Серый цвет для неактивных дат */
                   }
                   QCalendarWidget QWidget#qt_calendar_navigationbar {
                       background-color: #f0f0f0; /* Светло-серый фон навигационной панели */
                       color: #333;  /* Текст на навигационной панели */
                   }
                   QCalendarWidget QToolButton {
                       border: none;
                       background-color: transparent;
                       font-size: 14px;
                       color: #333;
                   }
                   QCalendarWidget QToolButton:hover {
                     background-color: #e0e0e0;
                   }
               """)

        self.label.setStyleSheet("""
    QLabel {
        background-color: #f0f0f0; /* Светло-серый фон */
        border: 1px solid #ccc; /* Светло-серая граница */
        border-radius: 5px; /* Скругленные углы */
        color: #333;
        font-family: Arial, sans-serif;
        font-size: 14px;
        padding: 10px;
    }
""")

    def action_dat_base(self):
        global like
        con = sqlite3.connect('data_base')
        cur = con.cursor()

        theme = self.comboBox.currentText()

        t = datetime.datetime(self.calendarWidget.selectedDate().year(),
                              self.calendarWidget.selectedDate().month(),
                              self.calendarWidget.selectedDate().day(),
                              )
        spisok_dati = [t.day, t.month, t.year]

        data = f'{spisok_dati[0]} {spisok_dati[1]} {spisok_dati[2]}'

        self.result = cur.execute(f"""SELECT newss FROM news
                    WHERE theme = '{theme}' and data = '{data}' """).fetchall()
        cur.close()
        con.close()

        for i in self.result:
            like = i[0]
            self.label.sizeHint()
            self.label.setText(like)

    def action_add_button_like(self):
        global like

        conn = sqlite3.connect('data_base')
        cur = conn.cursor()
        result = cur.execute(
            "SELECT like_news FROM like")

        for i in result:
            if i[0] == str(like):
                exit()
        cur.execute(
            "INSERT INTO like (like_news) VALUES ('%s')" % str(like))
        conn.commit()
        cur.close()
        conn.close()

    def action_button_like(self):
        dialog = Dialog(self)
        dialog.exec()

    def action_del_button_like(self):
        global like

        conn = sqlite3.connect('data_base')
        cur = conn.cursor()
        cur.execute("DELETE FROM like WHERE like_news = ?", (like,))
        conn.commit()
        cur.close()
        conn.close()

    def action_add_news(self):
        dialog = News(self)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Proekt()
    ex.show()
    sys.exit(app.exec())
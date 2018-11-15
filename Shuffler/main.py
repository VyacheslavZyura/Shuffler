# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMessageBox, QLabel, QPushButton, QFileDialog
from PyQt5.QtWidgets import QSpinBox, QAbstractSpinBox, QDialog
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap
from PyQt5.Qt import QTransform

from sys import argv, exc_info, exit
from procs import aggregation, shuffler, check_memory
from os.path import dirname, abspath, join

#Переменные:
abs_path = dirname(abspath(__file__))
log_file = join(abs_path, r"\Logs\logs.txt") # Путь до лога ошибок
main_ico = join(abs_path, r"\Temp\icon.ico") # Основная иконка
sour_ico = join(abs_path, r"\Temp\src.ico")  # Иконка кнопки "Отсюда"
dest_ico = join(abs_path, r"\Temp\dst.ico")  # Иконка кнопки "Сюда"
arrow_path = join(abs_path, r"\Temp\arrow.ico") # Указатель
print(log_file)
print(main_ico)
print(sour_ico)
print(dest_ico)
print(arrow_path)
# Приложение

# Параметры приложения - стиль и иконка
app = QApplication(argv)
app.setStyle("windowsvista") 
main_icon = QIcon(main_ico)
app.setWindowIcon(main_icon)    

# Главное окно, параметры, иконка в верхней полосе
window = QWidget()
window.setWindowFlags(Qt.Window | 
                      Qt.MSWindowsFixedSizeDialogHint)
window.setWindowTitle("Shuffler")
window.setWindowIcon(main_icon)
window.resize(234, 172)
window.setWindowOpacity(.94)  

# Шрифты
font = QFont()
font.setPointSize(10)
font.setWeight(50)
process_font = QFont()
process_font.setPointSize(7)


# Кнопка "Отсюда"
src_button = QPushButton("Отсюда", window)
src_button.setGeometry(10, 10, 100, 100)
src_button.setCursor(QCursor(Qt.PointingHandCursor))
src_button_icon = QIcon()  # Иконка для кнопки "Отсюда"

src_button_icon.addPixmap(QPixmap(sour_ico),
                 QIcon.Normal, QIcon.Off)
src_button.setIcon(src_button_icon)
src_button.setIconSize(QSize(24, 24)) # Размеры иконки
src_button.setToolTip("Не выбрано. Отсюда соберем песни")


# Кнопка "Сюда"
dst_button = QPushButton("Сюда", window)
dst_button.setGeometry(120, 10, 100, 100)
dst_button.setCursor(QCursor(Qt.PointingHandCursor))
dst_button_icon = QIcon()  # Иконка для кнопки "Cюда"

dst_button_icon.addPixmap(QPixmap(dest_ico),
                 QIcon.Normal, QIcon.On)
dst_button.setIcon(dst_button_icon)
dst_button.setIconSize(QSize(24, 24)) # Размеры иконки
dst_button.setToolTip("Не выбрано")
dst_button.setEnabled(False)
# Надпись 
size_label = QLabel(window)
size_label.setGeometry(QRect(10, 109, 99, 20))
size_label.setText("   Количество, MB ")
size_label.setToolTip("Выставить ограничение на размер будущего плейлиста")

# Поле для ввода чисел
size_Box = QSpinBox(window)
size_Box.setGeometry(QRect(10, 127, 91, 28))
size_Box.setFont(font)
size_Box.setValue(15)
size_Box.setButtonSymbols(QAbstractSpinBox.NoButtons)
size_Box.setRange(5, 55000)
size_Box.setAlignment(Qt.AlignRight|
                      Qt.AlignTrailing|
                      Qt.AlignVCenter)

# Кнопка "Сформировать"
active_button = QPushButton("Сформировать", window)
active_button.setGeometry(110, 115, 115, 50)
active_button.setCursor(QCursor(Qt.PointingHandCursor))
active_button_icon = QIcon()  # Иконка для кнопки "Сформировать"
active_button_icon.addPixmap(QPixmap(main_ico), 
                 QIcon.Normal, QIcon.Off)
active_button.setIcon(active_button_icon)
active_button.setIconSize(QSize(24, 24)) # Размеры иконки
active_button.setToolTip("Сформировать случайный список песен")
active_button.setEnabled(False)
# Надпись Процесса
process_label = QLabel(window)
process_label.setGeometry(QRect(9, 158, 97, 11))
process_label.setFont(process_font)
process_label.setText("Выбор папок...")
process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
# Стрелка
arrow_label = QLabel(window)
arrow = QPixmap(arrow_path)
transform = QTransform().rotate(-50)
arrow_label.setPixmap(arrow.transformed(transform, mode = 1))
arrow_label.setGeometry(QRect(64, 0, 90, 70))

# Функции:
# Генерация окна сообщения:
def msg_event(number):
    if number == 1: # Программа отработала 100%
        QMessageBox.information(window, "Готово", 
                                            "Песни собраны, наслаждайтесь!",
                                            buttons=QMessageBox.Ok,
                                            defaultButton=QMessageBox.Ok)
    elif number == 2: # Недостаточно места
        QMessageBox.information(window, "Не хватает места!", 
                                            "В папке \"Сюда\" недостаточно свободного места.",
                                            buttons=QMessageBox.Ok,
                                            defaultButton=QMessageBox.Ok)
    elif number == 3: # Неизвестная ошибка
        QMessageBox.critical(window, "Ошибка", 
                                            "Обнаружена ошибка, прерывающая выполнение программы.\nВсе подробности в файле: \"Shuffler\\Logs\\logs.txt\"",
                                            buttons=QMessageBox.Ok,
                                            defaultButton=QMessageBox.Ok)
    elif number == 4: # Не выбрана папка
        QMessageBox.information(window, "Вы не выбрали папку", 
                                            "Чтобы создать случайный плейлист\n             - необходимо выбрать папку!",
                                            buttons=QMessageBox.Ok,
                                            defaultButton=QMessageBox.Ok)

# Нажатие клавиши "Отсюда"
def src_FileDialog():

    # 1 часть функции (прогресс, работа иконки указателя, доступ к след. кнопке)
    if process_label.text() != "Ожидание старта..." and process_label.text() != "Выбор папок...":
        process_label.setText("Повторный выбор...")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
    
    transform = QTransform().rotate(130)
    arrow_label.setPixmap(arrow.transformed(transform, mode = 1))
    arrow_label.setGeometry(QRect(64, 62, 80, 80))
    dst_button.setEnabled(True)

    # 2 часть функции (диалоговое окно)
    dialog_src = QFileDialog(parent=window, filter="",
                               caption="Отсюда будут собраны музыкальные композиции")
    dialog_src.setFileMode(QFileDialog.Directory)
    dialog_src.setOption(QFileDialog.DontUseNativeDialog, True)
    result_src = dialog_src.exec()

    if result_src == QDialog.Accepted:
        for src in dialog_src.selectedFiles():
            src_button.setToolTip(src)
        
    else: # Если не выбрана папка
        msg_event(4)
        src_FileDialog()

# Нажатие клавиши "Сюда"
def dst_FileDialog():

    # 1 часть функции (прогресс, работа иконки указателя, доступ к след. кнопке)
    if process_label.text() == "Ожидание старта..." or process_label.text() != "Повторный выбор...":
        process_label.setText("Ожидание старта...")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
    else: 
        process_label.setText("Повторное ожидание..")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
    
    transform = QTransform().rotate(220)
    arrow_label.setPixmap(arrow.transformed(transform, mode = 1))
    arrow_label.setGeometry(QRect(55, 54, 80, 80))
    active_button.setEnabled(True)

    # 2 часть функции (диалоговое окно)
    dialog_dst = QFileDialog(parent=window, filter="",
                               caption="Сюда будут сгенерированы случайные композиции")
    dialog_dst.setFileMode(QFileDialog.Directory)
    dialog_dst.setOption(QFileDialog.DontUseNativeDialog, True)
    result_dst = dialog_dst.exec()

    if result_dst == QDialog.Accepted:
        for dst in dialog_dst.selectedFiles():
            dst_button.setToolTip(dst)               
    else: # Если не выбрана папка
        msg_event(4)
        dst_FileDialog()

# Функция выполняется при нажатии кнопки "Сформировать":
def main_process():
    # 1 часть функции (прогресс и отключение иконки указателя)
    process_label.setText("Начало программы...")
    process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
    arrow_label.hide()

    try:
        process_label.setText("Проверка памяти..")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
        
        # 2 часть: Сбор переменных и проверка свободного места 
        source = src_button.toolTip()        
        destination = dst_button.toolTip()
        limit = size_Box.value()*1024*1024
        
        if check_memory(destination, limit):
            pass
        else: 
            msg_event(2) 
            return False

        # 3 часть: Создание списка
        process_label.setText("Анализ данных...")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
        songs = aggregation(source)

        # 4 часть: Микс, копирование песен в директорию, месседж о готовности.
        process_label.setText("Копирование данных..")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
        
        shuffler(songs, destination, limit)

        process_label.setText("Все задачи выполнены")
        process_label.setToolTip("Сейчас происходит: %s" % process_label.text())
        
        msg_event(1)  #Программа завершена

    except:  # 5 часть: Ловим ошибки в лог файл Logs/logs.txt
        msg_event(3)
        try:
            log = open(log_file, "a")
            Type, Value, Trace = exc_info()
            log.writelines("\n")     
            log.writelines("Начало новой сессии!".center(50,"-"))
            log.writelines("\nОбнаружена ошибка: Процесс - %s" % process_label.text())
            log.writelines("\nType: %s" % {Type})
            log.writelines("\nValue: %s" % {Value})
            log.writelines("\nПеременные полученные на вход: ")
            log.writelines("\nSource: %s" % {source})
            log.writelines("\nDestination: %s" % {destination})
            log.writelines("\nLimit: %s" % {limit})
            log.writelines("\n")      
            log.writelines("Окончание сессии".center(50,"-")) 
            log.writelines("\n")            
        finally:
            log.close()


# Хвост программы
#При нажатии кнопок:
active_button.clicked.connect(main_process)
dst_button.clicked.connect(dst_FileDialog)   
src_button.clicked.connect(src_FileDialog)

# положение в центре экрана, отображение
desktop = QApplication.desktop()
x = (desktop.width() - window.width()) // 2
y = (desktop.height() - window.height()) // 2
window.move(x, y)
window.show()
exit(app.exec_())
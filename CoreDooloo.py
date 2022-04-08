import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton, QWidget
from PyQt5.QtCore import QThreadPool, QTimer
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pytube import YouTube
from ui_dooloodFacade import Ui_Form
from modul import ThreadApp, Download, DataBase, WebParse

DB_PATH = Path.cwd().joinpath('data/')
DB_NAME = "test.db"
VERSION = 'alfa 0.5.0'


class MainApp(QMainWindow, Ui_Form):

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.counter = 0
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.DB = DataBase.DB(DB_NAME)
        self.progressBar.setHidden(True)
        self.progress_bar_text.setHidden(True)
        self.pushButton.pressed.connect(self.start_worker)
        self.version_lable.setText(VERSION)
        self.lineEdit_3.setText(str(Path.cwd().joinpath('download/')))
        self.pushButton_2.pressed.connect(self.set_path)

    def start_worker(self):
        # Pass the function to execute
        worker = ThreadApp.Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        # Execute
        self.threadpool.start(worker)

    def execute_this_fn(self, progress_callback):

        #init_pars

        defaulUrl = 'https://www.youtube.com/channel/UCfxnN0xALQR6OtznIj35ypQ/videos'
        URL = self.lineEdit.text()
        if URL == '':
            URL = defaulUrl

        defPathDownload = Path.cwd().joinpath('download/')
        PATH_DOWNLOAD = self.lineEdit_3.text()
        if PATH_DOWNLOAD == defPathDownload:
            PATH_DOWNLOAD = defPathDownload

        SELECT_MODE = self.select_mode()
        LABEL = self.lineEdit_2.text()

        DB = self.DB
        browser = WebParse.WebParse(URL, SELECT_MODE, DB, LABEL, self)
        val = 0

        #сбор ссылок и запись в БД
        driver = browser.start_pars()
        driver.get(browser.url)
        html = driver.find_element(By.TAG_NAME, "html")

        scroll = 10

        prg_count = 0
        prg_var = scroll
        self.progressBar.setRange(0, prg_var)
        self.progressBar.setHidden(False)
        self.progress_bar_text.setText(f'{prg_count}%')
        self.progress_bar_text.setHidden(False)

        prg_unit = prg_var / 100
        prg_unit_count = prg_unit

        self.listWidget.addItem('Скролинг всех видео...')
        self.listWidget.addItem(f'Ожидание составит {prg_var / 10} сек')
        for i in range(prg_var):
            html.send_keys(Keys.DOWN)
            val += 1
            progress_callback.emit(val)
            if val >= prg_unit_count:
                prg_count += 1
                prg_unit_count += prg_unit
                self.progress_bar_text.setText(f'{prg_count}%')
            time.sleep(0.15)

        self.progressBar.setHidden(True)
        self.progress_bar_text.setHidden(True)

        browser.element = driver.find_element(By.ID, 'items')
        browser.elements = driver.find_elements(By.TAG_NAME, "ytd-grid-video-renderer")

        #время скролинга на странице ВИДЕО
        self.DB.connect_db()

        elements = browser.elements

        pars_prg = len(elements)
        prg_var = pars_prg
        prg_unit = prg_var / 100
        prg_unit_count = prg_unit
        val = 0
        prg_count = 0
        self.progressBar.setRange(0, pars_prg)
        self.listWidget.addItem('Начался сбор ссылок ...')
        self.progressBar.setHidden(False)
        self.progress_bar_text.setHidden(False)

        for e in elements:
            video_title = e.find_element(By.ID, "video-title")
            link = (video_title.get_attribute("href"))
            title = (video_title.get_attribute("title"))
            DB.add_data(LABEL, title, link)
            val += 1
            progress_callback.emit(val)
            if val >= prg_unit_count:
                prg_count += 1
                prg_unit_count += prg_unit
                self.progress_bar_text.setText(f'{prg_count}%')
            time.sleep(0.1)

        self.listWidget.addItem(f'Всего ссылок было добавленно: {pars_prg}')

        self.progressBar.setHidden(True)
        self.progress_bar_text.setHidden(True)

        DB.insert_data()
        DB.close_db()

        #DOwnload

        DB.connect_db()
        DB.take_data()

        pars_prg = len(DB.value)
        prg_var = pars_prg
        prg_unit = prg_var / 100
        prg_unit_count = prg_unit
        val = 0
        prg_count = 0
        self.progress_bar_text.setText(f'{val}%')
        self.progressBar.setHidden(False)
        self.progress_bar_text.setHidden(False)
        self.progressBar.setRange(0, pars_prg)
        self.listWidget.addItem(f'Скачевание началось в папку {PATH_DOWNLOAD}')

        for obj in DB.value:
            url = obj[2]
            video_name = obj[1]
            video_obj = YouTube(url)
            stream = video_obj.streams.get_highest_resolution()

            val += 1
            progress_callback.emit(val)
            if val >= prg_unit_count:
                prg_count += 1
                prg_unit_count += prg_unit
                self.progress_bar_text.setText(f'{prg_count}%')
            self.listWidget.addItem(f'Качаю видео {video_name}')
            stream.download(PATH_DOWNLOAD)

        DB.delete_table()
        DB.close_db()

        return self.listWidget.addItem(f'Все видео были закачены')

    def print_output(self, *args):
        print(f"Print_output {args}")
        self.progressBar.setHidden(True)
        self.progressBar.setValue(0)

    def select_mode(self):
        if self.radioButton.isChecked():
            return 'videos'
        if self.radioButton_2.isChecked():
            return 'video'

    def thread_complete(self):
        self.listWidget.addItem(f'Кoнец программы...')

    def progress_fn(self, val):
        self.progressBar.setValue(val)

    def set_path(self):
        PATH = Path.cwd().joinpath('download/')
        self.lineEdit_3.setText(str(PATH))


def main_application():
    app = QApplication(sys.argv)
    main = MainApp()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_application()

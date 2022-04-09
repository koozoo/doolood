from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path
import sys
import os


class WebParse:
    def __init__(self, url, choice_download, obj_db, label, obj_app):
        self.url = url
        self.choice_download = choice_download
        self.element = []
        self.elements = []
        self.DB = obj_db
        self.label = label
        self.obj_app = obj_app

    def start_pars(self):
        type_os = sys.platform

        if type_os == 'win32' or type_os == 'cygwin':
            driver = '\\geckodriver.exe'
        elif type_os == 'darwin':
            driver = 'lib/macos/geckodriver'

        var = webdriver.Firefox(executable_path=driver, options=self.options())

        return var

    def options(self):
        opt = webdriver.FirefoxOptions()
        opt.set_preference('dom.webdriver.enabled', False)
        opt.set_preference('dom.webnotifications.enabled', False)
        opt.set_preference('dom.volume_scale', '0.0')
        opt.headless = True
        return opt

    def parse_youtube_videos(self):
        # self.DB.connect_db()

        driver = self.start_pars()
        driver.get(self.url)
        html = driver.find_element(By.TAG_NAME, "html")
        for i in range(100):
            html.send_keys(Keys.DOWN)
            time.sleep(0.15)

        self.element = driver.find_element(By.ID, 'items')
        self.elements = driver.find_elements(By.TAG_NAME, "ytd-grid-video-renderer")

        # for e in self.elements:
        #     video_title = e.find_element(By.ID, "video-title")
        #     link = (video_title.get_attribute("href"))
        #     title = (video_title.get_attribute("title"))
        #     self.DB.add_data(self.label, title, link)
        #
        #
        # self.DB.insert_data()
        # self.DB.close_db()

        # time.sleep(5)
        # driver.close()
        driver.quit()

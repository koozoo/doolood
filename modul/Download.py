from pathlib import Path
import sys
from pytube import YouTube


class Download:
    def __init__(self, obj_db, download_path, progress_callback):
        self.download_path = download_path
        self.OS = sys.platform
        self.db = obj_db
        self.url = None
        self.total_video = None
        self.video = None
        self.num = 0
        self.progress_callback = progress_callback

    def download(self):
        self.db.connect_db()
        self.db.take_data()

        for obj in self.db.big_data:
            self.url = obj[2]
            video_obj = YouTube(self.url)
            stream = video_obj.streams.get_highest_resolution()
            stream.download(self.download_path)
            self.num += 1
            self.progress_callback.emit(self.num)

        self.db.close_db()

    def path_for_os(self, download_path):
        path = download_path
        if path != '':
            print(Path())
            return download_path
        elif self.OS == 'darwin':
            self.download_path = Path()
        elif self.OS == 'cygwin':
            pass
        elif self.OS == 'linux':
            pass
        else:
            pass

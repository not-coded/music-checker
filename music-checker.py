import os
import sys
import re
from PyQt6.QtWidgets import QApplication, QSpacerItem, QSizePolicy, QLabel, QFileDialog, QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QByteArray, Qt
from tinytag import TinyTag
import yt_dlp

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 100, 780, 360)
        self.setWindowTitle('Music Checker')
        layout = QVBoxLayout()
        #layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.setLayout(layout)

        label = QLabel('Music Checker')
        label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(label)

        label = QLabel('This tool checks if the music file is the right one by comparing the YouTube link to the song metadata, if there is no link then it will use the title and author of the metadata.')
        layout.addWidget(label)

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        # ---- File selecting stuff ----

        hbox = QHBoxLayout()
        layout.addLayout(hbox)

        self.textInput = QLineEdit()
        self.textInput.setReadOnly(True)
        hbox.addWidget(self.textInput)

        fileButton = QPushButton('Select File')
        fileButton.clicked.connect(self.selectFile)
        hbox.addWidget(fileButton)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        # ---- Showing music metadata ----

        container = QWidget()
        centered_layout = QHBoxLayout(container)
        
        labels_widget = QWidget()
        labels = QVBoxLayout(labels_widget)
        labels.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.titleLabel = QLabel('Title: ')
        self.titleLabel.setStyleSheet("font-size: 12pt;")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.titleLabel.hide()
        labels.addWidget(self.titleLabel)

        self.artistLabel = QLabel('Artist: ')
        self.artistLabel.setStyleSheet("font-size: 12pt;")
        self.artistLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.artistLabel.hide()
        labels.addWidget(self.artistLabel)

        self.durationLabel = QLabel('Duration: ')
        self.durationLabel.setStyleSheet("font-size: 12pt;")
        self.durationLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.durationLabel.hide()
        labels.addWidget(self.durationLabel)

        self.commentLabel = QLabel('Comment: ')
        self.commentLabel.setStyleSheet("font-size: 12pt;")
        self.commentLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.commentLabel.hide()
        labels.addWidget(self.commentLabel)

        # WOAS - The 'Official audio source webpage' frame is a URL pointing at the official webpage for the source of the audio file, e.g. a movie.
        # https://mypod.sourceforge.net/user%20manual/html/apa.html
        # SpotDL includes the spotify link which we can use incase the song is wrong.
        self.woasLabel = QLabel('Source: ')
        self.woasLabel.setStyleSheet("font-size: 12pt;")
        self.woasLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.woasLabel.hide()
        labels.addWidget(self.woasLabel)
        
        centered_layout.addWidget(labels_widget)
        
        self.imageLabel = QLabel()
        self.imageLabel.hide()
        centered_layout.addWidget(self.imageLabel)
        
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

        # ---- ----

        layout.addStretch()
        self.show()

        
    
    def selectFile(self):

        fileDialog = QFileDialog
        # TODO: use native file dialog

        self.current_file, _ = fileDialog.getOpenFileName(self, 'Open File', '.', 'All Files (*.*)')

        if not self.current_file or not os.path.exists(self.current_file):
            return None

        self.textInput.setText(self.current_file)

        # 1. get metadata
        # 2. update Title, Artist, Duration, Comment (link)
        # 2.1. show image?
        self.show_metadata()

        # 3. check youtube link in comment
        # 4. if valid then checkmark yay
        # 4.1 if invalid then check first 2 results and check which one matches the title & artist the best
        self.check_youtube_link()
        

    def check_youtube_link(self):
        tag = TinyTag.get(self.current_file, image=False)
        youtube_id = self.extract_youtube_id(tag.comment)
        if youtube_id is None:
            return None

        video_info = self.get_video_info(youtube_id)
        if video_info is None:
            return None

        print(video_info)

        # if the author name (youtube) contains author name (metadata) and same thing with author then return true

        print(video_info['author'].lower())
        print(tag.artist.lower())

        if tag.artist.lower() in video_info['author'].lower() and tag.artist.lower() in video_info['author'].lower():
            return True

        
    
    def extract_youtube_id(self, text):
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'
        match = re.search(youtube_regex, text)
        if match:
            video_id = match.group(4)
            return video_id
        return None
    
    def get_video_info(self, url):
        try:
            yt_dlp_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
                'default_search': 'ytsearch1',
                'noplaylist': True
            }
            
            with yt_dlp.YoutubeDL(yt_dlp_opts) as ytp:
                info = ytp.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'author': info.get('uploader'),
                    'duration': info.get('duration'),
                    'id': url
                }
        except Exception as e:
            print(e)
            return None
        

    def show_metadata(self):
        tag = TinyTag.get(self.current_file, image=True)
        image: Image | None = tag.images.any

        self.titleLabel.setText(f"Title: {tag.title}")
        self.titleLabel.show()
        self.artistLabel.setText(f"Artist: {tag.artist}")
        self.artistLabel.show()

        minutes = int(tag.duration // 60)
        seconds = int(tag.duration % 60)
        self.durationLabel.setText(f"Duration: {minutes:02d}:{seconds:02d}")
        self.durationLabel.show()

        self.commentLabel.setText(f"Comment: {tag.comment}")
        self.commentLabel.show()

        if tag.other.get('woas') is not None:
            self.woasLabel.setText(f"Source: {tag.other.get('woas')[0]}")
            self.woasLabel.show()

        if image is not None:
            # https://pypi.org/project/tinytag/
            # ^ useful stuff
            data: bytes = image.data

            bytes_buffer = QByteArray(data)
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_buffer)
            pixmap = pixmap.scaled(200, 200)

            self.imageLabel.setPixmap(pixmap)
            self.imageLabel.show()        


        



def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

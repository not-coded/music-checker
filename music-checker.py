import os
import sys
import re
import requests
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

        # ---- Showing song metadata ----

        container = QWidget()
        centered_layout = QHBoxLayout(container)
        
        labels_widget = QWidget()
        labels = QVBoxLayout(labels_widget)
        labels.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.songMetadataLabel = QLabel('Song Metadata:')
        self.songMetadataLabel.setStyleSheet("font-size: 16pt;")
        self.songMetadataLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.songMetadataLabel.hide()
        layout.addWidget(self.songMetadataLabel)

        self.songTitleLabel = QLabel('Title: ')
        self.songTitleLabel.setStyleSheet("font-size: 12pt;")
        self.songTitleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songTitleLabel.hide()
        labels.addWidget(self.songTitleLabel)

        self.songArtistLabel = QLabel('Artist: ')
        self.songArtistLabel.setStyleSheet("font-size: 12pt;")
        self.songArtistLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songArtistLabel.hide()
        labels.addWidget(self.songArtistLabel)

        self.songDurationLabel = QLabel('Duration: ')
        self.songDurationLabel.setStyleSheet("font-size: 12pt;")
        self.songDurationLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songDurationLabel.hide()
        labels.addWidget(self.songDurationLabel)

        self.songCommentLabel = QLabel('Comment: ')
        self.songCommentLabel.setStyleSheet("font-size: 12pt;")
        self.songCommentLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songCommentLabel.hide()
        labels.addWidget(self.songCommentLabel)

        # WOAS - The 'Official audio source webpage' frame is a URL pointing at the official webpage for the source of the audio file, e.g. a movie.
        # https://mypod.sourceforge.net/user%20manual/html/apa.html
        # SpotDL includes the spotify link which we can use incase the song is wrong.
        self.songSourceLabel = QLabel('Source: ')
        self.songSourceLabel.setStyleSheet("font-size: 12pt;")
        self.songSourceLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songSourceLabel.hide()
        labels.addWidget(self.songSourceLabel)
        
        centered_layout.addWidget(labels_widget)
        
        self.songImageLabel = QLabel()
        self.songImageLabel.hide()
        centered_layout.addWidget(self.songImageLabel)
        
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

        # ---- Showing YouTube metadata ----

        container = QWidget()
        centered_layout = QHBoxLayout(container)
        
        labels_widget = QWidget()
        labels = QVBoxLayout(labels_widget)
        labels.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.youtubeMetadataLabel = QLabel('YouTube Metadata:')
        self.youtubeMetadataLabel.setStyleSheet("font-size: 16pt;")
        self.youtubeMetadataLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.youtubeMetadataLabel.hide()
        layout.addWidget(self.youtubeMetadataLabel)

        self.youtubeTitleLabel = QLabel('Title: ')
        self.youtubeTitleLabel.setStyleSheet("font-size: 12pt;")
        self.youtubeTitleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.youtubeTitleLabel.hide()
        labels.addWidget(self.youtubeTitleLabel)

        self.youtubeArtistLabel = QLabel('Artist: ')
        self.youtubeArtistLabel.setStyleSheet("font-size: 12pt;")
        self.youtubeArtistLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.youtubeArtistLabel.hide()
        labels.addWidget(self.youtubeArtistLabel)

        self.youtubeDurationLabel = QLabel('Duration: ')
        self.youtubeDurationLabel.setStyleSheet("font-size: 12pt;")
        self.youtubeDurationLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.youtubeDurationLabel.hide()
        labels.addWidget(self.youtubeDurationLabel)
        
        centered_layout.addWidget(labels_widget)
        
        self.youtubeImageLabel = QLabel()
        self.youtubeImageLabel.hide()
        centered_layout.addWidget(self.youtubeImageLabel)
        
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
        self.show_song_metadata()

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

        # if the author name (youtube) contains author name (metadata) and same thing with author then return true
        print(video_info)

        self.show_youtube_metadata(video_info)

        if tag.artist.lower() in video_info['author'].lower() and tag.artist.lower() in video_info['author'].lower():
            print("the youtube song and the metadata song match!!!!")
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
                    'id': url,
                    'thumbnail': info.get('thumbnail')
                }
        except Exception as e:
            print(e)
            return None

    
    def show_youtube_metadata(self, video_info):
        self.youtubeMetadataLabel.show()

        self.youtubeTitleLabel.setText(f"Title: {video_info['title']}")
        self.youtubeTitleLabel.show()
        self.youtubeArtistLabel.setText(f"Artist: {video_info['author']}")
        self.youtubeArtistLabel.show()

        minutes = int(video_info['duration'] // 60)
        seconds = int(video_info['duration'] % 60)
        self.youtubeDurationLabel.setText(f"Duration: {minutes:02d}:{seconds:02d}")
        self.youtubeDurationLabel.show()

        if video_info['thumbnail'] is not None:
            response = requests.get(video_info['thumbnail']) # its a webp link
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            pixmap = pixmap.scaled(356, 200) # wohooo we love 16:9

            self.youtubeImageLabel.setPixmap(pixmap)
            self.youtubeImageLabel.show()

    def show_song_metadata(self):
        tag = TinyTag.get(self.current_file, image=True)
        image: Image | None = tag.images.any

        self.songMetadataLabel.show()

        self.songTitleLabel.setText(f"Title: {tag.title}")
        self.songTitleLabel.show()
        self.songArtistLabel.setText(f"Artist: {tag.artist}")
        self.songArtistLabel.show()

        minutes = int(tag.duration // 60)
        seconds = int(tag.duration % 60)
        self.songDurationLabel.setText(f"Duration: {minutes:02d}:{seconds:02d}")
        self.songDurationLabel.show()

        self.songCommentLabel.setText(f"Comment: {tag.comment}")
        self.songCommentLabel.show()

        if tag.other.get('woas') is not None:
            self.songSourceLabel.setText(f"Source: {tag.other.get('woas')[0]}")
            self.songSourceLabel.show()

        if image is not None:
            # https://pypi.org/project/tinytag/
            # ^ useful stuff
            data: bytes = image.data

            bytes_buffer = QByteArray(data)
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_buffer)
            pixmap = pixmap.scaled(200, 200)

            self.songImageLabel.setPixmap(pixmap)
            self.songImageLabel.show()        


        



def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

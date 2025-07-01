import os
import sys
import re
import requests
from PyQt6.QtWidgets import QApplication, QSpacerItem, QSizePolicy, QLabel, QFileDialog, QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import QByteArray, QTimer, Qt, QUrl
from tinytag import TinyTag
import yt_dlp

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 100, 1063, 285)
        self.setFixedSize(1063, 285)
        self.setWindowTitle('Music Checker')
        layout = QVBoxLayout()
        #layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.setLayout(layout)

        label = QLabel('Music Checker')
        label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(label)

        label = QLabel('This tool checks if the music file is the right one by comparing the YouTube Metadata to the song metadata, if there is no link then it will use the title and author of the metadata.')
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
        self.songCommentLabel.setTextFormat(Qt.TextFormat.RichText)
        self.songCommentLabel.hide()
        labels.addWidget(self.songCommentLabel)

        # WOAS - The 'Official audio source webpage' frame is a URL pointing at the official webpage for the source of the audio file, e.g. a movie.
        # https://mypod.sourceforge.net/user%20manual/html/apa.html
        # SpotDL includes the spotify link which we can use incase the song is wrong.
        self.songSourceLabel = QLabel('Source: ')
        self.songSourceLabel.setStyleSheet("font-size: 12pt;")
        self.songSourceLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.songSourceLabel.setTextFormat(Qt.TextFormat.RichText)
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

        self.youtubeSourceLabel = QLabel('Source: ')
        self.youtubeSourceLabel.setStyleSheet("font-size: 12pt;")
        self.youtubeSourceLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.youtubeSourceLabel.setTextFormat(Qt.TextFormat.RichText)
        self.youtubeSourceLabel.hide()
        labels.addWidget(self.youtubeSourceLabel)
        
        centered_layout.addWidget(labels_widget)
        
        self.youtubeImageLabel = QLabel()
        self.youtubeImageLabel.hide()
        centered_layout.addWidget(self.youtubeImageLabel)
        
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

        # ---- ----

        layout.addItem(QSpacerItem(30, 30, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.resultLabel = QLabel('')
        self.resultLabel.setStyleSheet("font-size: 16pt;")
        self.resultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resultLabel.hide()
        layout.addWidget(self.resultLabel)

        self.findCorrectSongButton = QPushButton('Find correct song on YouTube')
        self.findCorrectSongButton.clicked.connect(self.find_correct_song)
        self.findCorrectSongButton.hide()
        self.findCorrectSongButton.setFixedWidth(200)
        layout.addWidget(self.findCorrectSongButton, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        self.show()

        
    def find_correct_song(self):
        if self.check_youtube_link(True):
            self.resultLabel.show()
            self.resultLabel.setText('[⚠️] Only the YouTube Metadata matches, the Song Metadata does not match.')
            self.findCorrectSongButton.hide()
            return True
        else:
            self.resultLabel.show()
            self.resultLabel.setText('[❌] Could not find a song that matched the metadata.')
            self.findCorrectSongButton.hide()
            return False
            

        

    def selectFile(self):

        fileDialog = QFileDialog
        # TODO: use native file dialog

        # https://pypi.org/project/tinytag/
        supported_formats = (
            "Audio Files (*.mp3 *.mp2 *.mp1 *.m4a *.wav *.ogg *.flac *.wma *.aiff *.aifc);;"
            "MP3 Files (*.mp3 *.mp2 *.mp1);;"
            "M4A Files (*.m4a);;"
            "WAVE Files (*.wav);;"
            "OGG Files (*.ogg);;"
            "FLAC Files (*.flac);;"
            "WMA Files (*.wma);;"
            "AIFF Files (*.aiff *.aifc);;"
        )
        self.current_file, _ = fileDialog.getOpenFileName(self, 'Select Audio File', '', supported_formats)

        if not self.current_file or not os.path.exists(self.current_file):
            return None

        self.textInput.setText(self.current_file)
        
        # hide stuff so the window can actually get resized
        self.youtubeArtistLabel.hide();
        self.youtubeDurationLabel.hide();
        self.youtubeSourceLabel.hide();
        self.youtubeTitleLabel.hide();
        self.youtubeMetadataLabel.hide();
        self.youtubeImageLabel.hide();
        self.resultLabel.hide();
        self.findCorrectSongButton.hide();

        
        # i mean this works for resizing the window i guess
        QTimer.singleShot(1, lambda: [self.show_song_metadata(), self.setFixedSize(1063, 500)])

        # its going to be on not responding state sooo
        QTimer.singleShot(250, lambda: [self.check_youtube_link(), self.setFixedSize(1063, 720)])
        
        

    def check_youtube_link(self, forceTitleAndAuthor=False):
        tag = TinyTag.get(self.current_file, image=False)
        youtube_id = self.extract_youtube_id(tag.comment)
        has_youtube_link = youtube_id is not None and forceTitleAndAuthor == False
        if has_youtube_link:
            video_info = self.get_video_info(youtube_id)
            url = f"https://youtube.com/watch?v={youtube_id}"
            self.songCommentLabel.setText(f"Comment: <a href='{url}' style='color: blue; text-decoration: underline;'>{url}</a>")
            self.songCommentLabel.linkActivated.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            self.songCommentLabel.show()
        else:
            video_info = self.get_video_info_by_title_and_author(tag.title, tag.artist)
            

        if video_info is None:
            print("Failed to get video info:")
            print("Has YouTube Link: ", has_youtube_link)
            print("Youtube ID: ", youtube_id)
            print("Comment: ", tag.comment)

            self.resultLabel.show()
            self.resultLabel.setText("An error occured while checking the YouTube Metadata. Check logs for more info.\nPlease try again.")
            return None

        self.show_youtube_metadata(video_info)

        if tag.artist.lower() in video_info['author'].lower() and tag.artist.lower() in video_info['author'].lower():
            self.resultLabel.show()
            self.resultLabel.setText('[✅] The YouTube Metadata and the Song Metadata Match!')
            return True
        else:
            self.resultLabel.show()
            self.resultLabel.setText('[❌] The YouTube Metadata and the Song Metadata Do Not Match!')
            self.findCorrectSongButton.show()
            return False

        
    
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
    
    # insane name
    def get_video_info_by_title_and_author(self, title, author):
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
                info = ytp.extract_info(f"ytsearch1:{title} - {author}", download=False)
                top_result = info['entries'][0]

                return {
                    'title': top_result.get('title'),
                    'author': top_result.get('uploader'),
                    'duration': top_result.get('duration'),
                    'id': top_result.get('id'),
                    'thumbnail': top_result.get('thumbnail')
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

        url = f"https://youtube.com/watch?v={video_info['id']}"
        self.youtubeSourceLabel.setText(f"Source: <a href='{url}' style='color: blue; text-decoration: underline;'>{url}</a>")
        self.youtubeSourceLabel.linkActivated.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        self.youtubeSourceLabel.show()

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
            url = tag.other.get('woas')[0]
            self.songSourceLabel.setText(f"Source: <a href='{url}' style='color: blue; text-decoration: underline;'>{url}</a>")
            self.songSourceLabel.linkActivated.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            self.songSourceLabel.show()

        if image is not None:
            # https://pypi.org/project/tinytag/
            # ^ useful stuff
            data: bytes = image.data

            bytes_buffer = QByteArray(data)
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_buffer)
            if pixmap.width() / pixmap.height() != 16 / 9:
                pixmap = pixmap.scaled(200, 200)
            else:
                pixmap = pixmap.scaled(356, 200)

            self.songImageLabel.setPixmap(pixmap)
            self.songImageLabel.show()        


        



def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

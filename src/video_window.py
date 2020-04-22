from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QPushButton,
        QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QTableWidget,
        QTableWidgetItem, QMainWindow, QAction, QAbstractScrollArea, QShortcut,
        QSpacerItem, QProgressBar, QMessageBox)

from utils import create_action, format_time
from bad_clips_table import BadClipsWidget
from bad_clips_slider import HlightRmClipsWidget
from proc_bar_dialog import ProcVideoDialog
from signals import SignalBus

import os
import sys
from functools import partial
from moviepy.editor import VideoFileClip


TMP_VIDEO_PATH = os.path.join(QDir.homePath(), 'tmp_proc_video.mp4')


class VideoWindow(QMainWindow):

    def __init__(self, app, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.app = app
        self.setWindowTitle("sofa")
        self.setWindowIcon(QIcon('src/static/img/tofu.png'))
        self.rate = 1
        self.isNewMark = False
        self.openedFile = None
        self.initUI()
        self.set_default_shortcuts()
        self.shortcuts = {}
        self.comm = SignalBus.instance()

    def initUI(self):
        videoWidget = self.create_player()
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)
        self.create_menu_bar()
        self.wid = QWidget(self)
        self.setCentralWidget(self.wid)
        self.set_layout(videoWidget, self.wid)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()
        self.clipsWidget = BadClipsWidget()
        self.create_control()

        self.playButton.clicked.connect(self.play)
        self.speedUpButton.clicked.connect(self.speed)
        self.slowDownButton.clicked.connect(self.slow)
        self.adv3Button.clicked.connect(partial(self.advance, 3))
        self.goBack3Button.clicked.connect(partial(self.back, 3))
        self.advanceButton.clicked.connect(partial(self.advance, 10))
        self.goBackButton.clicked.connect(partial(self.back, 10))
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.cutButton.clicked.connect(self.createMark)
        self.cutButton.clicked.connect(self.hlightSlider.toggleRm)

        return videoWidget

    def set_default_shortcuts(self):
        self.playButton.setShortcut(QKeySequence(Qt.Key_Space))
        self.speedUpButton.setShortcut(QKeySequence(Qt.Key_Up))
        self.slowDownButton.setShortcut(QKeySequence(Qt.Key_Down))
        self.advanceButton.setShortcut(QKeySequence(Qt.Key_Right))
        self.goBackButton.setShortcut(QKeySequence(Qt.Key_Left))
        self.cutButton.setShortcut(QKeySequence(Qt.Key_C))

    def create_control(self):
        self.playButton = _create_button(
                self.style().standardIcon(QStyle.SP_MediaPlay))
        self.speedUpButton = _create_button(
                self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.slowDownButton = _create_button(
                self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.adv3Button = _create_button(
                self.style().standardIcon(QStyle.SP_ArrowRight))
        self.advanceButton = _create_button(
                self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.goBack3Button = _create_button(
                self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.goBackButton = _create_button(
                self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.cutButton = _create_button(self.style().standardIcon(
            QStyle.SP_MessageBoxCritical))
        self.timeBox = QLabel(format_time(0), self)
        self.timeBox.setAlignment(Qt.AlignCenter)
        self.rateBox = QLabel(str(self.rate) + 'x', self)
        self.rateBox.setAlignment(Qt.AlignCenter)
        self.hlightSlider = HlightRmClipsWidget()
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)

    def create_menu_bar(self):
        openAction = create_action('open.png', '&Open', 'Ctrl+O', 'Open video',
                self.openFile, self)
        saveAction = create_action('save.png', '&Save Clips', 'Ctrl+S',
                'Save anonimized clips', self.saveClips, self)
        exitAction = create_action('exit.png', '&Exit', 'Ctrl+Q', 'Exit',
                self.exitCall, self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

    def set_layout(self, videoWidget, wid):
        labellingLayout = QVBoxLayout()
        labellingLayout.addWidget(self.clipsWidget)

        controlLayout = self.make_control_layout()

        videoAreaLayout = QVBoxLayout()
        videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        videoAreaLayout.addWidget(videoWidget)
        videoAreaLayout.addLayout(controlLayout)
        videoAreaLayout.addWidget(self.errorLabel)

        layout = QHBoxLayout()
        layout.addLayout(videoAreaLayout, 4)
        layout.addLayout(labellingLayout)

        wid.setLayout(layout)

    def make_control_layout(self):
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout.addWidget(self.timeBox)
        buttonsLayout.addWidget(self.slowDownButton)
        buttonsLayout.addWidget(self.goBackButton)
        buttonsLayout.addWidget(self.goBack3Button)
        buttonsLayout.addWidget(self.playButton)
        buttonsLayout.addWidget(self.adv3Button)
        buttonsLayout.addWidget(self.advanceButton)
        buttonsLayout.addWidget(self.speedUpButton)
        buttonsLayout.addWidget(self.rateBox)
        cutLayout = QHBoxLayout()
        cutLayout.setContentsMargins(0, 0, 0, 0)
        cutLayout.addSpacerItem(QSpacerItem(200, 5, QSizePolicy.Minimum,
            QSizePolicy.Minimum))
        cutLayout.addWidget(self.cutButton)
        cutLayout.addSpacerItem(QSpacerItem(200, 5, QSizePolicy.Minimum,
            QSizePolicy.Minimum))
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.positionSlider)
        layout.addWidget(self.hlightSlider)
        layout.addLayout(buttonsLayout)
        layout.addLayout(cutLayout)
        return layout

    def openFile(self):
        self.rawFileName, _ = QFileDialog.getOpenFileName(self, "Open video",
                QDir.homePath())
        if self.rawFileName != '':
            should_process = QMessageBox.question(self.wid, 'Open video',
                    'Do you want to pre process the video?',
                    QMessageBox.Yes | QMessageBox.No)
            if should_process == QMessageBox.Yes:
                self.fileName = TMP_VIDEO_PATH
                process = ProcVideoDialog(self.rawFileName, self.fileName, self)
                self.comm.videoProcessed.connect(self.openMedia)
            else:
                self.fileName = self.rawFileName
                self.openMedia()

    @pyqtSlot()
    def openMedia(self):
        self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.fileName)))
        self.openedFile = os.path.basename(self.fileName)
        self.setWindowTitle("sofa - " + self.openedFile)
        self.playButton.setEnabled(True)
        self.speedUpButton.setEnabled(True)
        self.slowDownButton.setEnabled(True)
        self.advanceButton.setEnabled(True)
        self.adv3Button.setEnabled(True)
        self.goBackButton.setEnabled(True)
        self.goBack3Button.setEnabled(True)
        self.cutButton.setEnabled(True)
        self.rate = 1

    def exitCall(self):
        if self.openedFile is not None:
            os.remove(self.fileName)
        sys.exit(self.app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def slow(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.rate -= 0.5
            # TODO: Workaround pt 1
            # https://forum.qt.io/topic/88490/change-playback-rate-at-...
            # ...runtime-problem-with-position-qmediaplayer/8
            currentPos = self.mediaPlayer.position()
            # TODO: Workaround pt 1
            self.mediaPlayer.setPlaybackRate(self.rate)
            # TODO: Workaround pt 2
            self.mediaPlayer.setPosition(currentPos)
            # TODO: Workaround pt 2: end
            self.rateBox.setText(str(self.rate)+'x')

    def speed(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.rate += 0.5
            # TODO: Workaround pt 1
            # https://forum.qt.io/topic/88490/change-playback-rate-at-...
            # ...runtime-problem-with-position-qmediaplayer/8
            currentPos = self.mediaPlayer.position()
            # TODO: Workaround pt 1
            self.mediaPlayer.setPlaybackRate(self.rate)
            # TODO: Workaround pt 2
            self.mediaPlayer.setPosition(currentPos)
            # TODO: Workaround pt 2: end
            self.rateBox.setText(str(self.rate)+'x')

    def advance(self, t=10):
        currentPos = self.mediaPlayer.position()
        nextPos  = currentPos + t*1000
        self.setPosition(nextPos)

    def back(self, t=10):
        currentPos = self.mediaPlayer.position()
        nextPos  = max(currentPos - t*1000, 0)
        self.setPosition(nextPos)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.hlightSlider.setValue(position)
        self.timeBox.setText(format_time(int(position/1000)))

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.hlightSlider.setRange(duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.speedUpButton.setEnabled(False)
        self.slowDownButton.setEnabled(False)
        self.advanceButton.setEnabled(False)
        self.goBackButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def saveClips(self):
        prefix = os.path.splitext(os.path.basename(self.rawFileName))[0] + \
                '_slice_'
        dirPath = QFileDialog.getExistingDirectory(self, 'Select Dir')
        if dirPath != '':
            try:
                video = VideoFileClip(self.fileName)
                marks = self.clipsWidget.get_marks()
                begin_time = 0.0
                for i, m in enumerate(marks):
                    end_time = float(m[0])
                    out_path = os.path.join(dirPath, prefix+str(i)+".mp4")
                    clip = video.subclip(begin_time, end_time)
                    clip.write_videofile(out_path)
                    begin_time = float(m[1])
                end_video = self.mediaPlayer.duration()/1000
                if begin_time < end_video and len(marks) > 0:
                    i = len(marks)
                    out_path = os.path.join(dirPath, prefix+str(i)+".mp4")
                    clip = video.subclip(begin_time, end_time)
                    clip.write_videofile(out_path)
                self.errorLabel.setText('Clips saved at ' + dirPath)
                QMessageBox.information(self.wid, 'Sucess',
                        'Clips succesfuly saved')
            except:
                self.errorLabel.setText('Error: Could not save file.')
                QMessageBox.warning(self.wid, 'Error',
                        'Could not save file. Check permissions')

    @pyqtSlot()
    def createMark(self):
        state = self.mediaPlayer.state()
        if state == QMediaPlayer.PlayingState or state == \
                QMediaPlayer.PausedState:
            self.clipsWidget.new_mark(self.mediaPlayer.position()/1000,
                    self.isNewMark)
            self.isNewMark = not self.isNewMark


def _create_button(icon):
    button = QPushButton()
    button.setIcon(icon)
    button.setEnabled(False)
    return button

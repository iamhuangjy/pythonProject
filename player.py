import _thread
import random
from urllib.request import urlretrieve

from PyQt5.QtWidgets import (QWidget, QDesktopWidget,
                             QMessageBox, QHBoxLayout, QVBoxLayout, QSlider, QListWidget,
                             QPushButton, QLabel, QFileDialog, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os, time
import configparser

from urllib3.connectionpool import xrange

from music_api import kugou_api
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg


class Player(QWidget):
    def __init__(self):
        super().__init__()
        self.startTimeLabel = QLabel('00:00')
        self.endTimeLabel = QLabel('00:00')
        self.slider = QSlider(Qt.Horizontal, self)
        self.PlayModeBtn = QPushButton(self)
        self.playBtn = QPushButton(self)
        self.prevBtn = QPushButton(self)
        self.nextBtn = QPushButton(self)
        self.openBtn = QPushButton(self)
        self.saveBtn = QPushButton(self)
        self.queryList = QListWidget()
        self.musicList = QListWidget()
        self.song_formats = ['mp3', 'm4a', 'flac', 'wav', 'ogg']
        self.songs_list = []
        self.cur_playing_song = ''
        self.is_pause = True
        self.player = QMediaPlayer()
        self.is_switching = False
        self.playMode = 0
        self.settingfilename = 'config.ini'
        self.textLable = QLabel('前进的路上，也要记得欣赏沿途的风景呀!')
        self.infoLabel = QLabel('Mculover666 v2.0.0')
        self.ui = QLabel('下载：')

        self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play.png)}")
        self.playBtn.setFixedSize(24, 24)
        self.nextBtn.setStyleSheet("QPushButton{border-image: url(resource/image/next.png)}")
        self.nextBtn.setFixedSize(24, 24)
        self.prevBtn.setStyleSheet("QPushButton{border-image: url(resource/image/prev.png)}")
        self.prevBtn.setFixedSize(24, 24)
        self.openBtn.setStyleSheet("QPushButton{border-image: url(resource/image/open.png)}")
        self.openBtn.setFixedSize(24, 24)
        self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/sequential.png)}")
        self.PlayModeBtn.setFixedSize(24, 24)
        self.saveBtn.setText("保存")
        self.saveBtn.setFixedSize(48, 24)
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)

        # 搜索框
        self.qBoxLayout = QHBoxLayout()
        # 输入框
        self.textbox = QLineEdit(self)
        self.textbox.setToolTip("输入查询内容")
        self.queryBtn = QPushButton(self)
        self.queryBtn.setText("搜索")
        self.queryBtn.clicked.connect(self.clickQueryBbtn)
        self.qBoxLayout.addWidget(self.textbox)
        self.qBoxLayout.addWidget(self.queryBtn)

        self.horizontalHeader = ["曲名", "歌手", "时长", "操作"]
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(self.horizontalHeader)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.table)

        self.hBoxSlider = QHBoxLayout()
        self.hBoxSlider.addWidget(self.startTimeLabel)
        self.hBoxSlider.addWidget(self.slider)
        self.hBoxSlider.addWidget(self.endTimeLabel)

        self.hBoxButton = QHBoxLayout()
        self.hBoxButton.addWidget(self.PlayModeBtn)
        self.hBoxButton.addStretch(1)
        self.hBoxButton.addWidget(self.prevBtn)
        self.hBoxButton.addWidget(self.playBtn)
        self.hBoxButton.addWidget(self.nextBtn)
        self.hBoxButton.addStretch(1)
        self.hBoxButton.addWidget(self.openBtn)
        self.hBoxButton.addStretch(1)
        self.hBoxButton.addWidget(self.saveBtn)

        self.vBoxControl = QVBoxLayout()
        self.vBoxControl.addLayout(self.hBoxSlider)
        self.vBoxControl.addLayout(self.hBoxButton)

        self.wavBoxAbout = QHBoxLayout()
        vb = CustomViewBox()
        vb.setMouseEnabled(x=True, y=False)
        vb.setMenuEnabled(False)
        self.plt3 = pg.PlotWidget(viewBox=vb)
        self.hl = pg.LinearRegionItem([0, 100])
        self.hl.setBounds([0, 1000])
        self.minX = 0
        self.maxX = 100000

        def update():
            self.hl.setZValue(10)
            self.minX, self.maxX = self.hl.getRegion()

        self.hl.sigRegionChanged.connect(update)
        self.plt3.addItem(self.hl)

        self.wavBoxAbout.addWidget(self.plt3)

        self.hBoxAbout = QHBoxLayout()
        self.hBoxAbout.addWidget(self.textLable)
        self.hBoxAbout.addWidget(self.ui)
        self.hBoxAbout.addWidget(self.infoLabel)

        self.vboxMain = QVBoxLayout()
        self.vboxMain.addLayout(self.qBoxLayout)
        self.vboxMain.addLayout(self.mainLayout)
        self.vboxMain.addWidget(self.musicList)
        self.vboxMain.addLayout(self.vBoxControl)
        self.vboxMain.addLayout(self.wavBoxAbout)
        self.vboxMain.addLayout(self.hBoxAbout)
        self.vboxMain.setStretchFactor(self.qBoxLayout, 1)
        self.vboxMain.setStretchFactor(self.mainLayout, 2)
        self.vboxMain.setStretchFactor(self.musicList, 2)
        self.vboxMain.setStretchFactor(self.vBoxControl, 1.5)
        self.vboxMain.setStretchFactor(self.wavBoxAbout, 2)
        self.vboxMain.setStretchFactor(self.hBoxAbout, 1)
        self.setLayout(self.vboxMain)

        self.saveBtn.clicked.connect(self.cutMp3)
        self.openBtn.clicked.connect(self.openMusicFloder)
        self.playBtn.clicked.connect(self.playMusic)
        self.prevBtn.clicked.connect(self.prevMusic)
        self.nextBtn.clicked.connect(self.nextMusic)
        self.musicList.itemDoubleClicked.connect(self.doubleClicked)
        self.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider.value()))
        self.PlayModeBtn.clicked.connect(self.playModeSet)

        self.loadingSetting()

        self.initUI()

    # 初始化界面
    def initUI(self):
        self.resize(1200, 600)
        self.center()
        self.setWindowTitle('音乐播放器')
        self.setWindowIcon(QIcon('resource/image/favicon.ico'))
        self.show()

    # 窗口显示居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 打开文件夹
    def openMusicFloder(self):
        self.cur_path = QFileDialog.getExistingDirectory(self, "选取音乐文件夹", './')
        if self.cur_path:
            self.showMusicList()
            self.cur_playing_song = ''
            self.startTimeLabel.setText('00:00')
            self.endTimeLabel.setText('00:00')
            self.slider.setSliderPosition(0)
            self.updateSetting()
            self.is_pause = True
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play.png)}")

    # 显示音乐列表
    def showMusicList(self):
        self.musicList.clear()
        for song in os.listdir(self.cur_path):
            if song.split('.')[-1] in self.song_formats:
                self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                self.musicList.addItem(song)
        self.musicList.setCurrentRow(0)
        if self.songs_list:
            self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]

    # 提示
    def Tips(self, message):
        QMessageBox.about(self, "提示", message)

    # 设置当前播放的音乐
    def setCurPlaying(self):
        self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cur_playing_song)))

    # 播放/暂停播放
    def playMusic(self):
        if self.musicList.count() == 0:
            self.Tips('当前路径内无可播放的音乐文件')
            return
        if not self.player.isAudioAvailable():
            self.setCurPlaying()
        if self.is_pause or self.is_switching:
            self.plt3.plot().clear()
            self.drawWavImageByPygraph(self.cur_playing_song)
            self.player.play()
            self.is_pause = False
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/pause.png)}")
        elif (not self.is_pause) and (not self.is_switching):
            self.player.pause()
            self.is_pause = True
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play.png)}")

    # 上一曲
    def prevMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips('当前路径内无可播放的音乐文件')
            return
        pre_row = self.musicList.currentRow() - 1 if self.musicList.currentRow() != 0 else self.musicList.count() - 1
        self.musicList.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 下一曲
    def nextMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips('当前路径内无可播放的音乐文件')
            return
        next_row = self.musicList.currentRow() + 1 if self.musicList.currentRow() != self.musicList.count() - 1 else 0
        self.musicList.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 双击歌曲名称播放音乐
    def doubleClicked(self):
        self.slider.setValue(0)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 根据名称查询音乐
    def clickQueryBbtn(self):
        textboxValue = self.textbox.text()
        ss = kugou_api.kugou_search_api(textboxValue)
        items = ["song_name", "song_user", "song_time", "down"]
        for song in ss:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for j in range(len(items)):
                if j == len(items) - 1:
                    self.table.setCellWidget(row, j, self.buttonForRow(song.get("song_name"), song.get("song_url")))
                    break
                self.table.setItem(row, j, QTableWidgetItem(str(song.get(items[j]))))
        self.musicList.setCurrentRow(0)
        # 清空输入框信息情歌王
        self.textbox.setText("")

    # 根据播放模式自动播放，并刷新进度条
    def playByMode(self):
        # 刷新进度条
        if (not self.is_pause) and (not self.is_switching):
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.slider.value() + 1000)
        self.startTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.endTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        # 顺序播放
        if (self.playMode == 0) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        # 单曲循环
        elif (self.playMode == 1) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        # 随机播放
        elif (self.playMode == 2) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.musicList.setCurrentRow(random.randint(0, self.musicList.count() - 1))
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False

    # 更新配置文件
    def updateSetting(self):
        config = configparser.ConfigParser()
        config.read(self.settingfilename)
        if not os.path.isfile(self.settingfilename):
            config.add_section('MP3Player')
        config.set('MP3Player', 'PATH', self.cur_path)
        config.write(open(self.settingfilename, 'w'))

    # 加载配置文件
    def loadingSetting(self):
        config = configparser.ConfigParser()
        config.read(self.settingfilename)
        if not os.path.isfile(self.settingfilename):
            return
        self.cur_path = config.get('MP3Player', 'PATH')
        self.showMusicList()

    # 播放模式设置
    def playModeSet(self):
        # 设置为单曲循环模式
        if self.playMode == 0:
            self.playMode = 1
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/circulation.png)}")
        # 设置为随机播放模式
        elif self.playMode == 1:
            self.playMode = 2
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/random.png)}")
        # 设置为顺序播放模式
        elif self.playMode == 2:
            self.playMode = 0
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/sequential.png)}")

    # 确认用户是否要真正退出
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "确定要退出吗？", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    """
    根据歌曲名和url下载歌曲，每一首歌的下载，都是一个新的线程
    song_name : 歌曲名称
    song_url : 歌曲下载的url
    """

    def down_song(self, song_name, song_url):
        # 文件名中":"属于特殊字符，在文件保存中会出错，将之替换为中文的"："就没问题
        if ":" in song_name:
            song_name = song_name.replace(":", "：")
        if "/" in song_name:
            song_name = song_name.replace("/", "-")
        if "." in song_name:
            song_name = song_name.replace(".", "-")
        print(song_name, " : ", song_url)
        # 添加提示
        self.ui.setText("正在下载: 《{}》...".format(song_name))
        # 下载保存
        urlretrieve(song_url, r"{}.mp3".format(self.cur_path + '/' + song_name))
        # 添加提示
        self.ui.setText("下载完成: 《{}》".format(song_name))

    """
    点击下载按钮触发的槽函数
    row : 需要下载的歌曲在列表中的行号
    table_type : 下载按钮所在的table_widget
    """

    def btn_down_click(self, song_name, song_url):
        # 根据列表行号和控件名称获取对应的歌曲url和歌曲名称
        if len(song_name) == 0 or len(song_url) == 0:
            return
        # 创建一个下载线程
        try:
            _thread.start_new_thread(self.down_song, (song_name, song_url))
        except:
            print("Error: 无法启动线程")

    # 重载键盘回车
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            # print('Space')
            self.btn_search_click()

    # 列表内添加按钮
    def buttonForRow(self, song_name, song_url):
        widget = QWidget()
        # 下载
        downloadBtn = QPushButton('下载')
        downloadBtn.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')
        downloadBtn.clicked.connect(lambda: self.btn_down_click(song_name, song_url))
        hLayout = QHBoxLayout()
        hLayout.addWidget(downloadBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    """
    mp3转wav
    mp3 : mp3文件全路径
    wav : mav文件存储路径
    """

    def mp32wav(self, mp3, wav):
        sound = AudioSegment.from_mp3(mp3)
        sound.export(wav, format="wav")

    """
    剪切mp3文件
    mp3 : mp3文件全路径
    start : 开始时间--毫秒
    end : 结束时间--毫秒
    """

    def cutMp3(self):
        if self.maxX == 0:
            print("请选择文件内容")
        else:
            song = AudioSegment.from_mp3(self.cur_playing_song)
            slice = song[self.minX: self.maxX]
            slice.export(self.cur_path+'/'+'test1.mp3', format="mp3")

    """
    读取wav文件内容，画出波形图,利用的是Matplotlib
    wav : wav文件全路径
    """

    def drawWavImageByMatplotlib(self, wav):
        audiofile = AudioSegment.from_file(wav)
        data = np.fromstring(audiofile._data, np.int16)
        channels = []
        for chn in xrange(audiofile.channels):
            channels.append(data[chn::audiofile.channels])
        plt.title("Night.wav's Frames")
        plt.subplot(211)
        plt.plot(channels[0][0::1000], color='green')
        plt.subplot(212)
        plt.plot(channels[1][0::1000], color='red')
        plt.show()

    """
    读取wav文件内容，画出波形图,利用的是Pygraph
    wav : wav文件全路径
    """

    def drawWavImageByPygraph(self, wav):
        self.plt3.plot().clear()
        x = np.arange(1000)
        y = np.random.normal(200, 50, 1000)
        pen = pg.mkPen(color='green')
        self.plt3.plot(x, y, pen=pen)


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.PanMode)

    def mouseClickEvent(self, ev):
        if ev.button() == pg.QtCore.Qt.RightButton:
            self.autoRange()

    def mouseDragEvent(self, ev):
        pg.ViewBox.mouseDragEvent(self, ev)

    def wheelEvent(self, ev, axis=None):
        # pg.ViewBox.wheelEvent(self, ev, axis)
        ev.ignore()

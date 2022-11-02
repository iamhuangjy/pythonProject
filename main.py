#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
"""
MP3 player
 pyinstaller -F main.py --additional-hooks=extra-hooks --additional-hooks-dir "./extra-hooks"
 需要创建一个extra-hooks的文件夹
 然后创建一个hook-librosa.py文件
 最后输入一下内容
 from PyInstaller.utils.hooks import collect_data_files
 datas = collect_data_files('librosa')

author: Mculover666
version: v2.0.0
"""
 
import sys
from player import Player
from PyQt5.QtWidgets import (QApplication)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Player()
    sys.exit(app.exec_())
#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
"""
MP3 player
 
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
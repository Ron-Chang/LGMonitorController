#!/usr/bin/env python3
"""
https://pypi.org/project/hid/
https://github.com/apmorton/pyhidapi
"""

import re
import sys

import hid
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lib import ultragear


class Gui(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('27g950controller')

        mainLayout = QVBoxLayout(self)

        self.selection_buttons_layout = QHBoxLayout(self)
        self.selection_buttons_layout.addWidget(QLabel('<b>Select monitors: </b>'))
        mainLayout.addLayout(self.selection_buttons_layout)

        mainLayout.addWidget(QLabel(''))

        power_buttons_layout = QGridLayout(self)
        power_buttons_layout.addWidget(QLabel('<b>Power</b>'), 0, 0, 1, 2)
        x = QPushButton('Turn off')
        x.clicked.connect(self.turn_off)
        power_buttons_layout.addWidget(x, 1, 0)
        x = QPushButton('Turn on')
        x.clicked.connect(self.turn_on)
        power_buttons_layout.addWidget(x, 1, 1)
        mainLayout.addLayout(power_buttons_layout)

        mainLayout.addWidget(QLabel(''))

        brightness_buttons_layout = QGridLayout(self)
        brightness_buttons_layout.addWidget(QLabel('<b>Brightness</b>'), 0, 0, 1, 6)
        for i in range(1, 13):
            x = QPushButton(str(i))
            x.clicked.connect(lambda _, i=i: self.set_brightness(i))
            row = 1 + i // 7
            col = i - 1 - (6 if i > 6 else 0)
            brightness_buttons_layout.addWidget(x, row, col)
        mainLayout.addLayout(brightness_buttons_layout)

        mainLayout.addWidget(QLabel(''))

        config_buttons_layout = QGridLayout(self)
        config_buttons_layout.addWidget(QLabel('<b>Lighting mode</b>'), 0, 0, 1, 4)
        for i in range(4):
            x = QPushButton(f'Color {i + 1}')
            x.clicked.connect(lambda _, i=i: self.set_static_color(i + 1))
            config_buttons_layout.addWidget(x, 1, i)
        x = QPushButton('Peaceful')
        x.clicked.connect(self.set_peaceful_color)
        config_buttons_layout.addWidget(x, 2, 0, 1, 2)
        x = QPushButton('Dynamic')
        x.clicked.connect(self.set_dynamic_color)
        config_buttons_layout.addWidget(x, 2, 2, 1, 2)
        mainLayout.addLayout(config_buttons_layout)

        mainLayout.addWidget(QLabel(''))

        edit_button_sentry_layout = QHBoxLayout(self)
        edit_buttons_buttons_layout = QHBoxLayout(self)
        x = QLabel('Enter new color: ')
        edit_button_sentry_layout.addWidget(x)
        self.colorInputBox = QLineEdit('27e5ff')
        self.colorInputBox.setFixedWidth(150)
        self.colorInputBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily('Hack Nerd Font')
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.colorInputBox.setFont(font)
        self.colorInputBox.textChanged.connect(self.validate_new_color)
        edit_button_sentry_layout.addWidget(self.colorInputBox)
        self.colorValidationOutputBox = QLabel('valid')
        self.colorValidationOutputBox.setAlignment(Qt.AlignmentFlag.AlignRight)
        edit_button_sentry_layout.addWidget(self.colorValidationOutputBox)
        for i in range(4):
            x = QPushButton(f'Set {i + 1}')
            x.clicked.connect(lambda _, i=i: self.set_color(i + 1))
            edit_buttons_buttons_layout.addWidget(x)
        edit_buttons_layout = QVBoxLayout(self)

        edit_buttons_layout.addWidget(QLabel('<b>Edit static colors</b>'))
        edit_buttons_layout.addLayout(edit_button_sentry_layout)
        edit_buttons_layout.addLayout(edit_buttons_buttons_layout)
        mainLayout.addLayout(edit_buttons_layout)

    def init_monitors(self):
        monitors = ultragear.find_monitors()
        if not monitors:
            for item in self.layout().children():
                self.layout().removeItem(item)
            self.layout().addWidget(QLabel('No monitors found'))
            return

        self.devs = []
        for monitor in monitors:
            self.devs.append(hid.Device(path=monitor['path']))

        self.selection = list(range(len(self.devs)))

        for i in self.selection:
            x = QCheckBox(str(i + 1))
            x.setCheckState(Qt.CheckState.Checked)
            x.stateChanged.connect(lambda checked, i=i: self.update_selection(i, checked))
            self.selection_buttons_layout.addWidget(x)

    def cleanup(self):
        if hasattr(self, 'devs'):
            for dev in self.devs:
                dev.close()

    def is_valid_color(self, color):
        return re.match('^[0-9a-f]{6}$', color)

    def validate_new_color(self, text):
        s = 'valid' if self.is_valid_color(text.lower()) else 'invalid'
        self.colorValidationOutputBox.setText(s)

    def update_selection(self, monitor_num, checked):
        if checked == 0:
            self.selection.remove(monitor_num)
        elif checked == 2:
            self.selection.append(monitor_num)

    def send_command(self, cmd):
        devs = []
        for i in self.selection:
            devs.append(self.devs[i])
        ultragear.send_command(cmd, devs)

    def turn_on(self):
        cmd = ultragear.control_commands['turn_on']
        self.send_command(cmd)

    def turn_off(self):
        cmd = ultragear.control_commands['turn_off']
        self.send_command(cmd)

    def set_static_color(self, color):
        cmd = ultragear.control_commands['color' + str(color)]
        self.send_command(cmd)

    def set_peaceful_color(self):
        cmd = ultragear.control_commands['color_peaceful']
        self.send_command(cmd)

    def set_dynamic_color(self):
        cmd = ultragear.control_commands['color_dynamic']
        self.send_command(cmd)

    def set_brightness(self, brt):
        cmd = ultragear.brightness_commands[brt]
        self.send_command(cmd)

    def set_color(self, slot):
        color = self.colorInputBox.text().lower()
        if not self.is_valid_color(color):
            return
        cmd = ultragear.get_set_color_command(slot, color)
        self.send_command(cmd)


app = QApplication(sys.argv)
try:
    x = Gui()
    x.init_monitors()
    x.show()
    sys.exit(app.exec())
finally:
    if 'x' in locals():
        x.cleanup()

#
# This file is part of the TelemFFB distribution (https://github.com/walmis/TelemFFB).
# Copyright (c) 2023 Valmantas Palikša.
# Copyright (c) 2023 Micah Frisby
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import inspect
import json
import logging
import os
import re

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon, QColor, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton, QStyle,
                             QToolButton, QCheckBox, QComboBox, QLineEdit, QFileDialog, QSpinBox, QHBoxLayout)

from telemffb.ButtonPressThread import ButtonPressThread
from telemffb.custom_widgets import (InfoLabel, NoWheelSlider, NoWheelNumberSlider, vpf_purple, t_purple, Toggle, AnimatedToggle)
from telemffb.ConfiguratorDialog import ConfiguratorDialog
from telemffb.hw.ffb_rhino import HapticEffect
from telemffb.utils import validate_vpconf_profile, dbprint, HiDpiPixmap

from . import globals as G
from . import xmlutils


class SettingsLayout(QGridLayout):
    expanded_items = []
    prereq_list = []
    ##########
    # debug settings
    show_slider_debug = False   # set to true for slider values shown
    show_order_debug = False    # set to true for order numbers shown
    bump_up = True              # set to false for no row bumping up

    all_sliders = []

    def __init__(self, parent=None, mainwindow=None):
        super(SettingsLayout, self).__init__(parent)
        result = None
        if G.settings_mgr.current_sim != 'nothing':
            a, b, result = xmlutils.read_single_model(G.settings_mgr.current_sim, G.settings_mgr.current_aircraft_name)

        self.mainwindow = mainwindow
        if result is not None:
            self.build_rows(result)
        self.device = HapticEffect()
        self.setColumnMinimumWidth(7, 20)
        self.trigger_form_reload = True

    def handleScrollKeyPressEvent(self, event):
        # Forward key events to each slider in the layout
        for i in range(self.count()):
            item = self.itemAt(i)
            if isinstance(item.widget(), NoWheelSlider()):
                item.widget().handleKeyPressEvent(event)

    def append_prereq_count(self, datalist):
        for item in datalist:
            item['prereq_count'] = ''
            item['has_expander'] = ''
            for pr in self.prereq_list:
                if item['name'] == pr['prereq']:
                    item['prereq_count'] = pr['count']
            p_count = 0
            if item['prereq_count'] != '':
                p_count = int(item['prereq_count'])

            if p_count > 1 or (p_count == 1 and item['hasbump'] != 'true'):
                item['has_expander'] = 'true'

    def has_bump(self, datalist):
        for item in datalist:
            item['hasbump'] = ''
            bumped_up = item['order'][-2:] == '.1'
            if bumped_up:
                for b in datalist:
                    if item['prereq'] == b['name']:
                        b['hasbump'] = 'true'

    def add_expanded(self, datalist):
        for item in datalist:
            item['parent_expanded'] = ''
            for exp in self.expanded_items:
                if item['prereq'] == exp:
                    item['parent_expanded'] = 'true'
                else:
                    item['parent_expanded'] = 'false'

    def is_visible(self, datalist):

        for item in datalist:
            bumped_up = item['order'][-2:] == '.1'
            iv = 'false'
            cond = ''
            if item['prereq'] == '':
                iv = 'true'
                cond = 'no prereq needed'
            else:
                for p in datalist:
                    if item['prereq'] == p['name']:
                        if p['value'].lower() == 'true':
                            if p['has_expander'].lower() == 'true':
                                if p['name'] in self.expanded_items and p['is_visible'] == 'true':
                                    iv = 'true'
                                    cond = 'item parent expanded'
                                else:
                                    if p['hasbump'].lower() == 'true':
                                        if bumped_up:
                                            iv = 'true'
                                            cond = 'parent hasbump & bumped'
                            else:
                                if p['is_visible'].lower() == 'true':
                                    if p['hasbump'].lower() == 'true':
                                        if bumped_up:
                                            iv = 'true'
                                            cond = 'parent hasbump & bumped no expander par vis'
                        break

            item['is_visible'] = iv
            # for things not showing debugging:
            # if iv.lower() == 'true':
            #     print (f"{item['displayname']} visible because {cond}")

    def eliminate_invisible(self, datalist):
        newlist = []
        for item in datalist:
            if item['is_visible'] == 'true':
                newlist.append(item)

        for item in newlist:
            item['prereq_count'] = '0'
            pcount = 0
            for row in newlist:
                if row['prereq'] == item['name']:
                    pcount += 1
                    if row['has_expander'].lower() == 'true':
                        pcount -= 1
            item['prereq_count'] = str(pcount)

        return newlist

    def read_active_prereqs(self, datalist):
        p_list = []
        for item in datalist:
            found = False
            count = 0
            for p in datalist:
                if item['name'] == p['prereq']:
                    count += 1
                    found = True
                # If 'prereq' is not in the list, add a new entry
            if found:
                p_list.append({'prereq': item['name'], 'value': 'False', 'count': count})
        return p_list

    def build_rows(self, datalist):
        sorted_data = sorted(datalist, key=lambda x: float(x['order']))
        # self.prereq_list = xmlutils.read_prereqs()
        self.prereq_list = self.read_active_prereqs(sorted_data)
        self.has_bump(sorted_data)
        self.append_prereq_count(sorted_data)
        self.add_expanded(sorted_data)
        self.is_visible(sorted_data)
        newlist = self.eliminate_invisible(sorted_data)

        def is_expanded(item):
            if item['name'] in self.expanded_items:
                return True
            for row in sorted_data:
                if row['name'] == item['prereq'] and is_expanded(row):
                    return True
            return False

        i = 0
        for item in newlist:
            bumped_up = item['order'][-2:] == '.1'
            rowdisabled = False
            addrow = False
            is_expnd = is_expanded(item)
            # print(f"{item['order']} - {item['value']} - b {bumped_up} - hb {item['hasbump']} - ex {is_expnd} - hs {item['has_expander']} - pex {item['parent_expanded']} - iv {item['is_visible']} - pcount {item['prereq_count']} - {item['displayname']} - pr {item['prereq']}")
            if item['is_visible'].lower() == 'true':
                i += 1
                if bumped_up:
                    if self.bump_up:  # debug
                        i -= 1   # bump .1 setting onto the enable row
                self.generate_settings_row(item, i, rowdisabled)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.addItem(spacerItem, i+1, 1, 1, 1)
        # Give entry column a high stretch factor, all others remain default 0.
        # When window is resized, the entry column will grow to take up all the new space
        self.setColumnStretch(4, 10)

        # print (f"{i} rows with {self.count()} widgets")

    def reload_caller(self):
        # caller_frame = inspect.currentframe().f_back
        # caller_name = caller_frame.f_code.co_name
        # dbprint("blue", f"RELOAD_CALLER was called by {caller_name}")
        if not self.trigger_form_reload:
            self.trigger_form_reload = True  # reset back to true for next iteration
        else:
            self.reload_layout(None)

    def reload_layout(self, result=None):
        # stack = inspect.stack()
        # for frame_info in stack:
        #     dbprint("green", f"Function {frame_info.function} in {frame_info.filename} at line {frame_info.lineno}")
        self.clear_layout()
        if result is None:
            cls, pat, result = xmlutils.read_single_model(G.settings_mgr.current_sim, G.settings_mgr.current_aircraft_name)
            G.settings_mgr.current_pattern = pat
        if result is not None:
            self.build_rows(result)

    def clear_layout(self):
        layout = self.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout:
                        self._clear_sub_layout(sub_layout)
                        sub_layout.deleteLater()

    def _clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self._clear_sub_layout(sub_layout)
                    sub_layout.deleteLater()

    def generate_settings_row(self, item, i, rowdisabled=False):
        self.setRowMinimumHeight(i, 25)
        entry_colspan = 2
        lbl_colspan = 2

        exp_col = 0
        chk_col = 1
        lbl_col = 2
        entry_col = 4
        unit_col = 5
        val_col = 6
        erase_col = 7
        fct_col = 10
        ord_col = 11

        validvalues = item['validvalues'].split(',')

        if self.show_order_debug:
            order_lbl = QLabel()
            order_lbl.setText(item['order'])
            order_lbl.setMaximumWidth(30)
            self.addWidget(order_lbl, i, ord_col)

        erase_button = QPushButton() # Create erase button at beginning so behavior can be modified per widget type if necessary

        # booleans get a checkbox
        if item['datatype'] == 'bool':

            checkbox = Toggle(
                checked_color=vpf_purple,
                bar_color=t_purple
            )

            # checkbox = AnimatedToggle(
            #     checked_color="#ab37c8",
            #     pulse_checked_color="#44ab37c8"
            # )
            checkbox.setMaximumSize(QtCore.QSize(45, 30))
            checkbox.setMinimumSize(QtCore.QSize(45, 30))
            checkbox.setObjectName(f"cb_{item['name']}")
            # checkbox.blockSignals(True)
            if item['value'].lower() == 'false':
                checkbox.setCheckState(0)
                rowdisabled = True
            else:
                checkbox.setCheckState(2)
            checkbox.blockSignals(False)
            if item['prereq'] != '':
                chk_col += 1
            self.addWidget(checkbox, i, chk_col)
            checkbox.stateChanged.connect(lambda state, name=item['name']: self.checkbox_changed(name, state))

        if item['unit'] is not None and item['unit'] != '':
            entry_colspan = 1
            unit_dropbox = QComboBox()
            unit_dropbox.blockSignals(True)
            if item['unit'] == 'hz':
                unit_dropbox.addItem('hz')
                unit_dropbox.setCurrentText('hz')
            elif item['unit'] == 'deg':
                unit_dropbox.addItem('deg')
                unit_dropbox.setCurrentText('deg')
            else:
                unit_dropbox.addItems(validvalues)
                unit_dropbox.setCurrentText(item['unit'])
            unit_dropbox.setObjectName(f"ud_{item['name']}")
            unit_dropbox.currentIndexChanged.connect(self.unit_dropbox_changed)
            self.addWidget(unit_dropbox, i, unit_col)
            unit_dropbox.blockSignals(False)
            unit_dropbox.setDisabled(rowdisabled)

        # everything has a name, except for things that have a checkbox *and* slider
        label = InfoLabel(f"{item['displayname']}")
        label.setToolTip(item['info'])
        label.setMinimumHeight(20)
        label.setMinimumWidth(20)
        # label.setMaximumWidth(150)
        if item['order'][-2:] == '.1':
            olditem = self.itemAtPosition(i, lbl_col)
            if olditem is not None:
                self.remove_widget(olditem)
            # for p_item in self.prereq_list:
            #     if p_item['prereq'] == item['prereq'] and p_item['count'] == 1:
            #         olditem = self.itemAtPosition(i, self.exp_col)
            #         if olditem is not None:
            #             self.remove_widget(olditem)
        if item['prereq'] != '' and item['hasbump'] != 'true' and item['order'][-2:] != '.1':
            # label.setStyleSheet("QLabel { padding-left: 20px; }")
            lbl_colspan = 1
            lbl_col += 1
        self.addWidget(label, i, lbl_col, 1, lbl_colspan)

        slider = NoWheelSlider()
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.setObjectName(f"sld_{item['name']}")

        n_slider = NoWheelNumberSlider()
        n_slider.setOrientation(QtCore.Qt.Horizontal)
        n_slider.setObjectName(f"sld_{item['name']}")

        d_slider = NoWheelSlider()
        d_slider.setOrientation(QtCore.Qt.Horizontal)
        d_slider.setObjectName(f"dsld_{item['name']}")

        df_slider = NoWheelSlider()
        df_slider.setOrientation(QtCore.Qt.Horizontal)
        df_slider.setObjectName(f"dfsld_{item['name']}")

        m_butt = QPushButton("-")
        m_butt.setFixedSize(20, 20)
        m_butt.setStyleSheet("""
            QPushButton {
                font-size: 16px;  /* Adjust the font size */
                font-family: Cascadia Code;
                font-weight: bold;
                color: black;
                padding: 0px;
                border: none;  /* Remove any border */
                margin: 0px;   /* Remove any margin */
                background-color: transparent;  /* Transparent background */
            }
            QPushButton:hover {
                background-color: #ddd;  /* Optional: Change background on hover */
            }
            QPushButton:pressed {
                background-color: #bbb;  /* Optional: Change background on press */
            }
        """)

        # Create the "+" button
        p_butt = QPushButton("+")
        p_butt.setFixedSize(20, 20)
        p_butt.setStyleSheet("""
            QPushButton {
                font-size: 16px;  /* Adjust the font size */
                font-family: Cascadia Code;
                font-weight: bold;
                color: black;
                padding: 0px;
                border: none;  /* Remove any border */
                margin: 0px;   /* Remove any margin */
                background-color: transparent;  /* Transparent background */
            }
            QPushButton:hover {
                background-color: #ddd;  /* Optional: Change background on hover */
            }
            QPushButton:pressed {
                background-color: #bbb;  /* Optional: Change background on press */
            }
        """)

        line_edit = QLineEdit()
        line_edit.blockSignals(True)
        # unit?
        line_edit.setText(item['value'])
        line_edit.blockSignals(False)
        line_edit.setAlignment(Qt.AlignHCenter)
        line_edit.setObjectName(f"vle_{item['name']}")
        line_edit.setMinimumWidth(150)
        line_edit.editingFinished.connect(self.line_edit_changed)

        expand_button = QToolButton()
        if item['name'] in self.expanded_items:
            expand_button.setArrowType(Qt.DownArrow)
        else:
            expand_button.setArrowType(Qt.RightArrow)
        expand_button.setMaximumWidth(24)
        expand_button.setMinimumWidth(24)
        expand_button.setObjectName(f"ex_{item['name']}")
        expand_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        expand_button.setStyleSheet("""
            QToolButton {
                font-size: 16px;  /* Adjust the font size */
                font-family: Cascadia Code;
                font-weight: bold;
                color: black;
                padding: 0px;
                border: none;  /* Remove any border */
                margin: 0px;   /* Remove any margin */
                background-color: transparent;  /* Transparent background */
            }
            QToolButton:hover {
                background-color: #ddd;  /* Optional: Change background on hover */
            }
            QToolButton:pressed {
                background-color: #bbb;  /* Optional: Change background on press */
            }
        """)
        expand_button.clicked.connect(self.expander_clicked)

        usb_button_text = f"Button {item['value']}"
        if item['value'] == '0':
            usb_button_text = 'Click to Configure'
        self.usbdevice_button = QPushButton(usb_button_text)
        self.usbdevice_button.setMinimumWidth(150)
        self.usbdevice_button.setObjectName(f"pb_{item['name']}")
        self.usbdevice_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.usbdevice_button.clicked.connect(self.usb_button_clicked)

        value_label = QLabel()
        value_label.setAlignment(Qt.AlignVCenter)
        value_label.setMaximumWidth(50)
        value_label.setObjectName(f"vl_{item['name']}")
        sliderfactor = QLabel(f"{item['sliderfactor']}")
        if self.show_slider_debug:
            sliderfactor.setMaximumWidth(20)
        else:
            sliderfactor.setMaximumWidth(0)
        sliderfactor.setObjectName(f"sf_{item['name']}")

        if item['datatype'] == 'float' or \
                item['datatype'] == 'negfloat':

            # print(f"label {value_label.objectName()} for slider {slider.objectName()}")
            factor = float(item['sliderfactor'])
            if '%' in item['value']:
                floatval = float(item['value'].replace('%', ''))
                val = floatval / 100
            else:
                val = float(item['value'])

            pctval = int((val / factor) * 100)
            if self.show_slider_debug:
                logging.debug(f"read value: {item['value']}  factor: {item['sliderfactor']} slider: {pctval}")
            slider.blockSignals(True)
            if validvalues is None or validvalues == '':
                pass
            else:
                slider.setRange(int(validvalues[0]), int(validvalues[1]))
            slider.setValue(pctval)
            value_label.setText(str(pctval) + '%')

            slider.valueChanged.connect(lambda value: self.slider_changed(write=False))  # update label on every change
            slider.delayedValueChanged.connect(lambda value: self.slider_changed(write=True))  # only write config when delay timer triggers
            sl_layout = QHBoxLayout()
            m_butt.clicked.connect(slider.decrease_single_step)
            p_butt.clicked.connect(slider.increase_single_step)
            sl_layout.addWidget(m_butt)
            sl_layout.addWidget(slider)
            sl_layout.addWidget(p_butt)
            self.addLayout(sl_layout, i, entry_col, 1, entry_colspan)
            self.addWidget(value_label, i, val_col, alignment=Qt.AlignVCenter)
            self.addWidget(sliderfactor, i, fct_col)

            slider.blockSignals(False)

        if item['datatype'] == 'n_float' :

            # print(f"label {value_label.objectName()} for slider {slider.objectName()}")
            factor = float(item['sliderfactor'])
            if '%' in item['value']:
                floatval = float(item['value'].replace('%', ''))
                val = floatval / 100
            else:
                val = float(item['value'])

            pctval = int((val / factor) * 100)
            if self.show_slider_debug:
                logging.debug(f"read value: {item['value']}  factor: {item['sliderfactor']} slider: {pctval}")
            n_slider.blockSignals(True)
            if validvalues is None or validvalues == '':
                pass
            else:
                n_slider.setRange(int(validvalues[0]), int(validvalues[1]))
            n_slider.setValue(pctval)
            value_label.setText(str(pctval) + '%')
            # value_label.setToolTip(f"Actual Value: %{int(val * 100)}")
            n_slider.valueChanged.connect(lambda value: self.slider_changed(write=False))  # update label on every change
            n_slider.delayedValueChanged.connect(lambda value: self.slider_changed(write=True)) # only write config when delay timer triggers
            # n_slider.sliderPressed.connect(self.sldDisconnect)
            # n_slider.sliderReleased.connect(self.sldReconnect)
            sl_layout = QHBoxLayout()
            m_butt.clicked.connect(n_slider.decrease_single_step)
            p_butt.clicked.connect(n_slider.increase_single_step)
            sl_layout.addWidget(m_butt)
            sl_layout.addWidget(n_slider)
            sl_layout.addWidget(p_butt)
            self.addLayout(sl_layout, i, entry_col, 1, entry_colspan)
            self.addWidget(value_label, i, val_col, alignment=Qt.AlignVCenter)
            self.addWidget(sliderfactor, i, fct_col)

            n_slider.blockSignals(False)

        if item['datatype'] == 'd_float':

            d_val = float(item['value'])
            factor = float(item['sliderfactor'])
            val = float(round(d_val / factor))
            if self.show_slider_debug:
                print(f"read value: {item['value']}   df_slider: {val}")
            df_slider.blockSignals(True)
            if validvalues is None or validvalues == '':
                pass
            else:
                df_slider.setRange(int(validvalues[0]), int(validvalues[1]))
            df_slider.setValue(round(val))
            value_label.setText(str(d_val))
            df_slider.valueChanged.connect(lambda value: self.df_slider_changed(write=False))  # update label on every change
            df_slider.delayedValueChanged.connect(lambda value: self.df_slider_changed(write=True)) # only write config when delay timer triggers
            sl_layout = QHBoxLayout()
            m_butt.clicked.connect(df_slider.decrease_single_step)
            p_butt.clicked.connect(df_slider.increase_single_step)
            sl_layout.addWidget(m_butt)
            sl_layout.addWidget(df_slider)
            sl_layout.addWidget(p_butt)
            self.addLayout(sl_layout, i, entry_col, 1, entry_colspan)
            self.addWidget(value_label, i, val_col)
            self.addWidget(sliderfactor, i, fct_col)
            df_slider.blockSignals(False)

        if item['datatype'] == 'cfgfloat':

            # print(f"label {value_label.objectName()} for slider {slider.objectName()}")

            if '%' in item['value']:
                pctval = int(item['value'].replace('%', ''))
            else:
                pctval = int(float(item['value']) * 100)
            pctval = int(round(pctval))
            # print (f"configurator value: {item['value']}   slider: {pctval}")
            slider.blockSignals(True)
            if validvalues is None or validvalues == '':
                pass
            else:
                slider.setRange(int(validvalues[0]), int(validvalues[1]))
            slider.setValue(pctval)
            value_label.setText(str(pctval) + '%')
            slider.valueChanged.connect(lambda value: self.cfg_slider_changed(write=False))  # update label on every change
            slider.delayedValueChanged.connect(lambda value: self.cfg_slider_changed(write=True)) # only write config when delay timer triggers
            sl_layout = QHBoxLayout()
            m_butt.clicked.connect(slider.decrease_single_step)
            p_butt.clicked.connect(slider.increase_single_step)
            sl_layout.addWidget(m_butt)
            sl_layout.addWidget(slider)
            sl_layout.addWidget(p_butt)
            self.addLayout(sl_layout, i, entry_col, 1, entry_colspan)
            self.addWidget(value_label, i, val_col)
            self.addWidget(sliderfactor, i, fct_col)

            slider.blockSignals(False)

        if item['datatype'] == 'd_int':

            d_val = int(item['value'])
            factor = float(item['sliderfactor'])
            val = int(round(d_val / factor))
            if self.show_slider_debug:
                print(f"read value: {item['value']}   d_slider: {val}")
            d_slider.blockSignals(True)
            if validvalues is None or validvalues == '':
                pass
            else:
                d_slider.setRange(int(validvalues[0]), int(validvalues[1]))
            d_slider.setValue(val)
            value_label.setText(str(d_val))
            d_slider.valueChanged.connect(lambda value: self.d_slider_changed(write=False))  # update label on every change
            d_slider.delayedValueChanged.connect(lambda value: self.d_slider_changed(write=True)) # only write config when delay timer triggers
            sl_layout = QHBoxLayout()
            m_butt.clicked.connect(d_slider.decrease_single_step)
            p_butt.clicked.connect(d_slider.increase_single_step)
            sl_layout.addWidget(m_butt)
            sl_layout.addWidget(d_slider)
            sl_layout.addWidget(p_butt)
            self.addLayout(sl_layout, i, entry_col, 1, entry_colspan)
            self.addWidget(value_label, i, val_col)
            self.addWidget(sliderfactor, i, fct_col)

            d_slider.blockSignals(False)

        if item['datatype'] == 'text':
            textbox = QLineEdit()
            textbox.setObjectName(f"le_{item['name']}")
            textbox.setText(item['value'])
            textbox.editingFinished.connect(self.textbox_changed)
            self.addWidget(textbox, i, entry_col, 1, entry_colspan)

        if item['datatype'] == 'spin_int':
            spin_box = QSpinBox()
            spin_box.blockSignals(True)
            spin_box.setValue(int(item['value']))
            spin_box.blockSignals(False)
            spin_box.setMinimumWidth(80)
            spin_box.setAlignment(Qt.AlignHCenter)
            spin_box.setObjectName(f"sb_{item['name']}")
            if validvalues is None or validvalues == '':
                pass
            else:
                spin_box.setMinimum(int(validvalues[0]))
                spin_box.setMaximum(int(validvalues[1]))
            spin_box.valueChanged.connect(self.spin_box_changed)
            self.addWidget(spin_box, i, entry_col, 1, entry_colspan, alignment=Qt.AlignLeft)

        if item['datatype'] == 'list' or item['datatype'] == 'anylist':
            dropbox = QComboBox()
            dropbox.setMinimumWidth(150)
            dropbox.setEditable(True)
            dropbox.lineEdit().setAlignment(QtCore.Qt.AlignHCenter)
            dropbox.setObjectName(f"db_{item['name']}")
            dropbox.addItems(validvalues)
            dropbox.blockSignals(True)
            dropbox.setCurrentText(item['value'])
            if item['datatype'] == 'list':
                dropbox.lineEdit().setReadOnly(True)
                dropbox.editTextChanged.connect(self.dropbox_changed)
            else:
                dropbox.currentTextChanged.connect(self.dropbox_changed)
            dropbox.blockSignals(False)
            self.addWidget(dropbox, i, entry_col, 1, entry_colspan)
            # dropbox.currentTextChanged.connect(self.dropbox_changed)

        if item['datatype'] == 'path':
            self.vpconf_brose_button = QPushButton()
            self.vpconf_brose_button.blockSignals(True)
            self.vpconf_brose_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.vpconf_brose_button.setMinimumWidth(150)
            self.vpconf_brose_button.setObjectName('path_vpconf')
            if item['value'] == '-':
                self.vpconf_brose_button.setText('Browse...')
            else:
                fname = os.path.basename(item['value'])
                button_text = fname
                self.vpconf_brose_button.setToolTip(item['value'])
                # p_length = len(item['value'])
                # if p_length > 45:
                #     button_text = f"{button_text[:40]}...{button_text[-25:]}"
                self.vpconf_brose_button.setText(button_text)
            self.vpconf_brose_button.blockSignals(False)
            self.vpconf_brose_button.setMaximumHeight(25)
            self.vpconf_brose_button.clicked.connect(self.browse_for_config)
            self.addWidget(self.vpconf_brose_button, i, entry_col, 1, entry_colspan, alignment=Qt.AlignLeft)

        if item['datatype'] == 'int' or item['datatype'] == 'anyfloat':
            self.addWidget(line_edit, i, entry_col, 1, entry_colspan)

        if item['datatype'] == 'button':
            self.addWidget(self.usbdevice_button, i, entry_col, 1, entry_colspan, alignment=Qt.AlignLeft)

        if item['datatype'] == 'configurator':
            self.configurator_button = QPushButton("Configure Gain Overrides")

            try:
                gaindict = json.loads(item['value'])
                self.configurator_button = QPushButton("Edit Gain Overrides")
            except:
                pass

            self.configurator_button.setMinimumWidth(150)
            self.configurator_button.setMaximumHeight(25)
            self.configurator_button.setObjectName(f"config_{item['name']}")
            self.configurator_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.configurator_button.clicked.connect(self.configurator_button_clicked)
            erase_button.clicked.connect(self.erase_configurator_overrides)
            self.addWidget(self.configurator_button, i, entry_col, 1, entry_colspan, alignment=Qt.AlignLeft)


        if item['has_expander'] == 'true' and item['prereq'] != '':
            exp_col += 1
        if not rowdisabled:
            # for p_item in self.prereq_list:
            #     if p_item['prereq'] == item['name'] : # and p_item['count'] > 1:
            p_count = 0
            if item['prereq_count'] != '':
                p_count = int(item['prereq_count'])

            if item['has_expander'].lower() == 'true':
                if item['name'] in self.expanded_items:
                    row_count = p_count
                    if item['hasbump'].lower() != 'true':
                        row_count += 1
                    expand_button.setMaximumHeight(200)
                    # self.addWidget(expand_button, i, exp_col, row_count, 1)
                    self.addWidget(expand_button, i, exp_col)
                else:
                    self.addWidget(expand_button, i, exp_col)

        label.setDisabled(rowdisabled)
        slider.setDisabled(rowdisabled)
        d_slider.setDisabled(rowdisabled)
        df_slider.setDisabled(rowdisabled)
        line_edit.setDisabled(rowdisabled)
        expand_button.setDisabled(rowdisabled)

        self.parent().parent().parent().addSlider(slider)
        self.parent().parent().parent().addSlider(d_slider)
        self.parent().parent().parent().addSlider(df_slider)

        # erase_button = QToolButton()
        icon = QIcon()
        pixmap = HiDpiPixmap(":/image/delete_button.png")
        #pixmap = pixmap.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon.addPixmap(pixmap)

        # Create the erase button

        erase_button.setObjectName(f"eb_{item['name']}")
        erase_button.setMaximumSize(25, 25)
        erase_button.setMinimumSize(25, 25)
        erase_button.setIcon(icon)
        #erase_button.setIconSize(pixmap.rect().size())
        erase_button.setToolTip("")
        erase_button.clicked.connect(lambda _, name=item['name']: self.erase_setting(name))
        self.addWidget(erase_button, i, erase_col)
        sp_retain = erase_button.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        erase_button.setSizePolicy(sp_retain)

        erase_button.setVisible(False)
        if item['replaced'] == 'Model (user)':
            if item['name'] != 'type':  # dont erase type on mainwindow settings
                erase_button.setVisible(True)
                erase_button.setToolTip("Reset to Default")
        self.setRowStretch(i, 0)
        erase_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;  /* Adjust the font size */
                font-family: Arial Black;
                font-weight: bold;
                color: black;
                padding: 0px;
                border: none;  /* Remove any border */
                margin: 0px;   /* Remove any margin */
                background-color: transparent;  /* Transparent background */
            }
            QPushButton:hover {
                background-color: #ddd;  /* Optional: Change background on hover */
            }
            QPushButton:pressed {
                background-color: #bbb;  /* Optional: Change background on press */
            }
        """)

    def show_erase_button(self, setting_name=None):
        if setting_name is None:
            setting_name = self.sender().objectName()

        # This regex pattern matches any prefix followed by an underscore and captures the rest as the settingname
        pattern = r'^[^_]+_(.+)$'
        setting = re.match(pattern, setting_name).group(1)
        # dbprint("red", f"SETTING: {setting}")
        eb = self.mainwindow.findChild(QPushButton, f"eb_{setting}")
        eb.setVisible(True)
        eb.setToolTip("Reset to Default")

    def remove_widget(self, olditem):
        widget = olditem.widget()
        if widget is not None:
            widget.deleteLater()
            self.removeWidget(widget)

    def checkbox_changed(self, name, state):
        self.trigger_form_reload = True
        logging.debug(f"Checkbox {name} changed. New state: {state}")
        value = 'false' if state == 0 else 'true'
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, name)
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def erase_setting(self, name):
        self.trigger_form_reload = True
        logging.debug(f"Erase {name} clicked")
        xmlutils.erase_models_from_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, name)
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def browse_for_config(self):
        self.trigger_form_reload = False
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        calling_button = self.sender()
        starting_dir = os.getcwd()
        if calling_button:
            tooltip_text = calling_button.toolTip()
            print(f"Tooltip text of the calling button: {tooltip_text}")
            if os.path.isfile(tooltip_text):
                # Use the existing file path as the starting point
                starting_dir = os.path.dirname(tooltip_text)

        # Open the file browser dialog
        file_path, _ = QFileDialog.getOpenFileName(self.mainwindow, "Choose File", starting_dir, "vpconf Files (*.vpconf)", options=options)

        if file_path:
            cfg_scope = xmlutils.device
            key = "pid" + cfg_scope.capitalize()
            pid = G.system_settings.get(key, '')

            if validate_vpconf_profile(file_path, pid=pid, dev_type=cfg_scope):
                #lprint(f"Selected File: {file_path}")
                xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, file_path, 'vpconf')

                self.show_erase_button('config_vpconf')
                self.vpconf_brose_button.setText(os.path.basename(file_path))
                if G.settings_mgr.timed_out:
                    self.reload_caller()

    def spin_box_changed(self):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('sb_', '')
        value = str(self.sender().value())
        logging.debug(f"Spin Box {setting_name} changed. New value: {value}")
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, setting_name)
        self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def textbox_changed(self):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('le_', '')
        value = self.sender().text()
        logging.debug(f"Textbox {setting_name} changed. New value: {value}")
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, setting_name)
        self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def dropbox_changed(self):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('db_', '')
        value = self.sender().currentText()
        logging.debug(f"Dropbox {setting_name} changed. New value: {value}")
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, setting_name)
        self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def unit_dropbox_changed(self):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('ud_', '')
        line_edit_name = 'vle_' + self.sender().objectName().replace('ud_', '')
        line_edit = self.mainwindow.findChild(QLineEdit, line_edit_name)
        value = ''
        unit = self.sender().currentText()
        if line_edit is not None:
            value = line_edit.text()
        logging.debug(f"Unit {self.sender().objectName()} changed. New value: {value}{unit}")
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, setting_name, unit)
        self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def line_edit_changed(self):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('vle_', '')
        unit_dropbox_name = 'ud_' + self.sender().objectName().replace('vle_', '')
        unit_dropbox = self.mainwindow.findChild(QComboBox, unit_dropbox_name)
        unit = ''
        if unit_dropbox is not None:
            unit = unit_dropbox.currentText()
        value = self.sender().text()
        logging.debug(f"Text box {self.sender().objectName()} changed. New value: {value}{unit}")
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value, setting_name, unit)
        self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def expander_clicked(self):
        self.trigger_form_reload = True
        logging.debug(f"expander {self.sender().objectName()} clicked.  value: {self.sender().text()}")
        settingname = self.sender().objectName().replace('ex_', '')
        if self.sender().arrowType() == Qt.RightArrow:
            # print ('expanded')

            self.expanded_items.append(settingname)
            self.sender().setArrowType(Qt.DownArrow)

            self.reload_caller()
        else:
            # print ('collapsed')
            new_exp_items = []
            for ex in self.expanded_items:
                if ex != settingname:
                    new_exp_items.append(ex)
            self.expanded_items = new_exp_items
            self.sender().setArrowType(Qt.DownArrow)

            self.reload_caller()

    def usb_button_clicked(self):
        if G.master_instance and G.device_type != G.current_device_config_scope:
            # button is being bound for non master device
            target_device = G.current_device_config_scope
        else:
            target_device = None

        button_name = self.sender().objectName().replace('pb_', '')
        the_button = self.mainwindow.findChild(QPushButton, f'pb_{button_name}')
        the_button.setText("Push a button! ")
        # listen for button loop
        # Start a thread to fetch button press with a timeout
        self.thread = ButtonPressThread(self.device, self.sender(), target_device)
        self.thread.button_pressed.connect(self.update_button)
        self.thread.start()

    def update_button(self, button_name, value):
        self.trigger_form_reload = False
        the_button = self.mainwindow.findChild(QPushButton, f'pb_{button_name}')
        the_button.setText(str(value))
        if str(value) != '0':
            xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, str(value), button_name)
            self.show_erase_button(setting_name=f'pb_{button_name}')
        else:
            the_button.setText("Click to Configure")
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def configurator_button_clicked(self):
        """
        User clicked the configurator gain override settings button.
        If the current settings scope is not the master device, send the command over IPC to have the child instance
        pop its dialog window.
        """
        if G.master_instance and G.device_type != G.current_device_config_scope:
            G.ipc_instance.send_broadcast_message(f'SHOW GAIN OVD:{G.current_device_config_scope}')
        else:
            # dbprint("red", f"Device = {G.device_type}")
            # dbprint("green", f"Scope = {G.current_device_config_scope}")
            G.gain_override_dialog.accepted.connect(self.update_configurator_overrides)
            G.gain_override_dialog.raise_()
            G.gain_override_dialog.activateWindow()
            G.gain_override_dialog.show()

    def erase_configurator_overrides(self):
        if G.master_instance and G.device_type != G.current_device_config_scope:
            G.ipc_instance.send_broadcast_message(f'ERASE GAIN OVD:{G.current_device_config_scope}')
        else:
            G.gain_override_dialog.revert_gains()
            G.gain_override_dialog.reset_to_vpconf()

    def update_configurator_overrides(self, gain_dict):
        self.trigger_form_reload = False
        """
        Called when signal received that user saved the configurator gain settings
        convert dictionary to text string and write to config.
        """
        gain_dict_json = json.dumps(gain_dict)
        xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, gain_dict_json, "configurator_gains")
        self.show_erase_button("config_configurator_gains")
        self.configurator_button.setText("Edit Gain Overrides")

    def slider_changed(self, write=True):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('sld_', '')
        value_label_name = 'vl_' + self.sender().objectName().replace('sld_', '')
        sliderfactor_name = 'sf_' + self.sender().objectName().replace('sld_', '')
        value_label = self.mainwindow.findChild(QLabel, value_label_name)
        sliderfactor_label = self.mainwindow.findChild(QLabel, sliderfactor_name)
        value = 0
        factor = 1.0
        if value_label is not None:
            value_label.setText(str(self.sender().value()) + '%')
            value = int(self.sender().value())
        if sliderfactor_label is not None:
            factor = float(sliderfactor_label.text())
        value_to_save = str(round(value * factor / 100, 4))
        if self.show_slider_debug:
            logging.debug(f"Slider {self.sender().objectName()} changed. New value: {value} factor: {factor}  saving: {value_to_save}")
        if write:
            xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value_to_save, setting_name)
            self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def cfg_slider_changed(self, write=True):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('sld_', '')
        value_label_name = 'vl_' + self.sender().objectName().replace('sld_', '')

        value_label = self.mainwindow.findChild(QLabel, value_label_name)
        value = 0
        factor = 1.0
        if value_label is not None:
            value_label.setText(str(self.sender().value()) + '%')
            value = int(self.sender().value())

        value_to_save = str(round(value / 100, 4))
        if self.show_slider_debug:
            logging.debug(f"Slider {self.sender().objectName()} cfg changed. New value: {value}  saving: {value_to_save}")
        if write:
            xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value_to_save, setting_name)
            self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def d_slider_changed(self, write=True):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('dsld_', '')
        value_label_name = 'vl_' + self.sender().objectName().replace('dsld_', '')
        sliderfactor_name = 'sf_' + self.sender().objectName().replace('dsld_', '')
        unit_dropbox_name = 'ud_' + self.sender().objectName().replace('dsld_', '')
        unit_dropbox = self.mainwindow.findChild(QComboBox, unit_dropbox_name)
        unit = ''
        if unit_dropbox is not None:
            unit = unit_dropbox.currentText()
        value_label = self.mainwindow.findChild(QLabel, value_label_name)
        sliderfactor_label = self.mainwindow.findChild(QLabel, sliderfactor_name)
        factor = 1
        if sliderfactor_label is not None:
            factor = float(sliderfactor_label.text())
        if value_label is not None:
            value = self.sender().value()
            value_to_save = str(round(value * factor))
            value_label.setText(value_to_save)
        if self.show_slider_debug:
            logging.debug(f"d_Slider {self.sender().objectName()} changed. New value: {value} factor: {factor}  saving: {value_to_save}{unit}")
        if write:
            xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value_to_save, setting_name, unit)
            self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    def df_slider_changed(self, write=True):
        self.trigger_form_reload = False
        setting_name = self.sender().objectName().replace('dfsld_', '')
        value_label_name = 'vl_' + self.sender().objectName().replace('dfsld_', '')
        sliderfactor_name = 'sf_' + self.sender().objectName().replace('dfsld_', '')
        unit_dropbox_name = 'ud_' + self.sender().objectName().replace('dfsld_', '')
        unit_dropbox = self.mainwindow.findChild(QComboBox, unit_dropbox_name)
        unit = ''
        if unit_dropbox is not None:
            unit = unit_dropbox.currentText()
        value_label = self.mainwindow.findChild(QLabel, value_label_name)
        sliderfactor_label = self.mainwindow.findChild(QLabel, sliderfactor_name)
        factor = 1
        if sliderfactor_label is not None:
            factor = float(sliderfactor_label.text())
        if value_label is not None:
            value = self.sender().value()
            value_to_save = str(round(value * factor, 2))
            value_label.setText(value_to_save)
        if self.show_slider_debug:
            logging.debug(f"df_Slider {self.sender().objectName()} changed. New value: {value} factor: {factor}  saving: {value_to_save}{unit}")
        if write:
            xmlutils.write_models_to_xml(G.settings_mgr.current_sim, G.settings_mgr.current_pattern, value_to_save, setting_name, unit)
            self.show_erase_button()
        if G.settings_mgr.timed_out:
            self.reload_caller()

    # # prevent slider from sending values as you drag
    # def sldDisconnect(self):
    #     self.sender().valueChanged.disconnect()
    #
    # # reconnect slider after you let go
    # def sldReconnect(self):
    #     self.sender().valueChanged.connect(self.slider_changed)
    #     self.sender().valueChanged.emit(self.sender().value())
    #
    # def cfg_sldReconnect(self):
    #     self.sender().valueChanged.connect(self.cfg_slider_changed)
    #     self.sender().valueChanged.emit(self.sender().value())
    #
    # def d_sldReconnect(self):
    #     self.sender().valueChanged.connect(self.d_slider_changed)
    #     self.sender().valueChanged.emit(self.sender().value())
    #
    # def df_sldReconnect(self):
    #     self.sender().valueChanged.connect(self.df_slider_changed)
    #     self.sender().valueChanged.emit(self.sender().value())
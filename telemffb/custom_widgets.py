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


from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QHBoxLayout, QSlider, QCheckBox, QFrame, \
    QComboBox, QMessageBox, QMenu, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QRect, QPointF, QPropertyAnimation, QRectF, QPoint, \
    QSequentialAnimationGroup, QEasingCurve, pyqtSlot, pyqtProperty, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QCursor, QGuiApplication, QBrush, QPen, QPaintEvent, QRadialGradient, \
    QLinearGradient, QFont
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider

import numpy as np
from scipy.interpolate import make_interp_spline, interp1d
from scipy.interpolate import Akima1DInterpolator

import telemffb.globals as G
from telemffb.utils import HiDpiPixmap

vpf_purple = "#ab37c8"   # rgb(171, 55, 200)
t_purple = QColor(f"#44{vpf_purple[-6:]}")


class NoKeyScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()

        self.sliders = []
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def addSlider(self, slider):
        self.sliders.append(slider)
    #
    # def keyPressEvent(self, event):
    #     # Forward keypress events to all sliders
    #     for slider in self.sliders:
    #         try:
    #             slider.keyPressEvent(event)
    #         except:
    #             pass
    #
    # def keyReleaseEvent(self, event):
    #     # Forward keypress events to all sliders
    #     for slider in self.sliders:
    #         try:
    #             slider.keyReleaseEvent(event)
    #         except:
    #             pass


class SliderWithLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.updateLabel)

        self.label = QLabel(str(self.slider.value()))

        layout = QVBoxLayout(self)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

    def updateLabel(self, value):
        self.label.setText(str(value))

class DelayTimerSlider(QSlider):
    delayedValueChanged = pyqtSignal(int)
    def __init__(self, *args, **kwargs):
        super(DelayTimerSlider, self).__init__(*args, **kwargs)
        self._delay = 150  # Delay in milliseconds
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emitDelayedValueChanged)
        self.valueChanged.connect(self._startTimer)

    def _startTimer(self):
        self._timer.start(self._delay)

    def _emitDelayedValueChanged(self):
        self.delayedValueChanged.emit(self.value())

class NoWheelSlider(QSlider):
    delayedValueChanged = pyqtSignal(int)
    def __init__(self, *args, **kwargs):

        super(NoWheelSlider, self).__init__(*args, **kwargs)
        # Default colors
        self.groove_color = "#bbb"
        self.handle_color = vpf_purple
        self.handle_height = 20
        self.handle_width = 16
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # Apply styles
        self.update_styles()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.is_mouse_over = False
        self._delay = 200  # Delay in milliseconds
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emitDelayedValueChanged)
        self.valueChanged.connect(self._startTimer)

        self.setMinimumHeight(int(self.handle_height ) + 10)
    def _startTimer(self):
        self._timer.start(self._delay)

    def _emitDelayedValueChanged(self):
        self.delayedValueChanged.emit(self.value())

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier:
            # Adjust the value by increments of 1
            current_value = self.value()
            if event.angleDelta().y() > 0:
                new_value = current_value + 1
            elif event.angleDelta().y() < 0:
                new_value = current_value - 1

            # Ensure the new value is within the valid range
            new_value = max(self.minimum(), min(self.maximum(), new_value))

            self.setValue(new_value)
            event.accept()
        else:
            event.ignore()

    def update_styles(self):
        # Generate CSS based on color and size properties
        css = f"""
            QSlider::groove:horizontal {{
                border: 1px solid #565a5e;
                height: 8px;  /* Adjusted groove height */
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e6e6e6, stop: 1 #bfbfbf
                );
                margin: 0;
                border-radius: 3px;  /* Adjusted border radius */
            }}
            QSlider::handle:horizontal {{
                background: qradialgradient(
                    cx: 0.3, cy: 0.5, fx: 0.3, fy: 0.35, radius: 0.8,
                    stop: 0.0 #ffffff,
                    stop: 0.3 {self.handle_color},
                    stop: 1.0 {QColor(self.handle_color).darker().name()}
                );
                border: 1px solid #565a5e;
                width: {int(self.handle_width)}px;  /* Adjusted handle width */
                height: {int(self.handle_height)}px;  /* Adjusted handle height */
                border-radius: {int(self.handle_height / 4 )}px;  /* Adjusted border radius */
                margin-top: -{int(self.handle_height / 4 )}px;  /* Negative margin to overlap with groove */
                margin-bottom: -{int(self.handle_height / 4 )}px;  /* Negative margin to overlap with groove */
                margin-left: -1px;  /* Adjusted left margin */
                margin-right: -1px;  /* Adjusted right margin */
            }}
        """
        self.setStyleSheet(css)

    def increase_single_step(self):
        self.setValue(self.value() + self.singleStep())

    def decrease_single_step(self):
        self.setValue(self.value() - self.singleStep())

    def setGrooveColor(self, color):
        self.groove_color = color
        self.update_styles()

    def setHandleColor(self, color):
        self.handle_color = color
        self.update_styles()

    def setHandleHeight(self, height):
        self.handle_height = height
        self.update_styles()

    def enterEvent(self, event):
        self.setFocus()
        super().enterEvent(event)  # Call the default handler to ensure normal behavior

    def leaveEvent(self, event):
        self.clearFocus()
        super().leaveEvent(event)  # Call the default handler to ensure normal behavior


class NoWheelNumberSlider(NoWheelSlider):
    def __init__(self, *args, **kwargs):
        super(NoWheelNumberSlider, self).__init__(*args, **kwargs)
        self.handle_width = 32  # Different handle width for NoWheelNumberSlider
        self.value_text = ""  # Add an attribute to store the text to be shown in the handle
        self.update_styles()

    def setHandleColor(self, color, text=""):
        self.handle_color = color
        self.value_text = text
        self.update_styles()
        self.update()  # Ensure the slider is repainted to show the new text

    def paintEvent(self, event):
        super(NoWheelNumberSlider, self).paintEvent(event)
        painter = QPainter(self)

        font = painter.font()
        font.setPointSize(font.pointSize() - 1)  # Decrease the font size by 1 point
        font.setBold(True)
        painter.setFont(font)

        # Draw the handle with the gradient color
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        handle_rect = self.style().subControlRect(self.style().CC_Slider, option,
                                                  self.style().SC_SliderHandle, self)

        # Adjust the handle rect width to match the custom handle width
        handle_rect.setWidth(self.handle_width)

        # Calculate the correct position for the handle based on the slider value
        if self.orientation() == Qt.Horizontal:
            handle_x = self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self.value(),
                                                            self.width() - self.handle_width)
            handle_rect.moveLeft(handle_x)
        else:
            handle_y = self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self.value(),
                                                            self.height() - self.handle_height)
            handle_rect.moveTop(handle_y)

        # Ensure the painter uses anti-aliasing for smoother text rendering
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the bounding rectangle for the text
        text_rect = painter.boundingRect(handle_rect, Qt.AlignCenter, self.value_text)

        # Draw the text inside the handle
        painter.setPen(Qt.white)
        painter.drawText(text_rect, Qt.AlignCenter, self.value_text)

        painter.end()

    def initStyleOption(self, option):
        option.initFrom(self)
        option.subControls = QStyle.SC_SliderHandle | QStyle.SC_SliderGroove
        option.orientation = self.orientation()
        option.minimum = self.minimum()
        option.maximum = self.maximum()
        option.sliderPosition = self.sliderPosition()
        option.sliderValue = self.value()
        option.singleStep = self.singleStep()
        option.pageStep = self.pageStep()
        option.tickPosition = self.tickPosition()
        option.tickInterval = self.tickInterval()

class ClickLogo(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):

        super(ClickLogo, self).__init__(parent)

        # Initial clickable state
        self._clickable = False

    def setClickable(self, clickable):
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self._clickable:
            self.clicked.emit()

    def enterEvent(self, event):
        if self._clickable:
            self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)


class InfoLabel(QWidget):
    def __init__(self, text=None, tooltip=None, parent=None):
        super(InfoLabel, self).__init__(parent)

        # Text label
        self.text_label = QLabel(self)
        self.text_label.setText(text)
        self.text_label.setMinimumWidth(self.text_label.sizeHint().height())

        # Information icon
        self.icon_label = QLabel(self)
        # icon_img = os.path.join(script_dir, "image/information.png")
        icon_img = ":/image/information.png"
        self.pixmap = HiDpiPixmap(icon_img)
        self.icon_label.setPixmap(self.pixmap._scaled(12, 12, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Adjust the height as needed
        self.icon_label.setVisible(False)

        # Layout to align the text label and icon
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.text_label, alignment=Qt.AlignLeft)
        self.layout.addSpacing(0)
        self.layout.addWidget(self.icon_label, alignment=Qt.AlignLeft)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()

        # Set initial size for text_label based on the size of the icon
        # self.text_label.setFixedHeight(self.icon_label.height())

        if text:
            self.setText(text)
        if tooltip:
            self.setToolTip(tooltip)

    def setText(self, text):
        self.text_label.setText(text)
        # Adjust the size of text_label based on the new text
        # self.text_label.setFixedHeight(self.icon_label.height())

    def setToolTip(self, tooltip):
        if tooltip:
            self.icon_label.setToolTip(tooltip)
            self.icon_label.setVisible(True)
        else:
            self.icon_label.setToolTip('')
            self.icon_label.setVisible(False)

    def setTextStyleSheet(self, style_sheet):
        self.text_label.setStyleSheet(style_sheet)

    def show_icon(self):
        # Manually scale the pixmap to a reasonable size
        scaled_pixmap = self.pixmap.scaledToHeight(self.text_label.sizeHint().height())  # Adjust the height as needed
        self.icon_label.setPixmap(scaled_pixmap)


class StatusLabel(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None, text='', color: QColor = Qt.yellow, size=10):
        super(StatusLabel, self).__init__(parent)

        self.label = QLabel(text)
        self.label.setStyleSheet("QLabel { padding-right: 5px; }")

        self.dot_color = color  # Default color
        self.dot_size = size
        self.setCursor(Qt.PointingHandCursor)
        self._clickable = True
        self.setToolTip('Click to manage this device')
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)

    def enterEvent(self, event):
        # Set the label to be blue and underlined when the mouse enters
        self.label.setStyleSheet("QLabel { padding-right: 5px; color: blue; text-decoration: underline; }")

    def leaveEvent(self, event):
        # Set the label back to its original style when the mouse leaves
        self.label.setStyleSheet("QLabel { padding-right: 5px; color: black; text-decoration: none; }")

    def mousePressEvent(self, event):
        if self._clickable:
            dev = self.label.text().lower()
            self.clicked.emit(dev)

    def hide(self):
        self.label.hide()
        super().hide()

    def show(self):
        self.label.show()
        super().show()

    def set_text(self, text):
        self.label.setText(text)

    def set_dot_color(self, color: QColor):
        self.dot_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate adjusted positioning for the dot
        dot_x = self.label.geometry().right() - 1  # 5 is an arbitrary offset for better alignment
        dot_y = self.label.geometry().center().y() - self.dot_size // 2 + 1

        # Define thicknesses
        outer_black_thickness = 1
        ring_thickness = 2
        total_thickness = outer_black_thickness + ring_thickness

        # Adjust the size to include the rings
        total_size = self.dot_size + 2 * total_thickness

        # Draw the outermost black ring
        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(dot_x - total_thickness, dot_y - total_thickness, total_size, total_size)

        # Draw the metallic grey ring
        ring_gradient = QRadialGradient(dot_x - total_thickness + total_size / 3,
                                        dot_y - total_thickness + total_size / 3, total_size / 2)
        ring_color = QColor(192, 192, 192)  # Metallic grey
        ring_gradient.setColorAt(0, ring_color.lighter(180))
        ring_gradient.setColorAt(0.35, ring_color)
        ring_gradient.setColorAt(1, ring_color.darker(200))

        painter.setBrush(ring_gradient)
        painter.drawEllipse(dot_x - total_thickness + outer_black_thickness,
                            dot_y - total_thickness + outer_black_thickness, total_size - 2 * outer_black_thickness,
                            total_size - 2 * outer_black_thickness)

        # Create a gradient for the dot with a 3D effect
        gradient = QRadialGradient(dot_x + self.dot_size / 3, dot_y + self.dot_size / 3, self.dot_size / 2)
        gradient.setColorAt(0, QColor(self.dot_color).lighter(180))  # Increase lightness for stronger highlight
        gradient.setColorAt(0.35, QColor(self.dot_color))  # Base color in the middle
        gradient.setColorAt(1, QColor(self.dot_color).darker(200))  # Increase darkness for stronger shadow

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(dot_x, dot_y, self.dot_size, self.dot_size)

        painter.end()

class SimStatusLabel(QWidget):
    def __init__(self, name : str):
        super().__init__()
        self.icon_size = QSize(24, 24)

        self._paused_state = False
        self._error_state = False
        self._active_state = False
        self._enabled_state = False

        self.error_message = None

        self.lbl = QLabel(name)
        # font = QFont("xxxxxx", weight=QFont.Bold)
        #
        # # Set the font to the label
        # self.lbl.setFont(font)

        self.lbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.pix = QLabel()
        self.pix.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        enable_color = QColor(255, 235, 0)
        disable_color = QColor(128, 128, 128) # grey
        active_color = QColor(23, 196, 17)
        paused_color = QColor(0, 0, 255)
        error_color = QColor(255, 0, 0)

        self.enabled_pixmap = self.create_status_icon(enable_color, self.icon_size, icon_type="colored")
        self.disabled_pixmap = self.create_status_icon(disable_color, self.icon_size, icon_type="x")
        self.active_pixmap = self.create_status_icon(active_color, self.icon_size, icon_type="colored")
        self.paused_pixmap = self.create_status_icon(paused_color, self.icon_size, icon_type="paused")
        self.error_pixmap = self.create_status_icon(error_color, self.icon_size, icon_type="exclamation")

        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(v_layout)
        v_layout.addWidget(self.lbl)
        v_layout.addWidget(self.pix)

        self.update()

    @property
    def paused(self):
        return self._paused_state

    @paused.setter
    def paused(self, value):
        if self._paused_state != value:
            self._paused_state = value
            self.update()

    @property
    def error(self):
        return self._error_state

    @error.setter
    def error(self, value):
        if self._error_state != value:
            self._error_state = value
            self.update()

    @property
    def active(self):
        return self._active_state

    @active.setter
    def active(self, value):
        if self._active_state != value:
            self.error_message = None
            self._active_state = value
            self.update()

    @property
    def enabled(self):
        return self._enabled_state

    @enabled.setter
    def enabled(self, value):
        if self._enabled_state != value:
            self._enabled_state = value
            self.update()

    def update(self):
        if self._error_state:
            self.pix.setPixmap(self.error_pixmap)
            msg = self.error_message if self.error_message is not None else 'check log'
            self.setToolTip(f"Error condition: {msg}")
        elif self._paused_state:
            self.pix.setPixmap(self.paused_pixmap)
            self.setToolTip("Telemetry stopped or sim is paused")
        elif self._active_state:
            self.pix.setPixmap(self.active_pixmap)
            self.setToolTip("Sim is running, receiving telemetry")
        elif self._enabled_state:
            self.pix.setPixmap(self.enabled_pixmap)
            self.setToolTip("Sim is enabled, not receiving telemetry")
        else:
            self.pix.setPixmap(self.disabled_pixmap)
            self.setToolTip("Sim is disabled")

    def create_status_icon(self, color, size: QSize, icon_type="colored"):
        pixmap = HiDpiPixmap(size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, 1)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, 1)

        # Define thicknesses
        outer_black_thickness = 1
        ring_thickness = 2
        inner_black_thickness = 1

        total_thickness = outer_black_thickness + ring_thickness + inner_black_thickness

        # Draw the outermost ring with gradient
        outer_ring_gradient = QRadialGradient(size.width() / 3, size.height() / 3, size.width() / 2)
        outer_ring_color = QColor(30, 30, 30)  # Dark grey for outer ring
        outer_ring_gradient.setColorAt(0, outer_ring_color.lighter(180))
        outer_ring_gradient.setColorAt(0.35, outer_ring_color)
        outer_ring_gradient.setColorAt(1, outer_ring_color.darker(200))

        painter.setBrush(outer_ring_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size.width(), size.height())

        # Draw the metallic grey ring
        ring_gradient = QRadialGradient(size.width() / 3, size.height() / 3, size.width() / 2)
        ring_color = QColor(192, 192, 192)  # Metallic grey
        ring_gradient.setColorAt(0, ring_color.lighter(180))
        ring_gradient.setColorAt(0.35, ring_color)
        ring_gradient.setColorAt(1, ring_color.darker(200))

        painter.setBrush(ring_gradient)
        painter.drawEllipse(outer_black_thickness, outer_black_thickness, size.width() - 2 * outer_black_thickness,
                            size.height() - 2 * outer_black_thickness)

        # Draw the inner ring with gradient
        inner_ring_gradient = QRadialGradient(size.width() / 3, size.height() / 3, size.width() / 2)
        inner_ring_color = QColor(100, 100, 100)  # Grey for inner ring
        inner_ring_gradient.setColorAt(0, inner_ring_color.lighter(180))
        inner_ring_gradient.setColorAt(0.35, inner_ring_color)
        inner_ring_gradient.setColorAt(1, inner_ring_color.darker(200))

        painter.setBrush(inner_ring_gradient)
        painter.drawEllipse(outer_black_thickness + ring_thickness, outer_black_thickness + ring_thickness,
                            size.width() - 2 * (outer_black_thickness + ring_thickness),
                            size.height() - 2 * (outer_black_thickness + ring_thickness))

        # Draw the colored dot
        dot_gradient = QRadialGradient(size.width() / 3, size.height() / 3, size.width() / 2)
        dot_gradient.setColorAt(0, color)  # Increase lightness for stronger highlight
        dot_gradient.setColorAt(0.35, color)  # Base color in the middle
        dot_gradient.setColorAt(1, color)  # Increase darkness for stronger shadow

        painter.setBrush(dot_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(total_thickness, total_thickness, size.width() - 2 * total_thickness,
                            size.height() - 2 * total_thickness)

        if icon_type == "paused":
            # Draw two vertical lines for the pause icon
            line_length = int(size.height() * 0.4)
            line_width = int(size.width() * 0.12)
            spacing = int(size.width() * 0.1)
            line1_x = int((size.width() / 2) - spacing)
            line2_x = int((size.width() / 2) + spacing)
            line_y = int((size.height() - line_length) / 2)

            # Draw the white pause lines
            painter.setPen(QPen(Qt.white, line_width))
            painter.drawLine(line1_x, line_y, line1_x, line_y + line_length)
            painter.drawLine(line2_x, line_y, line2_x, line_y + line_length)

        elif icon_type == "x":
            # Draw two diagonal lines for the 'X' icon with shadow
            line_length = int(size.width() * 0.6)
            line_width = int(size.width() * 0.12)
            offset = int((size.width() - line_length) / 2)

            line1_start = QPointF(total_thickness + offset, total_thickness + offset)
            line1_end = QPointF(size.width() - total_thickness - offset, size.height() - total_thickness - offset)
            line2_start = QPointF(size.width() - total_thickness - offset, total_thickness + offset)
            line2_end = QPointF(total_thickness + offset, size.height() - total_thickness - offset)

            # Draw the white 'X' lines
            painter.setPen(QPen(Qt.white, line_width))
            painter.drawLine(line1_start, line1_end)
            painter.drawLine(line2_start, line2_end)

        elif icon_type == "exclamation":

            # Draw an exclamation mark for the exclamation icon
            line_length = int(size.height() * 0.4)  # Adjusted to ensure the dot is distinct and separate
            line_width = int(size.width() * 0.15)
            dot_radius = int(size.width() * 0.08)  # Adjusted for a smaller dot
            line_x = int(size.width() / 2)
            line_y1 = int((size.height() - line_length - dot_radius * 2) / 2)
            line_y2 = line_y1 + line_length

            # Draw the white exclamation mark
            painter.setPen(QPen(Qt.white, line_width))
            painter.drawLine(line_x, line_y1, line_x, line_y2)
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(QPointF(line_x, line_y2 + dot_radius + 4), dot_radius, dot_radius)  # Move the dot down

        painter.end()

        return pixmap

class Toggle(QCheckBox):
    """Borrowed from qtwidgets library: https://github.com/pythonguis/python-qtwidgets
    Modified default behavior to support simple checkbox widget replacement in QT designer"""
    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self,
                 parent=None,
                 bar_color=QColor("#44ab37c8"),
                 checked_color="#ab37c8",
                 handle_color=Qt.white,
                 disabled_color=Qt.gray):
        super().__init__(parent)

        # Save our properties on the object via self, so we can access them later
        # in the paintEvent.
        self._bar_color = bar_color
        self._checked_color = checked_color
        self._handle_color = handle_color
        self._disabled_color = QColor(disabled_color)

        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())

        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget.
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0
        self.setMaximumSize(QSize(45, 30))
        self.setMinimumSize(QSize(45, 30))

        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self):
        return QSize(58, 45)

    def hitButton(self, pos: QPointF):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e: QPaintEvent):
        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handleRadius, 0.40 * contRect.height()
        )
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width() - 2 * handleRadius
        xPos = contRect.x() + handleRadius + trailLength * self._handle_position

        # Draw the bar with a subtle 3D sunken effect
        barGradient = QLinearGradient(0, 0, 0, barRect.height())
        barGradient.setStart(barRect.topLeft())
        barGradient.setFinalStop(barRect.bottomLeft())

        if not self.isEnabled():
            barGradient.setColorAt(0.0, self._disabled_color.lighter(150))
            barGradient.setColorAt(0.5, self._disabled_color)
            barGradient.setColorAt(1.0, self._disabled_color.darker(150))
        else:
            barGradient.setColorAt(0.0, self._bar_color.lighter(150))
            barGradient.setColorAt(0.5, self._bar_color)
            barGradient.setColorAt(1.0, self._bar_color.darker(150))

            if self.isChecked():
                barGradient.setColorAt(0.0, QColor(self._checked_color).lighter(150))
                barGradient.setColorAt(0.5, QColor(self._checked_color))
                barGradient.setColorAt(1.0, QColor(self._checked_color).darker(150))

        p.setBrush(QBrush(barGradient))
        p.drawRoundedRect(barRect, rounding, rounding)

        # Draw the border around the bar
        p.setPen(QPen(QColor("#565a5e"), 1))
        p.drawRoundedRect(barRect, rounding, rounding)

        if self.isChecked() and self.isEnabled():
            handle_color = self._handle_checked_brush.color()
        else:
            handle_color = self._handle_brush.color()

        # Draw the handle with a gradient for 3D effect
        handleGradient = QRadialGradient(QPointF(xPos - handleRadius / 3, barRect.center().y() - handleRadius / 3),
                                         handleRadius)
        handleGradient.setColorAt(0.0, QColor(255, 255, 255, 180))
        handleGradient.setColorAt(0.6, handle_color)
        handleGradient.setColorAt(1.0, handle_color.darker())

        p.setBrush(handleGradient)
        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @pyqtSlot(int)
    def handle_state_change(self, value):
        self._handle_position = 1 if value else 0

    @pyqtProperty(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

class LabeledToggle(QWidget):
    """Combo widget that creates a single widget with label and connectable slots using the Toggle widget"""
    stateChanged = pyqtSignal(int)  # Expose the stateChanged signal
    clicked = pyqtSignal(bool)      # Expose the clicked signal

    def __init__(self, parent=None, label=""):
        super().__init__(parent)

        self.toggle = Toggle(self)
        self.label = QLabel(label, self)
        self.label.setAlignment(Qt.AlignVCenter)  # Ensure the label is vertically centered

        layout = QHBoxLayout(self)
        layout.addWidget(self.toggle)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        self.setLayout(layout)

        self.toggle.stateChanged.connect(self.stateChanged)  # Forward the stateChanged signal
        self.toggle.clicked.connect(self.clicked)  # Forward the clicked signal

    def isChecked(self):
        return self.toggle.isChecked()

    def setChecked(self, checked):
        self.toggle.setChecked(checked)

    def setText(self, text):
        self.label.setText(text)

    def connect(self, *args, **kwargs):
        return self.stateChanged.connect(*args, **kwargs)

    def checkState(self):
        return self.toggle.checkState()

    def setCheckState(self, state):
        self.toggle.setCheckState(state)

    def click(self):
        self.toggle.click()

class AnimatedToggle(QCheckBox):
    """Borrowed from qtwidgets library: https://github.com/pythonguis/python-qtwidgets"""
    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self,
        parent=None,
        bar_color=Qt.gray,
        checked_color="#ab37c8",
        handle_color=Qt.white,
        pulse_unchecked_color="#44999999",
        pulse_checked_color="#44#ab37c8"
        ):
        super().__init__(parent)

        # Save our properties on the object via self, so we can access them later
        # in the paintEvent.
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())

        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        self._pulse_unchecked_animation = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_animation = QBrush(QColor(pulse_checked_color))

        # Setup the rest of the widget.
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0

        self._pulse_radius = 0

        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)  # time in ms

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
        self.pulse_anim.setDuration(350)  # time in ms
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.pulse_anim)

        self.stateChanged.connect(self.setup_animation)

    def sizeHint(self):
        return QSize(58, 45)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @pyqtSlot(int)
    def setup_animation(self, value):
        self.animations_group.stop()
        if value:
            self.animation.setEndValue(1)
        else:
            self.animation.setEndValue(0)
        self.animations_group.start()

    def paintEvent(self, e: QPaintEvent):

        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handleRadius, 0.40 * contRect.height()
        )
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width() - 2 * handleRadius

        xPos = contRect.x() + handleRadius + trailLength * self._handle_position

        if self.pulse_anim.state() == QPropertyAnimation.Running:
            p.setBrush(
                self._pulse_checked_animation if
                self.isChecked() else self._pulse_unchecked_animation)
            p.drawEllipse(QPointF(xPos, barRect.center().y()),
                          self._pulse_radius, self._pulse_radius)

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)

        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @pyqtProperty(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    @pyqtProperty(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()

class InstanceStatusRow(QWidget):
    changeConfigScope = QtCore.pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()

        self.instance_status_row = QHBoxLayout()
        self.master_status_icon = StatusLabel(None, f'This Instance({ G.device_type.capitalize() }):', Qt.green, 8)
        self.joystick_status_icon = StatusLabel(None, 'Joystick:', Qt.yellow, 8)
        self.pedals_status_icon = StatusLabel(None, 'Pedals:', Qt.yellow, 8)
        self.collective_status_icon = StatusLabel(None, 'Collective:', Qt.yellow, 8)

        self.status_icons = {
            "joystick" : self.joystick_status_icon,
            "pedals" : self.pedals_status_icon,
            "collective" : self.collective_status_icon
        }

        self.master_status_icon.clicked.connect(self.change_config_scope)
        self.joystick_status_icon.clicked.connect(self.change_config_scope)
        self.pedals_status_icon.clicked.connect(self.change_config_scope)
        self.collective_status_icon.clicked.connect(self.change_config_scope)

        self.instance_status_row.addWidget(self.master_status_icon)
        self.instance_status_row.addWidget(self.joystick_status_icon)
        self.instance_status_row.addWidget(self.pedals_status_icon)
        self.instance_status_row.addWidget(self.collective_status_icon)
        self.joystick_status_icon.hide()
        self.pedals_status_icon.hide()
        self.collective_status_icon.hide()

        self.instance_status_row.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.instance_status_row.setSpacing(10)

        self.setLayout(self.instance_status_row)

    def change_config_scope(self, val):
        self.changeConfigScope.emit(val)

    def set_status(self, device, status):
        status_icon = self.status_icons[device]
        if status == 'ACTIVE':
            status_icon.set_dot_color(Qt.green)
        elif status == 'TIMEOUT':
            status_icon.set_dot_color(Qt.red)
        else:
            status_icon.set_dot_color(Qt.yellow)


class SpringCurveWidget(QWidget):
    UNIT_CONVERSIONS = {
        "kt": 1.94384,
        "mph": 2.23694,
        "kph": 3.6,
        "m/s": 1.0,
    }

    def __init__(self, parent=None, unit='kt'):
        super().__init__(parent)
        # Default: 0% at 0 knots and 100% at 500 knots
        self.points = [QPointF(0, 0), QPointF(500, 100)]
        self.dragging_point = None
        self.right_clicked_point = None
        self.x_scale = 500  # Default range in base unit
        self.point_radius = 3
        self.margin = 50

        self.margin_top = 20  # Reduced space at the top
        self.margin_bottom = 30  # Reduced space at the bottom
        self.margin_left = 50  # Retain enough space for Y-axis labels
        self.margin_right = 20  # Minimal margin on the right

        self.setMinimumSize(400, 300)
        self.setWindowTitle("Spring Force Curve Editor")

        # Units setup
        self.current_unit = unit
        self.base_unit = "m/s"

        # # Smooth curve toggle
        # self.smooth_curve_enabled = False
        # self.smooth_toggle = LabeledToggle(self, "Smooth Curve")
        # self.smooth_toggle.stateChanged.connect(self.toggle_smooth_curve)
        # self.smooth_toggle.move(10, 10)
        # self.smooth_toggle.hide()
        #
        # # Reset Button
        # self.reset_button = QPushButton('Reset Points', self)
        # self.reset_button.move(120, 10)
        # self.reset_button.clicked.connect(lambda: self.clear_points())
        # self.reset_button.hide()

        # message label
        self.msg_label = QLabel(self)
        self.msg_label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.msg_label.move(60, 40)
        self.msg_label.hide()

        self.coordinate_label = QLabel(self)
        self.coordinate_label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.coordinate_label.setAlignment(Qt.AlignCenter)
        self.coordinate_label.setFixedSize(120, 20)  # Adjust size as needed
        self.coordinate_label.hide()  # Initially hidden

        self.test_point = None
        self.last_valid_position = None
        self._enabled = True  # Internal state to track enabled/disabled status

    def setEnabled(self, enabled: bool):
        """Enable or disable the widget."""
        self._enabled = enabled
        super().setEnabled(enabled)
        self.update()  # Trigger a repaint to reflect the new state

    def isEnabled(self):
        """Check if the widget is enabled."""
        return self._enabled

    def apply_disabled_overlay(self, painter):
        """Draw a semi-transparent overlay to indicate the widget is disabled."""
        painter.save()
        painter.setBrush(QColor(200, 200, 200, 128))  # Gray with 50% transparency
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        painter.drawRect(rect)
        painter.restore()

    def change_unit(self, new_unit):
        """Change the unit of the x-axis and update points and labels."""
        if new_unit == self.current_unit:
            return

        # Conversion factors
        current_conversion = self.UNIT_CONVERSIONS[self.current_unit]
        new_conversion = self.UNIT_CONVERSIONS[new_unit]
        conversion_factor = current_conversion / new_conversion

        # Update points and x_scale
        self.points = [
            QPointF(p.x() * conversion_factor, p.y()) for p in self.points
        ]
        self.x_scale *= conversion_factor

        self.current_unit = new_unit
        self.update()

    def toggle_smooth_curve(self, state):
        """Toggles smooth curve drawing, ensuring bounds are checked and the checkbox state is consistent."""
        toggle = self.sender()
        if not state:
            self.smooth_curve_enabled = False
            # self.msg_label.hide()  # Hide any error messages
            self.update()
            return

        if len(self.points) < 4:
            self.msg_label.setText("Error: Need at least 4 points for smooth mode.")
            self.msg_label.show()
            QTimer.singleShot(3000, self.msg_label.hide)
            QTimer.singleShot(300, lambda: toggle.setChecked(False)) # Force the toggle to unchecked

            return

        # Validate the entire curve for smooth mode
        x_values = [p.x() for p in self.points]
        y_values = [p.y() for p in self.points]

        try:
            akima = Akima1DInterpolator(x_values, y_values)
            x_smooth = np.linspace(min(x_values), max(x_values), 500)
            y_smooth = akima(x_smooth)
            # Check bounds
            if np.min(y_smooth) < 0 or np.max(y_smooth) > 100:
                self.msg_label.setText("Error: Smooth curve would exceed bounds.")
                self.msg_label.show()
                QTimer.singleShot(3000, self.msg_label.hide)
                QTimer.singleShot(300, lambda: toggle.setChecked(False))  # Force the toggle to unchecked

                return
        except Exception as e:
            self.msg_label.setText(f"Error: Cannot enable smooth curve ({e}).")
            self.msg_label.show()
            QTimer.singleShot(300, lambda: toggle.setChecked(False))  # Force the toggle to unchecked

            # self.smooth_toggle.setChecked(False)  # Force the toggle to unchecked
            return

        # Enable smooth curve mode
        self.smooth_curve_enabled = True
        self.msg_label.hide()  # Hide any error messages
        self.update()

    def get_force_for_speed(self, speed):
        """Returns the output force (y) for a given input speed (x) based on the current curve."""
        if not self.points:
            raise ValueError("No points defined in the curve.")

        x_values = [p.x() for p in self.points]
        y_values = [p.y() for p in self.points]

        if speed <= x_values[0]:
            # Speed is below the first point
            return 0  # Return 0% force
        elif speed >= x_values[-1]:
            # Speed is above the last point
            return 100  # Return 100% force

        force = 0  # Default value

        if self.smooth_curve_enabled:
            # Use smooth Akima interpolation if enabled
            try:
                if len(x_values) < 3:
                    # Not enough points for Akima, fallback to linear
                    interpolation = interp1d(x_values, y_values, bounds_error=False,
                                             fill_value=(y_values[0], y_values[-1]))
                    force = float(interpolation(speed))
                else:
                    akima = Akima1DInterpolator(x_values, y_values)
                    force = float(akima(speed))
            except Exception as e:
                raise ValueError(f"Error in smooth interpolation: {e}")
        else:
            # Linear interpolation for the current points
            interpolation = interp1d(x_values, y_values, bounds_error=False,
                                     fill_value=(y_values[0], y_values[-1]))
            force = float(interpolation(speed))

        # Clamp the force to the range [0, 100]
        return max(0, min(100, force))

    def update_airspeed_range(self, increment):
        """
        Update the x-axis scale dynamically and scale all points proportionally
        to preserve the shape of the curve.

        Args:
            increment (float): The amount to adjust the x-axis scale by (positive or negative).
        """
        # Calculate the new scale
        new_scale = max(100, self.x_scale + increment)  # Ensure scale doesn't go below 100

        # Calculate the scale factor
        scale_factor = new_scale / self.x_scale

        # Scale all points proportionally
        for point in self.points:
            point.setX(point.x() * scale_factor)

        # Update the x-axis scale and redraw
        self.x_scale = new_scale
        self.update()

    def decrease_x_scale(self):
        """Decrease the x-axis scale by 100 knots, but not below the highest point's x value."""
        max_x_value = max(p.x() for p in self.points)  # Get the highest x value among the points
        self.x_scale = max(max(100, max_x_value), self.x_scale - 100)  # Ensure scale doesn't go below max x value
        self.update()

    def highlight_dragged_point(self, painter):
        """Highlights the point currently being dragged."""
        painter.setPen(QPen(Qt.red, 2))  # Red outline
        painter.setBrush(QColor(255, 255, 0))  # Yellow fill

        # Convert the dragged point to widget space
        dragged_widget_point = self.map_to_widget_space(self.dragging_point)

        # Draw the highlighted point with a larger size
        painter.drawEllipse(
            QRectF(
                dragged_widget_point.x() - self.point_radius * 1.5,
                dragged_widget_point.y() - self.point_radius * 1.5,
                3 * self.point_radius,
                3 * self.point_radius,
            )
        )

    def draw_crosshairs(self, speed_mps, gain):
        if not self.isEnabled():
            return
        """
        Draw crosshairs on the graph at the specified speed and gain.
        Args:
            speed_mps (float): The airspeed in m/s.
            gain (float): The percentage gain.
        """
        # Convert speed to current units
        current_conversion = self.UNIT_CONVERSIONS[self.current_unit]
        speed_converted = speed_mps * current_conversion

        # Calculate crosshair positions in widget space
        rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)
        crosshair_x = rect.left() + (speed_converted / self.x_scale) * rect.width()
        crosshair_y = rect.top() + (1 - gain / 100.0) * rect.height()

        # Set crosshair position and store gain and speed for label
        self.crosshair_position = QPointF(crosshair_x, crosshair_y)
        self.crosshair_gain = gain
        self.crosshair_speed = speed_converted
        self.update()  # Trigger repaint

    def clear_crosshairs(self):
        """
        Clear the crosshairs from the graph.
        """
        self.crosshair_position = None
        self.crosshair_gain = None
        self.crosshair_speed = None
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_axis_labels(painter)
        if self.smooth_curve_enabled:
            self.draw_smooth_curve(painter)
        else:
            self.draw_curve(painter)

        # Highlight the dragged point
        if self.dragging_point is not None:
            self.highlight_dragged_point(painter)

        # Draw the crosshairs if position is set
        if hasattr(self, 'crosshair_position') and self.crosshair_position is not None:
            painter.setPen(QPen(QColor("#ab37c8"), 2, Qt.DashLine))  # Red dashed lines for crosshairs
            rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)

            # Draw vertical and horizontal crosshair lines
            painter.drawLine(int(self.crosshair_position.x()), rect.top(),
                             int(self.crosshair_position.x()), rect.bottom())  # Vertical line
            painter.drawLine(rect.left(), int(self.crosshair_position.y()),
                             rect.right(), int(self.crosshair_position.y()))  # Horizontal line

        # Draw the live speed and gain label at the center top of the graph
        if hasattr(self, 'crosshair_speed') and self.crosshair_speed is not None and hasattr(self, 'crosshair_gain'):
            rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)
            label_text = f"Speed: {self.crosshair_speed:.1f} {self.current_unit}, Gain: {self.crosshair_gain:.1f}%"
            label_x = rect.left() + (rect.width() // 2) - (len(label_text) * 3)  # Center horizontally
            label_y = rect.top() - 5  # Fixed position slightly above the graph area

            painter.setPen(QPen(Qt.black))  # Black text color
            painter.setFont(QFont('Arial', 10, QFont.Bold))  # Bold font for visibility
            painter.drawText(label_x, label_y, label_text)

        # Apply disabled overlay if the widget is disabled
        if not self._enabled:
            self.apply_disabled_overlay(painter)

    def draw_grid(self, painter):
        """Draws the grid lines."""
        rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)  # Adjust to ensure margin
        painter.setPen(QPen(Qt.lightGray, 1, Qt.DotLine))

        # Draw horizontal grid lines (Y-axis 0% to 100%)
        for i in range(0, 11):
            y = int(rect.top() + i * rect.height() / 10)  # Cast to int
            painter.drawLine(rect.left(), y, rect.right(), y)

        # Draw vertical grid lines (X-axis controlled by x_scale)
        for i in range(0, 11):
            x = int(rect.left() + i * rect.width() / 10)  # Cast to int
            painter.drawLine(x, rect.top(), x, rect.bottom())

    def draw_axis_labels(self, painter):
        """Draws the axis labels outside the grid area."""
        rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(Qt.black))

        # Draw Y-axis labels (0% to 100%)
        for i in range(0, 11):
            y = int(rect.top() + i * rect.height() / 10)
            painter.drawText(rect.left() - self.margin_left + 15, y + 5, f"{100 - i * 10}%")

        # Draw X-axis labels (converted to current unit)
        for i in range(0, 11):
            x = int(rect.left() + i * rect.width() / 10)
            speed = self.x_scale * i / 10
            painter.drawText(x - 10, rect.bottom() + self.margin_bottom //2, f"{int(speed)}")

    def draw_curve(self, painter):
        """Draws the spring force curve and points (linear segments)."""
        painter.setPen(QPen(Qt.blue, 2))

        # Convert points into widget space
        widget_points = [self.map_to_widget_space(p) for p in self.points]

        # Draw the lines between points
        for i in range(len(widget_points) - 1):
            painter.drawLine(widget_points[i], widget_points[i + 1])

        # Draw the control points
        for point in widget_points:
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(QRectF(
                point.x() - self.point_radius,
                point.y() - self.point_radius,
                2 * self.point_radius,
                2 * self.point_radius
            ))

    def draw_smooth_curve(self, painter):
        """Draws a smooth curve using Akima interpolation."""
        if len(self.points) < 4:
            # Fallback to linear interpolation or a simple curve
            self.draw_curve(painter)
            return

        painter.setPen(QPen(Qt.blue, 2))

        # Extract x and y values from points
        x_values = [p.x() for p in self.points]
        y_values = [p.y() for p in self.points]

        # Create smooth x and y values using Akima interpolation
        x_smooth = np.linspace(min(x_values), max(x_values), 500)
        try:
            akima = Akima1DInterpolator(x_values, y_values)
            y_smooth = akima(x_smooth)
        except Exception as e:
            QMessageBox.warning(self, "Interpolation Error", f"Error creating Akima interpolation: {e}")
            self.draw_curve(painter)
            return

        # Convert to widget coordinates
        widget_smooth_points = [self.map_to_widget_space(QPointF(x, y)) for x, y in zip(x_smooth, y_smooth)]

        # Draw smooth curve
        for i in range(len(widget_smooth_points) - 1):
            painter.drawLine(widget_smooth_points[i], widget_smooth_points[i + 1])

        # Draw control points
        for point in [self.map_to_widget_space(p) for p in self.points]:
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(QRectF(
                point.x() - self.point_radius,
                point.y() - self.point_radius,
                2 * self.point_radius,
                2 * self.point_radius
            ))

    def map_to_widget_space(self, point):
        """Maps the curve points to the widget's coordinate system."""
        rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)  # Adjusted for margin
        x = rect.left() + (point.x() / self.x_scale) * rect.width()  # Use x_scale for X-axis
        y = rect.top() + (1 - point.y() / 100.0) * rect.height()  # Y-axis is fixed 0-100%
        return QPointF(x, y)

    def map_from_widget_space(self, point):
        """Maps widget space coordinates back to data space."""
        rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)  # Adjusted for margin
        x = (point.x() - rect.left()) / rect.width() * self.x_scale  # Use x_scale for X-axis
        y = (1 - (point.y() - rect.top()) / rect.height()) * 100  # Y-axis is fixed 0-100%
        return QPointF(x, y)

    def check_smooth_curve_bounds(self, new_pos, index):
        """Check if the smooth curve will exceed bounds (0-100%) when a point is moved."""
        # Copy points and apply the new position
        projected_points = self.points.copy()
        projected_points[index] = new_pos
        x_values = [p.x() for p in projected_points]
        y_values = [p.y() for p in projected_points]

        # Ensure points are sorted by X
        sorted_indices = np.argsort(x_values)
        x_values = np.array(x_values)[sorted_indices]
        y_values = np.array(y_values)[sorted_indices]

        try:
            # Use Akima interpolation to evaluate smoothness
            akima = Akima1DInterpolator(x_values, y_values)
            x_smooth = np.linspace(min(x_values), max(x_values), 100)  # Reduce resolution for performance
            y_smooth = akima(x_smooth)
        except Exception as e:
            # If interpolation fails, log the issue and reject the move
            print(f"Akima interpolation error: {e}")
            return False

        # Allow slight tolerance (epsilon) to avoid numerical instability
        epsilon = 0.1  # Tolerance in percentage
        y_min_allowed = 0 - epsilon
        y_max_allowed = 100 + epsilon

        # Check bounds with relaxed tolerance
        if np.min(y_smooth) < y_min_allowed or np.max(y_smooth) > y_max_allowed:
            return False  # Curve exceeds bounds
        return True  # Curve is within acceptable bounds

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            clicked_point = self.map_from_widget_space(event.pos())
            for i, p in enumerate(self.points):
                if (p - clicked_point).manhattanLength() < 10:
                    self.right_clicked_point = p
                    if i not in [0, len(self.points) - 1]:  # Only allow deletion of non-first/last points
                        self.show_context_menu(event.pos())
                    break
            else:
                # No point was clicked, so attempt to add a new point
                self.add_new_point(clicked_point)
        elif event.button() == Qt.LeftButton:
            # Check if user clicked on an existing point to drag it
            clicked_point = self.map_from_widget_space(event.pos())
            for p in self.points:
                if (p - clicked_point).manhattanLength() < 10:
                    self.dragging_point = p
                    self.update()  # Trigger repaint to show highlight
                    break

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.dragging_point is not None:
            # Initialize last_valid_position if not set
            if self.last_valid_position is None:
                self.last_valid_position = QPointF(self.dragging_point)

            index = self.points.index(self.dragging_point)
            new_pos = self.map_from_widget_space(pos)
            valid_move = True

            if index == 0:
                # First point: allow movement along X=0 or Y=0
                if new_pos.x() <= 0:
                    new_pos.setX(0)  # Lock X to 0
                    new_pos.setY(max(0, min(100, new_pos.y())))  # Allow vertical movement (Y-axis)
                elif new_pos.y() <= 0:
                    new_pos.setY(0)  # Lock Y to 0
                    new_pos.setX(max(0, min(self.points[1].x() - 1, new_pos.x())))  # Allow horizontal movement (X-axis)
                else:
                    valid_move = False  # Prevent invalid diagonal movement

                # Validate bounds only in smooth mode
                if self.smooth_curve_enabled:
                    valid_move = valid_move and self.check_smooth_curve_bounds(new_pos, index)
            elif index == len(self.points) - 1:
                # Last point: allow movement along X=max or Y=100
                if new_pos.x() >= self.x_scale:
                    new_pos.setX(self.x_scale)  # Lock X to max
                    new_pos.setY(max(0, min(100, new_pos.y())))  # Allow vertical movement (Y-axis)
                elif new_pos.y() >= 100:
                    new_pos.setY(100)  # Lock Y to 100
                    new_pos.setX(
                        max(self.points[-2].x() + 1,
                            min(self.x_scale, new_pos.x())))  # Allow horizontal movement (X-axis)
                else:
                    valid_move = False  # Prevent invalid diagonal movement

                # Validate bounds only in smooth mode
                if self.smooth_curve_enabled:
                    valid_move = valid_move and self.check_smooth_curve_bounds(new_pos, index)
            else:
                # Intermediate points: ensure proper bounds and prevent overlap
                new_x = max(self.points[index - 1].x() + 1, min(self.points[index + 1].x() - 1, new_pos.x()))
                new_y = max(0, min(100, new_pos.y()))
                proposed_pos = QPointF(new_x, new_y)

                # Check smooth curve bounds if enabled
                if self.smooth_curve_enabled:
                    valid_move = self.check_smooth_curve_bounds(proposed_pos, index)

                if valid_move:
                    new_pos = proposed_pos

            # Update the dragging point or provide feedback if move is invalid
            if valid_move:
                self.dragging_point.setX(new_pos.x())
                self.dragging_point.setY(new_pos.y())
                self.last_valid_position = QPointF(self.dragging_point)  # Save the last valid position
                self.msg_label.hide()  # Hide any error message
            else:
                # For first and last points, silently block invalid moves
                if self.last_valid_position is not None:
                    self.dragging_point.setX(self.last_valid_position.x())
                    self.dragging_point.setY(self.last_valid_position.y())
                else:
                    # If last_valid_position is unexpectedly None, reset to current position
                    self.last_valid_position = QPointF(self.dragging_point)

                # For intermediate points, show an error message
                if index != 0 and index != len(self.points) - 1:
                    if not self.msg_label.isVisible():
                        self.msg_label.setText("Error: Further movement would exceed curve bounds.")
                        self.msg_label.show()
                        QTimer.singleShot(3000, self.msg_label.hide)

            # Update the coordinate label with the current position of the dragging point
                    # Update the coordinate label with the current position of the dragging point
            rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)  # Graph area
            self.coordinate_label.setText(f"{self.dragging_point.x():.2f} {self.current_unit}, %{self.dragging_point.y():.2f}")
            self.coordinate_label.move(
                rect.right() - self.coordinate_label.width() - 1,  # 10px padding from right edge
                rect.bottom() - self.coordinate_label.height() - 1  # 10px padding from bottom edge
            )
            self.coordinate_label.show()

            self.update()  # Trigger repaint

    def mouseReleaseEvent(self, event):
        if self.dragging_point is not None:
            # Restore last valid position if bounds were violated
            if self.last_valid_position and self.smooth_curve_enabled:
                print("RESTORED LAST POINT")
                self.dragging_point.setX(self.last_valid_position.x())
                self.dragging_point.setY(self.last_valid_position.y())
            self.dragging_point = None
            self.last_valid_position = None  # Reset last valid position
            self.coordinate_label.hide()  # Hide the coordinate label
            self.update()

    def show_context_menu(self, pos):
        """Shows a context menu for deleting points."""
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete Point")
        action = context_menu.exec_(self.mapToGlobal(pos))

        if action == delete_action:
            # Prevent deletion if smooth mode is enabled and only 4 points remain
            if self.smooth_curve_enabled and len(self.points) <= 4:
                self.msg_label.setText("Error: Cannot delete more points with smooth mode enabled.")
                self.msg_label.show()
                QTimer.singleShot(3000, self.msg_label.hide)
            else:
                self.points.remove(self.right_clicked_point)
                self.update()

    def add_new_point(self, new_point):
        """Add a new point and maintain order, ensuring the first point stays at y=0."""
        if new_point.x() <= 0:
            return  # Prevent adding a point at x <= 0

        # Temporarily add the new point and check bounds
        projected_points = self.points + [new_point]
        projected_points.sort(key=lambda p: p.x())  # Ensure points are ordered by x (speed)

        if self.smooth_curve_enabled:
            # Check bounds using Akima interpolation
            x_values = [p.x() for p in projected_points]
            y_values = [p.y() for p in projected_points]

            try:
                akima = Akima1DInterpolator(x_values, y_values)
                x_smooth = np.linspace(min(x_values), max(x_values), 500)
                y_smooth = akima(x_smooth)
            except Exception:
                self.msg_label.setText("Error: Invalid smooth curve with this point.")
                self.msg_label.show()
                return

            if np.min(y_smooth) < 0 or np.max(y_smooth) > 100:
                # Reject point if bounds exceeded
                self.msg_label.setText("Error: Adding this point would exceed curve bounds.")
                self.msg_label.show()
                QTimer.singleShot(3000, self.msg_label.hide)
                return
        else:
            # In linear mode, ensure Y is within 0 to 100
            if new_point.y() < 0 or new_point.y() > 100:
                self.msg_label.setText("Error: Adding this point would exceed bounds.")
                self.msg_label.show()
                QTimer.singleShot(3000, self.msg_label.hide)
                return

        # Ensure the first point remains affixed at y=0
        self.points[0].setY(0)
        self.points.append(new_point)
        self.points.sort(key=lambda p: p.x())  # Ensure points are ordered by x (speed)
        self.update()

    def to_dict(self):
        """Serialize the widget's state to a dictionary."""
        return {
            "x_scale": self.x_scale,
            "points": [{"x": p.x(), "y": p.y()} for p in self.points],
            "smooth_curve_enabled": self.smooth_curve_enabled,
            "current_unit": self.current_unit,
        }

    def from_dict(self, data):
        """Load the widget's state from a dictionary."""
        self.x_scale = data.get("x_scale", 500)
        self.points = [QPointF(p["x"], p["y"]) for p in data.get("points", [{"x": 0, "y": 0}, {"x": 500, "y": 100}])]
        self.smooth_curve_enabled = data.get("smooth_curve_enabled", False)
        self.current_unit = data.get("current_unit", "kt")
        # self.unit_selector.setCurrentText(self.current_unit)
        # self.smooth_toggle.setChecked(self.smooth_curve_enabled)
        self.update()

    def clear_points(self):
        """Resets the points to the default values."""
        self.points = [QPointF(0, 0), QPointF(self.x_scale, 100)]  # Default 0% at 0 knots and 100% at 500 knots
        self.test_point = None  # Clear the test point when resetting
        self.update()

    def draw_test_intersection(self, painter):
        """Draws a dashed intersection line at the test point for demonstration."""
        if self.test_point:
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))

            # Convert the test point to widget space
            test_widget_point = self.map_to_widget_space(self.test_point)

            if not (np.isnan(test_widget_point.x()) or np.isnan(test_widget_point.y())):
                # Draw the vertical line representing the speed (convert to int)
                rect = self.rect().adjusted(self.margin_left, self.margin_top, -self.margin_right, -self.margin_bottom)
                painter.drawLine(int(test_widget_point.x()), rect.top(), int(test_widget_point.x()), rect.bottom())

                # Draw the horizontal line representing the gain (convert to int)
                painter.drawLine(rect.left(), int(test_widget_point.y()), rect.right(), int(test_widget_point.y()))
            else:
                # Handle invalid test point (e.g., NaN)
                print("Warning: Test point contains NaN, skipping drawing.")
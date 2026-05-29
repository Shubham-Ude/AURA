import sys
import math
import os
from PyQt5.QtCore import Qt, QTimer, QPointF, QRect, QPoint
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QRegion, QPixmap

from core.gui_interface import gui_interface


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class AuraHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.U.R.A.")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(250, 250)

        self.move_to_top_right()
        self.setMask(QRegion(self.rect()))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        self.pulse_angle = 0
        self.drag_pos = None
        self.status_text = "Awaiting command..."

        # ✅ Load background image using safe path
        self.bg_image = QPixmap(resource_path("assets/aura_bg.png"))

    def move_to_top_right(self):
        screen = QDesktopWidget().screenGeometry()
        x = screen.width() - self.width() - 20
        y = 20
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)

    def set_status_text(self, text: str):
        self.status_text = text
        self.update()

    def display_user_text(self, text: str):
        self.set_status_text(f"🧑 {text}")

    def display_aura_text(self, text: str):
        self.set_status_text(f"🤖 {text}")

    def paintEvent(self, event):
        if not self.isVisible():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2

        if not self.bg_image.isNull():
            img_size = 160
            top_left = QPointF(cx - img_size / 2 + 1, cy - img_size / 2 + 18)
            painter.drawPixmap(top_left, self.bg_image.scaled(img_size, img_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        glow_color = QColor(155, 100, 250, 10)
        border_color = QColor(100, 220, 255, 100)
        orbit_color = QColor(100, 255, 255, 50)
        text_color = QColor(200, 220, 255, 255)
        glow_text_color = QColor(255, 120, 100, 100)
        subtext_color = QColor(200, 220, 255, 100)

        self.pulse_angle += 2
        pulse_radius = 60 + 10 * math.sin(math.radians(self.pulse_angle))
        painter.setBrush(glow_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), pulse_radius, pulse_radius)

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), 60, 60)

        orbit_x = cx + 60 * math.cos(math.radians(self.pulse_angle))
        orbit_y = cy + 60 * math.sin(math.radians(self.pulse_angle))
        painter.setBrush(orbit_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(orbit_x, orbit_y), 4, 4)

        base_font = QFont("Orbitron", 8, QFont.Bold)
        painter.setFont(base_font)

        text = "-A.R.U.A-"
        radius = 55
        start_angle = 44
        angle_step = 12

        for i, char in enumerate(text):
            angle_deg = start_angle + i * angle_step
            angle_rad = math.radians(angle_deg)
            x = cx + radius * math.cos(angle_rad)
            y = cy + radius * math.sin(angle_rad)

            painter.save()
            painter.translate(x, y)
            painter.rotate(angle_deg - 90)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                glow_pos = QPoint(dx, dy)
                painter.setPen(QPen(glow_text_color, 2))
                painter.drawText(glow_pos, char)

            painter.setPen(QPen(text_color, 1))
            painter.drawText(QPoint(0, 0), char)
            painter.restore()

        painter.setFont(QFont("Consolas", 8))
        painter.setPen(subtext_color)
        painter.drawText(10, self.height() - 10, self.status_text)


def launch_gui():
    app = QApplication(sys.argv)
    gui = AuraHUD()
    gui_interface.connect(gui)
    gui.show()

    try:
        sys.exit(app.exec_())
    except RuntimeError:
        print("[AURA HUD] Closed safely.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки иконок Cisco
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from icon_manager import IconManager


class IconTestWindow(QMainWindow):
    """Окно для тестирования иконок"""
    
    def __init__(self):
        super().__init__()
        self.icon_manager = IconManager()
        self.init_ui()
        
    def init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle("Тест иконок Cisco")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Контролы
        controls_layout = QHBoxLayout()
        
        # Выбор типа устройства
        controls_layout.addWidget(QLabel("Тип устройства:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "host", "workstation", "server", "router", "switch", "gateway",
            "firewall", "printer", "camera", "access_point", "wireless_router"
        ])
        self.device_combo.currentTextChanged.connect(self.update_icon)
        controls_layout.addWidget(self.device_combo)
        
        # Выбор статуса
        controls_layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["online", "offline", "error", "maintenance"])
        self.status_combo.currentTextChanged.connect(self.update_icon)
        controls_layout.addWidget(self.status_combo)
        
        layout.addLayout(controls_layout)
        
        # Область отображения иконки
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setMinimumSize(200, 200)
        self.icon_label.setStyleSheet("border: 2px solid gray;")
        layout.addWidget(self.icon_label)
        
        # Информация об иконке
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        # Кнопка обновления
        refresh_button = QPushButton("Обновить иконку")
        refresh_button.clicked.connect(self.update_icon)
        layout.addWidget(refresh_button)
        
        # Обновляем иконку
        self.update_icon()
        
    def update_icon(self):
        """Обновление отображаемой иконки"""
        device_type = self.device_combo.currentText()
        status = self.status_combo.currentText()
        
        try:
            # Получаем иконку
            pixmap = self.icon_manager.get_device_icon(device_type, status)
            
            # Отображаем иконку
            self.icon_label.setPixmap(pixmap)
            
            # Обновляем информацию
            self.info_label.setText(f"Тип: {device_type}, Статус: {status}, Размер: {pixmap.width()}x{pixmap.height()}")
            
        except Exception as e:
            self.info_label.setText(f"Ошибка загрузки иконки: {str(e)}")


def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    
    window = IconTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
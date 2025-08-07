#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Редактор свойств соединений (L1, L2).
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QGroupBox, QFormLayout, QSpinBox, QTabWidget
)
from PyQt6.QtCore import pyqtSignal

class ConnectionEditor(QWidget):
    """Виджет для редактирования свойств соединения."""
    connection_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.current_connection = None
        self._init_ui()

    def _init_ui(self):
        """Инициализация пользовательского интерфейса."""
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # --- Вкладка L1 ---
        l1_widget = QWidget()
        l1_layout = QFormLayout(l1_widget)
        self.source_port_input = QLineEdit()
        self.target_port_input = QLineEdit()
        l1_layout.addRow("Порт источника:", self.source_port_input)
        l1_layout.addRow("Порт назначения:", self.target_port_input)
        self.tabs.addTab(l1_widget, "L1 - Порты")

        # --- Вкладка L2 ---
        l2_widget = QWidget()
        l2_layout = QFormLayout(l2_widget)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["access", "trunk"])
        self.vlan_input = QSpinBox()
        self.vlan_input.setRange(1, 4094)
        l2_layout.addRow("Тип порта:", self.type_combo)
        l2_layout.addRow("VLAN ID:", self.vlan_input)
        self.tabs.addTab(l2_widget, "L2 - VLAN")

        main_layout.addWidget(self.tabs)

        # --- Кнопки ---
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Применить")
        self.reset_button = QPushButton("Сбросить")
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)

        # --- Подключения ---
        self.apply_button.clicked.connect(self.apply_changes)
        self.reset_button.clicked.connect(self.reset_form)

        self.set_form_enabled(False)

    def set_connection(self, conn_data: Dict[str, Any]):
        """Загружает данные соединения в редактор."""
        self.current_connection = conn_data
        self.load_connection_data(conn_data)
        self.set_form_enabled(True)

    def load_connection_data(self, data: Dict[str, Any]):
        """Заполняет поля формы данными соединения."""
        l1 = data.get("l1", {})
        self.source_port_input.setText(l1.get("source_port", ""))
        self.target_port_input.setText(l1.get("target_port", ""))

        l2 = data.get("l2", {})
        self.type_combo.setCurrentText(l2.get("type", "access"))
        self.vlan_input.setValue(l2.get("vlan", 1))

    def apply_changes(self):
        """Применяет изменения к текущему соединению."""
        if not self.current_connection:
            return

        self.current_connection["l1"] = {
            "source_port": self.source_port_input.text(),
            "target_port": self.target_port_input.text()
        }
        self.current_connection["l2"] = {
            "type": self.type_combo.currentText(),
            "vlan": self.vlan_input.value()
        }
        self.connection_updated.emit(self.current_connection)

    def clear(self):
        """Очищает форму и деактивирует ее."""
        self.current_connection = None
        self.source_port_input.clear()
        self.target_port_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.vlan_input.setValue(1)
        self.set_form_enabled(False)

    def reset_form(self):
        """Сбрасывает форму к исходным данным соединения."""
        if self.current_connection:
            self.load_connection_data(self.current_connection)

    def set_form_enabled(self, enabled: bool):
        """Включает или отключает все поля ввода."""
        self.tabs.setEnabled(enabled)
        self.apply_button.setEnabled(enabled)
        self.reset_button.setEnabled(enabled)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QGroupBox,
                             QFormLayout, QMessageBox, QSpinBox, QTabWidget)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from anmp.utils.helpers import validate_ip, get_prefix_length, get_subnet_mask


class NodeEditor(QWidget):
    """Редактор свойств узлов с вкладками для L1, L2, L3."""
    node_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.current_node = None
        self._init_ui()

    def _init_ui(self):
        """Инициализация пользовательского интерфейса."""
        main_layout = QVBoxLayout(self)

        # --- Общие параметры ---
        general_group = QGroupBox("Общие параметры")
        general_layout = QFormLayout(general_group)
        
        self.id_label = QLabel() # ID будет только отображаться
        general_layout.addRow("ID:", self.id_label)

        self.name_input = QLineEdit()
        general_layout.addRow("Имя:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "host", "workstation", "server", "router", "switch", 
            "firewall", "access_point", "gateway", "printer", "camera"
        ])
        general_layout.addRow("Тип:", self.type_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["online", "offline", "maintenance", "error"])
        general_layout.addRow("Статус:", self.status_combo)

        coords_layout = QHBoxLayout()
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        coords_layout.addWidget(QLabel("X:"))
        coords_layout.addWidget(self.x_input)
        coords_layout.addWidget(QLabel("Y:"))
        coords_layout.addWidget(self.y_input)
        general_layout.addRow("Позиция:", coords_layout)

        main_layout.addWidget(general_group)

        # --- Вкладки L1, L2, L3 ---
        self.tabs = QTabWidget()
        self._create_l1_tab()
        self._create_l2_tab()
        self._create_l3_tab()
        main_layout.addWidget(self.tabs)

        # --- Кнопки ---
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Применить")
        self.reset_button = QPushButton("Сбросить")
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)

        # --- Индикаторы валидации ---
        self.ip_status_label = QLabel()
        self.ip_status_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.ip_status_label)

        # --- Подключения ---
        self.apply_button.clicked.connect(self.apply_changes)
        self.reset_button.clicked.connect(self.reset_form)

        self.set_form_enabled(False)

    def _create_l1_tab(self):
        l1_widget = QWidget()
        layout = QFormLayout(l1_widget)
        self.location_input = QLineEdit()
        layout.addRow("Расположение:", self.location_input)
        self.tabs.addTab(l1_widget, "L1 - Физический")

    def _create_l2_tab(self):
        l2_widget = QWidget()
        layout = QFormLayout(l2_widget)
        self.mac_input = QLineEdit()
        layout.addRow("MAC-адрес:", self.mac_input)
        self.vlan_input = QSpinBox()
        self.vlan_input.setRange(1, 4094)
        layout.addRow("VLAN ID:", self.vlan_input)
        self.tabs.addTab(l2_widget, "L2 - Канальный")

    def _create_l3_tab(self):
        l3_widget = QWidget()
        layout = QFormLayout(l3_widget)
        self.ip_input = QLineEdit()
        self.mask_input = QLineEdit()
        self.gateway_input = QLineEdit()
        layout.addRow("IP-адрес:", self.ip_input)
        layout.addRow("Маска:", self.mask_input)
        layout.addRow("Gateway:", self.gateway_input)
        self.tabs.addTab(l3_widget, "L3 - Сетевой")

    def set_node(self, node_data: Dict[str, Any]):
        self.current_node = node_data
        self.load_node_data(node_data)
        self.set_form_enabled(True)

    def clear(self):
        self.current_node = None
        self.clear_form()
        self.set_form_enabled(False)

    def load_node_data(self, data: Dict[str, Any]):
        self.id_label.setText(str(data.get("id", "")))
        self.name_input.setText(data.get("name", ""))
        self.type_combo.setCurrentText(data.get("type", "host"))
        self.status_combo.setCurrentText(data.get("status", "online"))
        self.x_input.setValue(int(data.get("x", 0)))
        self.y_input.setValue(int(data.get("y", 0)))

        l1 = data.get("l1", {})
        self.location_input.setText(l1.get("location", ""))

        l2 = data.get("l2", {})
        self.mac_input.setText(l2.get("mac", ""))
        self.vlan_input.setValue(l2.get("vlan", 1))

        l3 = data.get("l3", {})
        self.ip_input.setText(l3.get("ip", ""))
        self.mask_input.setText(l3.get("mask", ""))
        self.gateway_input.setText(l3.get("gateway", ""))

    def clear_form(self):
        self.id_label.clear()
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.x_input.setValue(0)
        self.y_input.setValue(0)
        self.location_input.clear()
        self.mac_input.clear()
        self.vlan_input.setValue(1)
        self.ip_input.clear()
        self.mask_input.clear()
        self.gateway_input.clear()
        self.ip_status_label.clear()

    def apply_changes(self):
        if not self.current_node:
            return

        self.current_node.update({
            "name": self.name_input.text().strip(),
            "type": self.type_combo.currentText(),
            "status": self.status_combo.currentText(),
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "l1": {"location": self.location_input.text().strip()},
            "l2": {"mac": self.mac_input.text().strip(), "vlan": self.vlan_input.value()},
            "l3": {
                "ip": self.ip_input.text().strip(),
                "mask": self.mask_input.text().strip(),
                "gateway": self.gateway_input.text().strip(),
            },
        })
        self.node_updated.emit(self.current_node)
        
    def reset_form(self):
        if self.current_node:
            self.load_node_data(self.current_node)

    def set_form_enabled(self, enabled: bool):
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLineEdit, QComboBox, QSpinBox, QPushButton)):
                widget.setEnabled(enabled)
        if enabled:
            self.id_label.setEnabled(True)
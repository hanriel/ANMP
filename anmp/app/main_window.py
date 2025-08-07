#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANMP - Advanced Network Mapping Platform
Главный модуль приложения, рефакторинговая версия.
"""

import sys
from typing import Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QSplitter, QTabWidget, QVBoxLayout, QMessageBox, 
    QStatusBar, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent

from anmp.app.app_state import AppStateManager
from anmp.app.file_controller import FileController
from anmp.app.menu_controller import MenuController
from anmp.ui.network_canvas import NetworkCanvas
from anmp.ui.node_editor import NodeEditor
from anmp.core.network_scanner import NetworkScanner
from anmp.ui.connection_editor import ConnectionEditor


class ANMPApp(QMainWindow):
    """Главное окно приложения ANMP."""

    def __init__(self):
        super().__init__()

        # 1. Инициализация основных компонентов
        self.app_state = AppStateManager()
        self.file_controller = FileController(self.app_state)
        self.menu_controller = MenuController(self)
        self.network_scanner = NetworkScanner()

        # 2. Инициализация компонентов UI
        self.canvases = {
            "l1": NetworkCanvas("l1"),
            "l2": NetworkCanvas("l2"),
            "l3": NetworkCanvas("l3")
        }
        self.topology_tabs = QTabWidget()
        for level, canvas in self.canvases.items():
            self.topology_tabs.addTab(canvas, level.upper())

        self.node_editor = NodeEditor()
        self.connection_editor = ConnectionEditor()
        self.scanner_widget = self.network_scanner.get_widget()

        # 3. Настройка UI
        self.init_ui()

        # 4. Настройка соединений (сигналы и слоты)
        self.setup_connections()

        # 5. Установка начального состояния
        self.canvases["l3"].draw_network_cloud()
        self.update_ui_from_state()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("ANMP - Сетевой картограф")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        splitter.addWidget(self.topology_tabs)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.side_tabs = QTabWidget()
        self.side_tabs.addTab(self.node_editor, "Свойства узла")
        self.side_tabs.addTab(self.connection_editor, "Свойства соединения")
        right_layout.addWidget(self.side_tabs)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([1000, 400])

        action_callbacks = self._create_action_callbacks()
        self.setMenuBar(self.menu_controller.create_menu_bar(action_callbacks))
        self.addToolBar(self.menu_controller.create_toolbar(action_callbacks))

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(1000)

    def setup_connections(self):
        """Настройка всех сигналов и слотов."""
        self.app_state.project_loaded.connect(self.on_project_loaded)
        self.file_controller.error_occurred.connect(self.show_error_message)

        for canvas in self.canvases.values():
            canvas.connection_selected.connect(self.connection_editor.set_connection)
            self.connection_editor.connection_updated.connect(canvas.update_connection)

        self.scanner_widget.nodes_discovered.connect(self.on_nodes_discovered)

    def get_active_canvas(self) -> NetworkCanvas:
        return self.topology_tabs.currentWidget()

    def _create_action_callbacks(self) -> Dict[str, callable]:
        return {
            'new_project': self.file_controller.new_project,
            'open_project': self.file_controller.open_project,
            'save_project': lambda: self.file_controller.save_project(self.get_full_data()),
            'save_project_as': lambda: self.file_controller.save_project_as(self.get_full_data()),
            'export_png': lambda: self.export_canvas_as_png(),
            'add_node': self.add_node_action,
            'add_connection': self.add_connection_action,
            'delete_selected': lambda: self.get_active_canvas().delete_selected(),
            'auto_layout': lambda: self.get_active_canvas().auto_layout(),
            'scan_network': lambda: self.side_tabs.setCurrentWidget(self.scanner_widget),
            'show_about': self.show_about_dialog,
        }

    def on_project_loaded(self, file_path: str):
        """Загружает данные из AppState на все холсты."""
        data = self.app_state.get_project_data()
        if not data:
            self.show_error_message(f"Не удалось получить данные для проекта: {file_path}")
            return

        nodes = data.get("nodes", [])
        topologies = data.get("topologies", {})
        for level, canvas in self.canvases.items():
            canvas.load_data({
                "nodes": nodes,
                "connections": topologies.get(level, {}).get("connections", [])
            })
        self.update_ui_from_state()
        self.status_bar.showMessage(f"Проект загружен: {file_path}", 5000)

    def on_project_saved(self, file_path: str):
        self.update_ui_from_state()
        self.status_bar.showMessage(f"Проект сохранен: {file_path}", 5000)

    def on_project_cleared(self):
        for canvas in self.canvases.values():
            canvas.clear()
        self.node_editor.clear()
        self.update_ui_from_state()

    def on_nodes_discovered(self, discovered_nodes: List[Dict[str, Any]]):
        # Узлы добавляются на все холсты, но соединения только на L3
        for canvas in self.canvases.values():
            canvas.add_discovered_nodes(discovered_nodes)
        self.app_state.mark_as_modified()

    def get_full_data(self) -> Dict[str, Any]:
        return {
            "nodes": self.canvases["l1"].get_nodes_data(),
            "topologies": {
                level: canvas.get_connections_data() for level, canvas in self.canvases.items()
            }
        }

    def add_node_action(self):
        # При добавлении узел появляется на всех топологиях
        node_data = self.get_active_canvas().add_node()
        for level, canvas in self.canvases.items():
            if canvas is not self.get_active_canvas():
                canvas.add_node(node_data)

    def add_connection_action(self):
        canvas = self.get_active_canvas()
        selected_nodes = canvas.get_selected_nodes()
        if len(selected_nodes) == 2:
            canvas.add_connection(selected_nodes[0].node_data["id"], selected_nodes[1].node_data["id"])
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите ровно два узла для создания соединения.")

    def show_error_message(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    def update_ui_from_state(self):
        has_project = self.app_state.get_current_file_path() is not None or self.app_state.has_unsaved_changes()
        self.menu_controller.update_action_states(
            has_project=has_project,
            has_unsaved_changes=self.app_state.has_unsaved_changes()
        )
        title = "ANMP - " + self.app_state.get_project_name()
        if self.app_state.has_unsaved_changes():
            title += " *"
        self.setWindowTitle(title)

    def update_status_bar(self):
        canvas = self.get_active_canvas()
        node_count = canvas.get_node_count()
        connection_count = canvas.get_connection_count()
        self.status_bar.showMessage(f"Уровень: {canvas.level.upper()} | Узлов: {node_count}, Связей: {connection_count}")

    def export_canvas_as_png(self):
        canvas = self.get_active_canvas()
        file_path, _ = QFileDialog.getSaveFileName(self, f"Экспорт {canvas.level.upper()} в PNG", "", "PNG файлы (*.png)")
        if file_path:
            canvas.export_png(file_path)

    def show_about_dialog(self):
        QMessageBox.about(self, "О программе", "ANMP - Версия 1.2")

    def closeEvent(self, event: QCloseEvent):
        if self.app_state.has_unsaved_changes():
            reply = QMessageBox.question(self, "Выход", "Сохранить изменения?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                if not self.file_controller.save_project(self.get_full_data()):
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()


def main():
    app = QApplication(sys.argv)
    window = ANMPApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
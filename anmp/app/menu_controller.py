#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Контроллер управления меню
Отвечает за создание и управление меню и панелью инструментов
"""

from typing import Callable, Dict, Any
from PyQt6.QtWidgets import QMenuBar, QToolBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import QObject


class MenuController(QObject):
    """Контроллер управления меню"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.actions: Dict[str, QAction] = {}
        
    def create_menu_bar(self, callbacks: Dict[str, Callable]) -> QMenuBar:
        """Создание панели меню"""
        menubar = QMenuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("&Файл")
        
        # Новый проект
        new_action = QAction("&Новый проект", self.parent)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(callbacks.get('new_project', lambda: None))
        file_menu.addAction(new_action)
        self.actions['new_project'] = new_action
        
        file_menu.addSeparator()
        
        # Открыть
        open_action = QAction("&Открыть...", self.parent)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(callbacks.get('open_project', lambda: None))
        file_menu.addAction(open_action)
        self.actions['open_project'] = open_action
        
        # Сохранить
        save_action = QAction("&Сохранить", self.parent)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(callbacks.get('save_project', lambda: None))
        file_menu.addAction(save_action)
        self.actions['save_project'] = save_action
        
        # Сохранить как
        save_as_action = QAction("Сохранить &как...", self.parent)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(callbacks.get('save_project_as', lambda: None))
        file_menu.addAction(save_as_action)
        self.actions['save_project_as'] = save_as_action
        
        file_menu.addSeparator()
        
        # Экспорт
        export_menu = file_menu.addMenu("&Экспорт")
        
        export_png_action = QAction("Экспорт в PNG...", self.parent)
        export_png_action.triggered.connect(callbacks.get('export_png', lambda: None))
        export_menu.addAction(export_png_action)
        self.actions['export_png'] = export_png_action
        
        export_pdf_action = QAction("Экспорт в PDF...", self.parent)
        export_pdf_action.triggered.connect(callbacks.get('export_pdf', lambda: None))
        export_menu.addAction(export_pdf_action)
        self.actions['export_pdf'] = export_pdf_action
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction("&Выход", self.parent)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(callbacks.get('exit_app', lambda: None))
        file_menu.addAction(exit_action)
        self.actions['exit_app'] = exit_action
        
        # Меню Правка
        edit_menu = menubar.addMenu("&Правка")
        
        # Добавить узел
        add_node_action = QAction("&Добавить узел", self.parent)
        add_node_action.setShortcut(QKeySequence("Ctrl+N"))
        add_node_action.triggered.connect(callbacks.get('add_node', lambda: None))
        edit_menu.addAction(add_node_action)
        self.actions['add_node'] = add_node_action
        
        # Удалить выбранное
        delete_action = QAction("&Удалить", self.parent)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(callbacks.get('delete_selected', lambda: None))
        edit_menu.addAction(delete_action)
        self.actions['delete_selected'] = delete_action
        
        edit_menu.addSeparator()
        
        # Автоматическая компоновка
        layout_action = QAction("&Автоматическая компоновка", self.parent)
        layout_action.setShortcut(QKeySequence("Ctrl+L"))
        layout_action.triggered.connect(callbacks.get('auto_layout', lambda: None))
        edit_menu.addAction(layout_action)
        self.actions['auto_layout'] = layout_action
        
        # Меню Сеть
        network_menu = menubar.addMenu("&Сеть")
        
        # Сканировать сеть
        scan_action = QAction("&Сканировать сеть...", self.parent)
        scan_action.setShortcut(QKeySequence("Ctrl+S"))
        scan_action.triggered.connect(callbacks.get('scan_network', lambda: None))
        network_menu.addAction(scan_action)
        self.actions['scan_network'] = scan_action
        
        # Проверить связность
        connectivity_action = QAction("&Проверить связность", self.parent)
        connectivity_action.setShortcut(QKeySequence("Ctrl+P"))
        connectivity_action.triggered.connect(callbacks.get('check_connectivity', lambda: None))
        network_menu.addAction(connectivity_action)
        self.actions['check_connectivity'] = connectivity_action
        
        # Меню Справка
        help_menu = menubar.addMenu("&Справка")
        
        about_action = QAction("&О программе", self.parent)
        about_action.triggered.connect(callbacks.get('show_about', lambda: None))
        help_menu.addAction(about_action)
        self.actions['show_about'] = about_action
        
        return menubar
        
    def create_toolbar(self, callbacks: Dict[str, Callable]) -> QToolBar:
        """Создание панели инструментов"""
        toolbar = QToolBar()
        
        # Кнопка добавления узла
        add_node_action = QAction("Добавить узел", self.parent)
        add_node_action.triggered.connect(callbacks.get('add_node', lambda: None))
        toolbar.addAction(add_node_action)
        
        # Кнопка добавления соединения
        add_connection_action = QAction("Соединить", self.parent)
        add_connection_action.triggered.connect(callbacks.get('add_connection', lambda: None))
        toolbar.addAction(add_connection_action)

        toolbar.addSeparator()
        
        # Кнопка сканирования
        scan_action = QAction("Сканировать", self.parent)
        scan_action.triggered.connect(callbacks.get('scan_network', lambda: None))
        toolbar.addAction(scan_action)
        
        # Кнопка компоновки
        layout_action = QAction("Компоновка", self.parent)
        layout_action.triggered.connect(callbacks.get('auto_layout', lambda: None))
        toolbar.addAction(layout_action)
        
        return toolbar
        
    def update_action_states(self, has_project: bool, has_unsaved_changes: bool):
        """Обновление состояний действий в зависимости от состояния приложения."""
        # Действия, которые требуют наличия проекта (открытого или нового с изменениями)
        project_dependent_actions = [
            'save_project_as', 'export_png', 'export_pdf', 
            'delete_selected', 'auto_layout', 'check_connectivity'
        ]
        for action_name in project_dependent_actions:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(has_project)

        # Кнопка "Сохранить" активна только если есть несохраненные изменения
        if 'save_project' in self.actions:
            self.actions['save_project'].setEnabled(has_unsaved_changes)

        # Некоторые действия всегда доступны
        always_enabled_actions = [
            'new_project', 'open_project', 'exit_app', 'add_node', 
            'scan_network', 'show_about'
        ]
        for action_name in always_enabled_actions:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(True) 
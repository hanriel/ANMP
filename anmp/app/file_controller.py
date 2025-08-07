#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Контроллер управления файлами
Отвечает за сохранение, загрузку и экспорт проектов
"""

from typing import Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from anmp.core.data_manager import DataManager
from anmp.app.app_state import AppStateManager


class FileController(QObject):
    """Контроллер управления файлами"""
    
    # Сигналы
    
    file_saved = pyqtSignal(str)    # путь к файлу
    file_exported = pyqtSignal(str) # путь к экспортированному файлу
    error_occurred = pyqtSignal(str) # сообщение об ошибке
    
    def __init__(self, state_manager: AppStateManager):
        super().__init__()
        self.state_manager = state_manager
        self.data_manager = DataManager()
        
    def new_project(self) -> bool:
        """Создание нового проекта."""
        if self._confirm_unsaved_changes("созданием нового проекта"):
            self.state_manager.new_project()
            return True
        return False
        
    def open_project(self) -> bool:
        """Открытие проекта."""
        if not self._confirm_unsaved_changes("открытием проекта"):
            return False

        file_path, _ = QFileDialog.getOpenFileName(
            None, "Открыть проект", "", "JSON файлы (*.json);;Все файлы (*)"
        )

        if file_path:
            return self._load_project_from_path(file_path)
        return False
        
    def save_project(self, data: Dict[str, Any]) -> bool:
        """Сохранение проекта"""
        if self.state_manager.get_current_file_path():
            return self._save_project_to_path(
                self.state_manager.get_current_file_path(), 
                data
            )
        else:
            return self.save_project_as(data)
            
    def save_project_as(self, data: Dict[str, Any]) -> bool:
        """Сохранение проекта как"""
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Сохранить проект", "",
            "JSON файлы (*.json);;Все файлы (*)"
        )
        
        if file_path:
            return self._save_project_to_path(file_path, data)
        
        return False
        
    def _load_project_from_path(self, file_path: str) -> bool:
        """Загрузка проекта из файла"""
        try:
            data = self.data_manager.load_project(file_path)
            self.state_manager.load_project(file_path, data)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Не удалось загрузить проект: {str(e)}")
            return False
            
    def _save_project_to_path(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Сохранение проекта в файл."""
        try:
            self.data_manager.save_project(data, file_path)
            self.state_manager.save_project(file_path, data)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Не удалось сохранить проект: {str(e)}")
            return False

    def _confirm_unsaved_changes(self, action_text: str) -> bool:
        """Запрашивает у пользователя подтверждение при наличии несохраненных изменений."""
        if not self.state_manager.has_unsaved_changes():
            return True

        reply = QMessageBox.question(
            None, "Несохраненные изменения",
            f"У вас есть несохраненные изменения. Сохранить их перед {action_text}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Yes:
            # Здесь может потребоваться передача данных с холста
            # В новой архитектуре это должно обрабатываться в ANMPApp
            # Пока что оставляем заглушку
            # return self.save_project(data)
            pass  # Логика сохранения будет вызываться из ANMPApp

        return True 
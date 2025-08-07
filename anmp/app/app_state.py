#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Менеджер состояния приложения
Централизованное управление состоянием ANMP
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class ProjectState:
    """Состояние проекта"""
    file_path: Optional[str] = None
    has_unsaved_changes: bool = False
    original_data: Optional[Dict[str, Any]] = None
    name: str = "Новый проект"
    created: Optional[datetime] = None
    modified: Optional[datetime] = None


class AppStateManager(QObject):
    """Менеджер состояния приложения"""
    
    # Сигналы изменения состояния
    project_loaded = pyqtSignal(str)  # путь к файлу
    project_saved = pyqtSignal(str)   # путь к файлу
    project_modified = pyqtSignal()   # проект изменен
    project_cleared = pyqtSignal()    # проект очищен
    
    def __init__(self):
        super().__init__()
        self.project_state = ProjectState()
        self.recent_files: List[str] = []
        self.max_recent_files = 10
        
    def load_project(self, file_path: str, data: Dict[str, Any]) -> None:
        """Загрузка проекта"""
        self.project_state.file_path = file_path
        self.project_state.original_data = data
        self.project_state.has_unsaved_changes = False
        self.project_state.modified = datetime.now()
        
        # Добавляем в список недавних файлов
        self._add_recent_file(file_path)
        
        self.project_loaded.emit(file_path)
        
    def save_project(self, file_path: str, data: Dict[str, Any]) -> None:
        """Сохранение проекта"""
        self.project_state.file_path = file_path
        self.project_state.original_data = data
        self.project_state.has_unsaved_changes = False
        self.project_state.modified = datetime.now()
        
        # Добавляем в список недавних файлов
        self._add_recent_file(file_path)
        
        self.project_saved.emit(file_path)
        
    def mark_as_modified(self) -> None:
        """Отметить проект как измененный"""
        self.project_state.has_unsaved_changes = True
        self.project_modified.emit()
        
    def clear_project(self) -> None:
        """Очистить проект"""
        self.project_state = ProjectState()
        self.project_cleared.emit()
        
    def new_project(self) -> None:
        """Создать новый проект"""
        self.project_state = ProjectState()
        self.project_state.created = datetime.now()
        self.project_state.modified = datetime.now()
        self.project_cleared.emit()
        
    def has_unsaved_changes(self) -> bool:
        """Есть ли несохраненные изменения"""
        return self.project_state.has_unsaved_changes
        
    def get_current_file_path(self) -> Optional[str]:
        """Получить путь к текущему файлу"""
        return self.project_state.file_path
        
    def get_project_name(self) -> str:
        """Получить имя проекта"""
        if self.project_state.file_path:
            import os
            return os.path.basename(self.project_state.file_path)
        return self.project_state.name
        
    def get_project_data(self) -> Optional[Dict[str, Any]]:
        """Возвращает данные текущего проекта."""
        return self.project_state.original_data

    def get_recent_files(self) -> List[str]:
        """Получить список недавних файлов"""
        return self.recent_files.copy()
        
    def _add_recent_file(self, file_path: str) -> None:
        """Добавить файл в список недавних"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        
        # Ограничиваем количество файлов
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files] 
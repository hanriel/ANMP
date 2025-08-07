#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class DataManager:
    """Менеджер данных для работы с проектами сетевых карт"""
    
    def __init__(self):
        self.current_project = None
        self.project_metadata = {}
        
    def create_new_project(self, name: str = "Новый проект") -> Dict[str, Any]:
        """Создание нового проекта с разделением на L1, L2, L3."""
        return {
            "metadata": {
                "name": name,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "version": "1.2"
            },
            "nodes": [], # Общий список узлов
            "topologies": {
                "l1": {"connections": []},
                "l2": {"connections": []},
                "l3": {"connections": []}
            },
            "settings": {
                "auto_layout": True
            }
        }
        
    def save_project(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        Сохранение проекта в файл
        
        Args:
            data: Данные проекта
            file_path: Путь к файлу
            
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            # Обновляем метаданные
            if "metadata" not in data:
                data["metadata"] = {}
            
            data["metadata"]["modified"] = datetime.now().isoformat()
            
            # Создаем резервную копию если файл существует
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(file_path, backup_path)
            
            # Сохраняем данные
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.current_project = data
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения проекта: {e}")
            return False
            
    def load_project(self, file_path: str) -> Dict[str, Any]:
        """
        Загрузка проекта из файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Данные проекта
            
        Raises:
            FileNotFoundError: Файл не найден
            json.JSONDecodeError: Ошибка парсинга JSON
            ValueError: Неверный формат данных
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Валидация структуры данных
            self._validate_project_data(data)
            
            # Обновляем метаданные
            if "metadata" not in data:
                data["metadata"] = {}
            
            data["metadata"]["loaded"] = datetime.now().isoformat()
            
            self.current_project = data
            return data
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка загрузки проекта: {e}")
            
    def _validate_project_data(self, data: Dict[str, Any]) -> None:
        """Валидация структуры данных проекта с разделением на топологии."""
        data.setdefault("topologies", {
            "l1": {"connections": []},
            "l2": {"connections": []},
            "l3": {"connections": []}
        })
        # ... (остальная валидация узлов, как и раньше)
                    
    def export_to_json(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        Экспорт данных в JSON
        
        Args:
            data: Данные для экспорта
            file_path: Путь к файлу
            
        Returns:
            True если экспорт успешен, False иначе
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False
            
    def import_from_json(self, file_path: str) -> Dict[str, Any]:
        """
        Импорт данных из JSON
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Импортированные данные
        """
        return self.load_project(file_path)
        
    def get_project_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Получение информации о проекте
        
        Args:
            data: Данные проекта
            
        Returns:
            Информация о проекте
        """
        info = {
            "name": data.get("network", {}).get("name", "Неизвестный проект"),
            "node_count": len(data.get("nodes", [])),
            "connection_count": len(data.get("connections", [])),
            "subnet_count": len(data.get("network", {}).get("subnets", [])),
            "created": data.get("metadata", {}).get("created", "Неизвестно"),
            "modified": data.get("metadata", {}).get("modified", "Неизвестно"),
            "version": data.get("metadata", {}).get("version", "1.0")
        }
        
        return info
        
    def validate_network_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Валидация сетевых данных
        
        Args:
            data: Данные для валидации
            
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        # Проверка узлов
        node_ids = set()
        node_ips = set()
        
        for i, node in enumerate(data.get("nodes", [])):
            # Проверка уникальности ID
            if node.get("id") in node_ids:
                errors.append(f"Дублирующийся ID узла: {node.get('id')}")
            else:
                node_ids.add(node.get("id"))
                
            # Проверка IP-адреса
            ip = node.get("ip", "")
            if ip in node_ips:
                errors.append(f"Дублирующийся IP-адрес: {ip}")
            else:
                node_ips.add(ip)
                
            # Проверка координат
            x, y = node.get("x", 0), node.get("y", 0)
            if x < 0 or y < 0:
                errors.append(f"Некорректные координаты узла {node.get('id')}: ({x}, {y})")
                
        # Проверка соединений
        connection_ids = set()
        
        for i, connection in enumerate(data.get("connections", [])):
            source_id = connection.get("source")
            target_id = connection.get("target")
            
            # Проверка существования узлов
            if source_id not in node_ids:
                errors.append(f"Соединение {i}: источник {source_id} не существует")
                
            if target_id not in node_ids:
                errors.append(f"Соединение {i}: цель {target_id} не существует")
                
            # Проверка уникальности соединений
            connection_id = (min(source_id, target_id), max(source_id, target_id))
            if connection_id in connection_ids:
                errors.append(f"Дублирующееся соединение: {source_id} - {target_id}")
            else:
                connection_ids.add(connection_id)
                
        return errors
        
    def merge_projects(self, project1: Dict[str, Any], project2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Объединение двух проектов
        
        Args:
            project1: Первый проект
            project2: Второй проект
            
        Returns:
            Объединенный проект
        """
        merged = project1.copy()
        
        # Объединяем узлы
        existing_ids = {node["id"] for node in merged.get("nodes", [])}
        max_id = max(existing_ids) if existing_ids else 0
        
        for node in project2.get("nodes", []):
            if node["id"] not in existing_ids:
                node["id"] = max_id + 1
                max_id += 1
                merged["nodes"].append(node)
                
        # Объединяем соединения
        existing_connections = {(conn["source"], conn["target"]) 
                              for conn in merged.get("connections", [])}
        
        for connection in project2.get("connections", []):
            conn_tuple = (connection["source"], connection["target"])
            if conn_tuple not in existing_connections:
                merged["connections"].append(connection)
                
        # Обновляем метаданные
        merged["metadata"]["merged"] = datetime.now().isoformat()
        merged["metadata"]["source_projects"] = [
            project1.get("metadata", {}).get("name", "Проект 1"),
            project2.get("metadata", {}).get("name", "Проект 2")
        ]
        
        return merged
        
    def create_backup(self, file_path: str) -> str:
        """
        Создание резервной копии проекта
        
        Args:
            file_path: Путь к файлу проекта
            
        Returns:
            Путь к резервной копии
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
            
        backup_path = f"{file_path}.backup"
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
                
        return backup_path
        
    def restore_backup(self, file_path: str) -> bool:
        """
        Восстановление из резервной копии
        
        Args:
            file_path: Путь к файлу проекта
            
        Returns:
            True если восстановление успешно, False иначе
        """
        backup_path = f"{file_path}.backup"
        
        if not os.path.exists(backup_path):
            return False
            
        try:
            # Создаем резервную копию текущего файла
            if os.path.exists(file_path):
                temp_backup = f"{file_path}.temp"
                os.rename(file_path, temp_backup)
            
            # Восстанавливаем из резервной копии
            os.rename(backup_path, file_path)
            
            return True
        except Exception as e:
            print(f"Ошибка восстановления: {e}")
            return False 
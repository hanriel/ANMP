#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки работы ANMP
"""

import sys
import os

def test_imports():
    """Тестирование импортов"""
    print("Тестирование импортов...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6 импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта PyQt6: {e}")
        return False
        
    try:
        import networkx as nx
        print("✓ NetworkX импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта NetworkX: {e}")
        return False
        
    try:
        import matplotlib
        print("✓ Matplotlib импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта Matplotlib: {e}")
        return False
        
    try:
        import scapy.all as scapy
        print("✓ Scapy импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта Scapy: {e}")
        print("  Примечание: Scapy может требовать прав администратора")
        
    try:
        import numpy as np
        print("✓ NumPy импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта NumPy: {e}")
        return False
        
    return True

def test_modules():
    """Тестирование модулей приложения"""
    print("\nТестирование модулей приложения...")
    
    try:
        from utils import validate_ip, validate_subnet
        print("✓ Модуль utils импортирован успешно")
        
        # Тестирование функций
        assert validate_ip("192.168.1.1") == True
        assert validate_ip("256.256.256.256") == False
        assert validate_subnet("192.168.1.0/24") == True
        assert validate_subnet("invalid") == False
        print("✓ Функции валидации работают корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в модуле utils: {e}")
        return False
        
    try:
        from data_manager import DataManager
        print("✓ Модуль data_manager импортирован успешно")
        
        # Тестирование DataManager
        dm = DataManager()
        project_data = dm.create_new_project("Тестовый проект")
        assert "nodes" in project_data
        assert "connections" in project_data
        print("✓ DataManager работает корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в модуле data_manager: {e}")
        return False
        
    try:
        from network_scanner import NetworkScanner
        print("✓ Модуль network_scanner импортирован успешно")
        
        # Тестирование NetworkScanner
        scanner = NetworkScanner()
        widget = scanner.get_widget()
        assert widget is not None
        print("✓ NetworkScanner работает корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в модуле network_scanner: {e}")
        return False
        
    try:
        from node_editor import NodeEditor
        print("✓ Модуль node_editor импортирован успешно")
        
        # Тестирование NodeEditor
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        editor = NodeEditor()
        assert editor is not None
        print("✓ NodeEditor работает корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в модуле node_editor: {e}")
        return False
        
    try:
        from network_canvas import NetworkCanvas
        print("✓ Модуль network_canvas импортирован успешно")
        
        # Тестирование NetworkCanvas
        canvas = NetworkCanvas()
        assert canvas is not None
        print("✓ NetworkCanvas работает корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в модуле network_canvas: {e}")
        return False
        
    return True

def test_main_app():
    """Тестирование главного приложения"""
    print("\nТестирование главного приложения...")
    
    try:
        from main import NetworkMapperApp
        print("✓ Главное приложение импортировано успешно")
        
        # Создаем QApplication если его нет
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        # Создаем главное окно
        window = NetworkMapperApp()
        assert window is not None
        print("✓ Главное окно создано успешно")
        
        # Закрываем окно
        window.close()
        print("✓ Приложение закрыто корректно")
        
    except Exception as e:
        print(f"✗ Ошибка в главном приложении: {e}")
        return False
        
    return True

def main():
    """Главная функция тестирования"""
    print("=== Тестирование ANMP ===\n")
    
    # Тестируем импорты
    if not test_imports():
        print("\n❌ Тестирование импортов не прошло")
        return False
        
    # Тестируем модули
    if not test_modules():
        print("\n❌ Тестирование модулей не прошло")
        return False
        
    # Тестируем главное приложение
    if not test_main_app():
        print("\n❌ Тестирование главного приложения не прошло")
        return False
        
    print("\n✅ Все тесты прошли успешно!")
    print("Приложение готово к запуску: python main.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
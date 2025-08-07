#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Менеджер иконок для отображения устройств Cisco
"""

import os
from typing import Dict, Optional
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize


class IconManager:
    """Менеджер иконок для устройств"""
    
    def __init__(self, icons_path: str = "icons/cisco"):
        self.icons_path = icons_path
        self.icon_cache: Dict[str, QPixmap] = {}
        self.device_icons = self._create_device_icon_mapping()
        
    def _create_device_icon_mapping(self) -> Dict[str, str]:
        """Создание соответствия типов устройств и иконок"""
        return {
            # Маршрутизаторы
            "router": "atm router.png",
            "gateway": "universal gateway.png",
            "vpn_gateway": "vpn gateway.png",
            "voice_router": "voice router.png",
            "tdm_router": "tdm router.png",
            "service_router": "Service router.png",
            "space_router": "Space router.png",
            
            # Коммутаторы
            "switch": "workgroup switch.png",
            "atm_switch": "atm switch.png",
            "voice_switch": "voice switch.png",
            "virtual_switch": "virtual layer switch.png",
            "director": "workgroup director.png",
            
            # Серверы
            "server": "www server.png",
            "file_server": "storage server.png",
            "web_server": "www server.png",
            "voice_server": "voice commserver.png",
            "unity_server": "unity server.png",
            "software_server": "software based server.png",
            
            # Рабочие станции
            "workstation": "workstation.png",
            "host": "standard host.png",
            "pc": "workstation.png",
            "sun_workstation": "sun workstation.png",
            
            # Принтеры и периферия
            "printer": "printer.png",  # Нужно добавить иконку принтера
            "terminal": "terminal.png",
            "tablet": "tablet.png",
            
            # Беспроводные устройства
            "access_point": "accesspoint.png",
            "wireless_router": "wireless router.png",
            "wireless_bridge": "wireless bridge.png",
            "wlan_controller": "wlan controller.png",
            
            # Сетевое оборудование
            "hub": "100baset hub.png",
            "small_hub": "small hub.png",
            "firewall": "firewall.png",  # Нужно добавить иконку файрвола
            "load_balancer": "ace.png",
            
            # Камеры и медиа
            "camera": "video camera.png",
            "tv": "tv.png",
            "set_top_box": "Set top box.png",
            
            # Люди
            "person": "standing man.png",
            "woman": "standing woman.png",
            "sitting_woman": "sitting woman.png",
            
            # Дополнительные устройства
            "ups": "ups.png",
            "antenna": "antenna.png",
            "supercomputer": "supercomputer.png",
            "storage_router": "storage router.png",
            
            # По умолчанию
            "default": "workstation.png"
        }
        
    def get_device_icon(self, device_type: str, status: str = "online") -> QPixmap:
        """
        Получение иконки для устройства
        
        Args:
            device_type: Тип устройства
            status: Статус устройства (online/offline/error/maintenance)
            
        Returns:
            QPixmap с иконкой устройства
        """
        # Определяем имя файла иконки
        icon_filename = self.device_icons.get(device_type, self.device_icons["default"])
        
        # Создаем ключ кэша
        cache_key = f"{icon_filename}_{status}"
        
        # Проверяем кэш
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
            
        # Загружаем иконку
        icon_path = os.path.join(self.icons_path, icon_filename)
        if not os.path.exists(icon_path):
            # Если иконка не найдена, используем иконку по умолчанию
            icon_path = os.path.join(self.icons_path, self.device_icons["default"])
            
        pixmap = QPixmap(icon_path)
        
        # Применяем эффекты в зависимости от статуса
        if status == "offline":
            pixmap = self._apply_grayscale_effect(pixmap)
        elif status == "error":
            pixmap = self._apply_red_tint_effect(pixmap)
        elif status == "maintenance":
            pixmap = self._apply_yellow_tint_effect(pixmap)
            
        # Масштабируем до нужного размера
        pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, 
                              Qt.TransformationMode.SmoothTransformation)
        
        # Кэшируем результат
        self.icon_cache[cache_key] = pixmap
        
        return pixmap
        
    def _apply_grayscale_effect(self, pixmap: QPixmap) -> QPixmap:
        """Применение эффекта черно-белого изображения"""
        # Простая реализация - можно улучшить
        return pixmap
        
    def _apply_red_tint_effect(self, pixmap: QPixmap) -> QPixmap:
        """Применение красного оттенка для ошибок"""
        # Простая реализация - можно улучшить
        return pixmap
        
    def _apply_yellow_tint_effect(self, pixmap: QPixmap) -> QPixmap:
        """Применение желтого оттенка для обслуживания"""
        # Простая реализация - можно улучшить
        return pixmap
        
    def get_available_icons(self) -> Dict[str, str]:
        """Получение списка доступных иконок"""
        available_icons = {}
        if os.path.exists(self.icons_path):
            for filename in os.listdir(self.icons_path):
                if filename.lower().endswith(('.png', '.jpeg', '.png')):
                    device_type = filename.replace('.png', '').replace('.jpeg', '').replace('.png', '')
                    available_icons[device_type] = filename
        return available_icons
        
    def add_device_icon_mapping(self, device_type: str, icon_filename: str):
        """Добавление нового соответствия типа устройства и иконки"""
        self.device_icons[device_type] = icon_filename
        
    def clear_cache(self):
        """Очистка кэша иконок"""
        self.icon_cache.clear()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGraphicsTextItem, QGraphicsLineItem, QGraphicsRectItem,
                             QGraphicsPixmapItem, QMenu, QInputDialog, QMessageBox, QColorDialog)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath, QPixmap

import networkx as nx
from anmp.utils.helpers import validate_ip
from anmp.utils.icon_manager import IconManager


class NetworkNode(QGraphicsPixmapItem):
    """Графический элемент узла сети с иконкой Cisco"""
    
    def __init__(self, node_data: Dict[str, Any], icon_manager: IconManager, parent=None):
        super().__init__(parent)
        self.node_data = node_data
        self.icon_manager = icon_manager
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Настройка внешнего вида
        self.update_appearance()
        
        # Создание текста
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.update_text()
        
        # Позиционирование текста под иконкой
        self.text_item.setPos(-30, 35)
        
    def update_appearance(self):
        """Обновление внешнего вида узла"""
        device_type = self.node_data.get("type", "host")
        status = self.node_data.get("status", "online")
        
        # Получаем иконку для устройства
        pixmap = self.icon_manager.get_device_icon(device_type, status)
        self.setPixmap(pixmap)
        
        # Устанавливаем точку трансформации в центр иконки
        self.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)
        
        # Добавляем рамку при выделении
        if self.isSelected():
            self.setGraphicsEffect(None)  # Сброс эффектов
            # Можно добавить эффект выделения здесь
        
    def update_text(self):
        """Обновление текста узла (имя и IP-адрес)."""
        name = self.node_data.get("name", "Unknown")
        ip = self.node_data.get("l3", {}).get("ip", "No IP")
        
        text = f"{name}\n{ip}"
        self.text_item.setPlainText(text)
        
        # Центрируем текст
        text_rect = self.text_item.boundingRect()
        pixmap_rect = self.pixmap().rect()
        self.text_item.setPos(
            (pixmap_rect.width() - text_rect.width()) / 2, 
            pixmap_rect.height()
        )
        
    def has_ip_conflict(self) -> bool:
        """Проверка конфликта IP-адресов"""
        # Эта проверка будет реализована в NetworkCanvas
        return False
        
    def mousePressEvent(self, event):
        """Обработка нажатия мыши."""
        # Логика выделения теперь обрабатывается в NetworkCanvas через on_selection_changed
        super().mousePressEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Отслеживание изменений для обновления соединений."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Принудительное обновление сцены для перерисовки связей
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        menu = QMenu()
        
        edit_action = menu.addAction("Редактировать")
        delete_action = menu.addAction("Удалить")
        menu.addSeparator()
        properties_action = menu.addAction("Свойства")
        
        action = menu.exec(event.screenPos())
        
        if action == edit_action:
            # Сигнал для редактирования
            pass
        elif action == delete_action:
            # Сигнал для удаления
            pass
        elif action == properties_action:
            # Сигнал для показа свойств
            pass


class NetworkConnection(QGraphicsLineItem):
    """Графический элемент соединения между узлами"""
    
    def __init__(self, source_node: NetworkNode, target_node: NetworkNode, 
                 connection_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.source_node = source_node
        self.target_node = target_node
        self.connection_data = connection_data
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Настройка внешнего вида
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.update_position()
        
    def update_position(self):
        """Обновление позиции линии"""
        source_pos = self.source_node.pos()
        target_pos = self.target_node.pos()
        
        # Рисуем линию от центра одного узла к центру другого
        self.setLine(source_pos.x(), source_pos.y(), 
                    target_pos.x(), target_pos.y())
        
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event)
        else:
            super().mousePressEvent(event)
            
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        menu = QMenu()
        
        delete_action = menu.addAction("Удалить соединение")
        properties_action = menu.addAction("Свойства")
        
        action = menu.exec(event.screenPos())
        
        if action == delete_action:
            # Сигнал для удаления соединения
            pass
        elif action == properties_action:
            # Сигнал для показа свойств
            pass


class NetworkCanvas(QGraphicsView):
    """Холст для рисования сетевых схем"""
    
    # Сигналы
    node_selected = pyqtSignal(dict)
    node_deselected = pyqtSignal()
    connection_selected = pyqtSignal(dict)
    
    def __init__(self, level: str):
        super().__init__()
        self.level = level
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Инициализация менеджера иконок
        self.icon_manager = IconManager()
        
        # Данные
        self.nodes = {}  # id -> NetworkNode
        self.connections = {}  # (source_id, target_id) -> NetworkConnection
        self.next_node_id = 1
        
        # Настройки
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Обработчики событий
        self.setup_event_handlers()
        
        # Подключаем сигнал изменения выделения
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        # Таймер для обновления соединений
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_connections)
        self.update_timer.start(100)  # Обновляем каждые 100мс
        
    def setup_event_handlers(self):
        """Настройка обработчиков событий"""
        # Двойной клик для добавления узла
        self.mouseDoubleClickEvent = self.on_double_click
        
    def on_double_click(self, event):
        """Обработка двойного клика"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Добавляем новый узел в позиции клика
            pos = self.mapToScene(event.pos())
            self.add_node_at_position(pos.x(), pos.y())
            
    def add_node(self, node_data: Optional[Dict[str, Any]] = None) -> int:
        """Добавление нового узла с правильной структурой данных."""
        new_id = self.next_node_id

        if node_data is None:
            node_data = {"id": self.next_node_id}
        else:
            node_data["id"] = self.next_node_id
        node_data.setdefault("name", f"Device-{new_id}")
        node_data.setdefault("type", "host")
        node_data.setdefault("x", random.randint(50, 400))
        node_data.setdefault("y", random.randint(50, 300))
        node_data.setdefault("status", "online")
        node_data.setdefault("l1", {"ports": [], "location": ""})
        node_data.setdefault("l2", {"mac": "", "vlan": 1})
        node_data.setdefault("l3", {"ip": f"192.168.1.{new_id}", "mask": "255.255.255.0", "gateway": ""})
        
        node_item = NetworkNode(node_data, self.icon_manager)
        node_item.setPos(node_data["x"], node_data["y"])
        
        self.scene.addItem(node_item)
        self.nodes[node_data["id"]] = node_item
        
        self.next_node_id += 1
        return node_data["id"]
        
    def add_node_at_position(self, x: float, y: float) -> int:
        """Добавление узла в указанной позиции"""
        node_data = {
            "name": f"Node-{self.next_node_id}",
            "type": "host",
            "ip": f"192.168.1.{self.next_node_id}",
            "mask": "255.255.255.0",
            "x": x,
            "y": y,
            "status": "online"
        }
        
        return self.add_node(node_data)
        
    def add_discovered_nodes(self, discovered_nodes: List[Dict[str, Any]]):
        """Добавление обнаруженных узлов"""
        for node_info in discovered_nodes:
            # Преобразуем данные сканера в формат узла
            node_data = {
                "name": node_info.get("name", f"Host-{node_info['ip'].split('.')[-1]}"),
                "type": node_info.get("type", "host"),
                "ip": node_info["ip"],
                "mask": node_info.get("mask", "255.255.255.0"),
                "x": random.randint(50, 600),
                "y": random.randint(50, 400),
                "status": node_info.get("status", "online"),
                "ports": node_info.get("ports", [])
            }
            
            self.add_node(node_data)
            
    def update_node(self, node_data: Dict[str, Any]):
        """Обновление узла"""
        node_id = node_data["id"]
        if node_id in self.nodes:
            node_item = self.nodes[node_id]
            node_item.node_data.update(node_data)
            node_item.update_appearance()
            node_item.update_text()
            
            # Обновляем позицию если изменилась
            if "x" in node_data and "y" in node_data:
                node_item.setPos(node_data["x"], node_data["y"])
                
    def delete_selected(self):
        """Удаление выбранных элементов"""
        selected_items = self.scene.selectedItems()
        
        for item in selected_items:
            if isinstance(item, NetworkNode):
                self.delete_node(item.node_data["id"])
            elif isinstance(item, NetworkConnection):
                self.delete_connection(item)
                
    def delete_node(self, node_id: int):
        """Удаление узла"""
        if node_id in self.nodes:
            # Удаляем все соединения с этим узлом
            connections_to_remove = []
            for (source_id, target_id), connection in self.connections.items():
                if source_id == node_id or target_id == node_id:
                    connections_to_remove.append((source_id, target_id))
                    
            for conn_id in connections_to_remove:
                self.delete_connection(self.connections[conn_id])
                
            # Удаляем узел
            node_item = self.nodes[node_id]
            self.scene.removeItem(node_item)
            del self.nodes[node_id]
            
    def delete_connection(self, connection: NetworkConnection):
        """Удаление соединения"""
        # Находим ключ соединения
        conn_key = None
        for key, conn in self.connections.items():
            if conn == connection:
                conn_key = key
                break
                
        if conn_key:
            self.scene.removeItem(connection)
            del self.connections[conn_key]
            
    def add_connection(self, source_id: int, target_id: int, 
                      connection_data: Optional[Dict[str, Any]] = None):
        """Добавление соединения между узлами"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return
            
        if source_id == target_id:
            return  # Нельзя соединить узел с самим собой
            
        # Проверяем, не существует ли уже такое соединение
        conn_key = (min(source_id, target_id), max(source_id, target_id))
        if conn_key in self.connections:
            return
            
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        
        if connection_data is None:
            connection_data = {
                "source": source_id,
                "target": target_id,
                "type": "ethernet"
            }
            
        connection = NetworkConnection(source_node, target_node, connection_data)
        self.scene.addItem(connection)
        self.connections[conn_key] = connection
        
    def update_connection(self, connection_data: Dict[str, Any]):
        """Обновляет данные соединения."""
        source_id = connection_data.get("source")
        target_id = connection_data.get("target")
        conn_key = (min(source_id, target_id), max(source_id, target_id))

        if conn_key in self.connections:
            self.connections[conn_key].connection_data.update(connection_data)
            # Здесь можно добавить визуальное обновление, если потребуется
            self.scene.update()

    def update_connections(self):
        """Обновление позиций соединений."""
        for connection in self.connections.values():
            connection.update_position()
            
    def auto_layout(self):
        """Автоматическая компоновка узлов"""
        if not self.nodes:
            return
            
        # Создаем граф для компоновки
        G = nx.Graph()
        
        # Добавляем узлы
        for node_id, node_item in self.nodes.items():
            G.add_node(node_id)
            
        # Добавляем ребра
        for (source_id, target_id) in self.connections.keys():
            G.add_edge(source_id, target_id)
            
        # Используем spring layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Применяем позиции
        for node_id, position in pos.items():
            if node_id in self.nodes:
                # Масштабируем координаты
                x = position[0] * 300 + 400
                y = position[1] * 300 + 300
                
                node_item = self.nodes[node_id]
                node_item.setPos(x, y)
                
                # Обновляем данные узла
                node_item.node_data["x"] = x
                node_item.node_data["y"] = y
                
    def get_isolated_nodes(self) -> List[str]:
        """Возвращает список имен изолированных узлов."""
        isolated_node_names = []
        all_node_ids = set(self.nodes.keys())
        connected_node_ids = set()

        for source_id, target_id in self.connections.keys():
            connected_node_ids.add(source_id)
            connected_node_ids.add(target_id)

        isolated_ids = all_node_ids - connected_node_ids
        for node_id in isolated_ids:
            isolated_node_names.append(self.nodes[node_id].node_data.get("name", f"ID: {node_id}"))
        
        return isolated_node_names
            
    def clear(self):
        """Очистка холста."""
        self.scene.clear()
        self.nodes.clear()
        self.connections.clear()
        self.next_node_id = 1
        if self.level == "l3":
            self.draw_network_cloud()
        if self.level == "l3":
            self.draw_network_cloud()
        
    def get_nodes_data(self) -> List[Dict[str, Any]]:
        """Возвращает данные всех узлов на холсте."""
        nodes_data = []
        for node_item in self.nodes.values():
            node_item.node_data["x"] = node_item.pos().x()
            node_item.node_data["y"] = node_item.pos().y()
            nodes_data.append(node_item.node_data)
        return nodes_data

    def get_connections_data(self) -> Dict[str, Any]:
        """Возвращает данные о соединениях на холсте."""
        return {"connections": [c.connection_data for c in self.connections.values()]}

    def get_selected_nodes(self) -> List[NetworkNode]:
        """Возвращает список выделенных узлов."""
        return [item for item in self.scene.selectedItems() if isinstance(item, NetworkNode)]
        
    def load_data(self, data: Dict[str, Any]):
        """Загрузка данных схемы"""
        self.clear()
        
        # Загружаем узлы
        for node_data in data.get("nodes", []):
            self.add_node(node_data)
            
        # Загружаем соединения
        for connection_data in data.get("connections", []):
            source_id = connection_data.get("source")
            target_id = connection_data.get("target")
            if source_id and target_id:
                self.add_connection(source_id, target_id, connection_data)
                
    def get_node_count(self) -> int:
        """Получение количества узлов"""
        return len(self.nodes)
        
    def get_connection_count(self) -> int:
        """Получение количества соединений"""
        return len(self.connections)
        
    def export_png(self, file_path: str):
        """Экспорт в PNG"""
        # Создаем pixmap с размером сцены
        rect = self.scene.sceneRect()
        pixmap = QPixmap(int(rect.width()), int(rect.height()))
        pixmap.fill(QColor(255, 255, 255))
        
        # Рисуем сцену на pixmap
        painter = QPainter(pixmap)
        self.scene.render(painter)
        painter.end()
        
        # Сохраняем
        pixmap.save(file_path)
        
    def export_pdf(self, file_path: str):
        """Экспорт в PDF"""
        # Эта функция требует дополнительных библиотек для работы с PDF
        # Пока что просто сохраняем как PNG
        self.export_png(file_path.replace('.pdf', '.png'))
        
    
        
    def draw_network_cloud(self):
        """Рисует облако сети на заднем плане используя иконку."""
        pixmap = QPixmap(os.path.join(self.icon_manager.icons_path, "cloud.jpg"))
        if not pixmap.isNull():
            cloud_item = self.scene.addPixmap(pixmap)
            cloud_item.setPos(20, 20) # Позиция облака
            cloud_item.setZValue(-1) # Помещаем на задний план

    def on_selection_changed(self):
        """Обработчик изменения выделения."""
        selected_items = self.scene.selectedItems()
        
        if not selected_items:
            self.node_deselected.emit()
            return

        # Отдаем приоритет соединениям
        for item in selected_items:
            if isinstance(item, NetworkConnection):
                self.connection_selected.emit(item.connection_data)
                return

        # Если соединения не выбраны, ищем узлы
        for item in selected_items:
            if isinstance(item, NetworkNode):
                self.node_selected.emit(item.node_data)
                return 
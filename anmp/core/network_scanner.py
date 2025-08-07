#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import ipaddress
import socket
import subprocess
import platform
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QProgressBar,
                             QSpinBox, QComboBox, QGroupBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Scapy недоступен, будет использован альтернативный метод сканирования")

from anmp.utils.helpers import validate_ip, validate_subnet, get_subnet_mask


class NetworkScannerThread(QThread):
    """Поток для сканирования сети"""
    
    # Сигналы для обновления UI
    progress_updated = pyqtSignal(int)
    node_discovered = pyqtSignal(dict)
    scan_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, target_network: str, timeout: int = 1000, 
                 scan_ports: bool = False, ports: List[int] = None):
        super().__init__()
        self.target_network = target_network
        self.timeout = timeout
        self.scan_ports = scan_ports
        self.ports = ports or [80, 443, 22, 21, 23, 25, 53, 110, 143, 993, 995]
        self.stop_scan = False
        
    def run(self):
        """Выполнение сканирования сети"""
        try:
            # Парсинг сети с помощью ipaddress
            network = ipaddress.IPv4Network(self.target_network, strict=False)
            total_hosts = len(list(network.hosts()))
            
            if total_hosts == 0:
                self.error_occurred.emit("Нет доступных хостов в сети")
                return
                
            discovered_nodes = []
            current_progress = 0
            
            # Сканирование каждого хоста
            for host in network.hosts():
                if self.stop_scan:
                    break
                    
                host_ip = str(host)
                
                # Ping для проверки доступности
                if self._ping_host(host_ip):
                    node_info = {
                        "ip": host_ip,
                        "name": f"Host-{host_ip.split('.')[-1]}",
                        "type": "host",
                        "mask": str(network.netmask),
                        "status": "online",
                        "ports": []
                    }
                    
                    # Сканирование портов если включено
                    if self.scan_ports:
                        open_ports = self._scan_ports(host_ip)
                        node_info["ports"] = open_ports
                        
                        # Определение типа устройства по открытым портам
                        node_info["type"] = self._detect_device_type(open_ports)
                    
                    discovered_nodes.append(node_info)
                    self.node_discovered.emit(node_info)
                
                current_progress += 1
                progress_percent = int((current_progress / total_hosts) * 100)
                self.progress_updated.emit(progress_percent)
                
                # Небольшая задержка между запросами
                time.sleep(0.1)
            
            self.scan_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка сканирования: {str(e)}")
    
    def _ping_host(self, ip: str) -> bool:
        """Проверка доступности хоста через ping"""
        try:
            if SCAPY_AVAILABLE:
                # Используем Scapy если доступен
                return self._ping_host_scapy(ip)
            else:
                # Используем системный ping
                return self._ping_host_system(ip)
        except Exception:
            return False
    
    def _ping_host_scapy(self, ip: str) -> bool:
        """Ping через Scapy"""
        try:
            # Отправляем ARP-запрос
            arp_request = scapy.ARP(pdst=ip)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            # Отправляем пакет и ждем ответ
            answered_list = scapy.srp(arp_request_broadcast, timeout=self.timeout/1000, verbose=False)[0]
            
            return len(answered_list) > 0
        except Exception:
            return False
    
    def _ping_host_system(self, ip: str) -> bool:
        """Ping через системную команду"""
        try:
            # Определяем команду ping в зависимости от ОС
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(self.timeout), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(self.timeout//1000), ip]
            
            # Выполняем команду
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def _scan_ports(self, ip: str) -> List[int]:
        """Сканирование открытых портов"""
        open_ports = []
        
        for port in self.ports:
            if self.stop_scan:
                break
                
            try:
                if SCAPY_AVAILABLE:
                    # Используем Scapy для сканирования портов
                    open_ports.extend(self._scan_ports_scapy(ip, port))
                else:
                    # Используем socket для сканирования портов
                    if self._scan_port_socket(ip, port):
                        open_ports.append(port)
                        
            except Exception:
                continue
                
        return open_ports
    
    def _scan_ports_scapy(self, ip: str, port: int) -> List[int]:
        """Сканирование портов через Scapy"""
        try:
            # Создаем TCP-соединение
            syn_packet = scapy.IP(dst=ip) / scapy.TCP(dport=port, flags="S")
            response = scapy.sr1(syn_packet, timeout=1, verbose=False)
            
            if response and response.haslayer(scapy.TCP):
                if response[scapy.TCP].flags == 0x12:  # SYN-ACK
                    return [port]
        except Exception:
            pass
        return []
    
    def _scan_port_socket(self, ip: str, port: int) -> bool:
        """Сканирование порта через socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _detect_device_type(self, ports: List[int]) -> str:
        """Определение типа устройства по открытым портам"""
        if 80 in ports or 443 in ports:
            return "server"
        elif 22 in ports:
            return "router"
        elif 23 in ports:
            return "switch"
        elif 21 in ports:
            return "ftp_server"
        elif 25 in ports or 110 in ports or 143 in ports:
            return "mail_server"
        elif 53 in ports:
            return "dns_server"
        else:
            return "host"
    
    def stop(self):
        """Остановка сканирования"""
        self.stop_scan = True


class NetworkScanner:
    """Класс для сканирования сети"""
    
    def __init__(self):
        self.scanner_thread = None
        self.discovered_nodes = []
        self.canvas = None  # Ссылка на холст
        
    def set_canvas(self, canvas):
        """Устанавливает ссылку на холст для передачи узлов"""
        self.canvas = canvas
        
    def get_widget(self) -> QWidget:
        """Получение виджета сканера"""
        return NetworkScannerWidget(self)
    
    def start_scan(self, target_network: str, timeout: int = 1000, 
                   scan_ports: bool = False, ports: List[int] = None) -> None:
        """Запуск сканирования сети"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            return
            
        self.scanner_thread = NetworkScannerThread(target_network, timeout, scan_ports, ports)
        self.scanner_thread.node_discovered.connect(self._on_node_discovered)
        self.scanner_thread.start()
    
    def stop_scan(self) -> None:
        """Остановка сканирования"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()
    
    def _on_node_discovered(self, node_info: Dict[str, Any]) -> None:
        """Обработка обнаруженного узла"""
        self.discovered_nodes.append(node_info)
        
        # Если есть ссылка на холст, добавляем узел сразу
        if self.canvas:
            # Проверяем, нет ли уже такого IP на карте
            existing_ips = set()
            for node in self.canvas.nodes.values():
                ip = node.node_data.get('ip')
                if ip:
                    existing_ips.add(ip)
            
            # Добавляем только если IP ещё нет на карте
            if node_info.get('ip') not in existing_ips:
                self.canvas.add_discovered_nodes([node_info])
    
    def get_discovered_nodes(self) -> List[Dict[str, Any]]:
        """Получение списка обнаруженных узлов"""
        return self.discovered_nodes.copy()
    
    def clear_discovered_nodes(self) -> None:
        """Очистка списка обнаруженных узлов"""
        self.discovered_nodes.clear()


class NetworkScannerWidget(QWidget):
    """Виджет для сканирования сети"""
    
    # Сигнал для передачи обнаруженных узлов
    nodes_discovered = pyqtSignal(list)
    
    def __init__(self, scanner: NetworkScanner):
        super().__init__()
        self.scanner = scanner
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        
        # Группа настроек сканирования
        scan_group = QGroupBox("Настройки сканирования")
        scan_layout = QVBoxLayout(scan_group)
        
        # Поле ввода сети
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Целевая сеть:"))
        self.network_input = QLineEdit()
        self.network_input.setPlaceholderText("192.168.1.0/24")
        network_layout.addWidget(self.network_input)
        scan_layout.addLayout(network_layout)
        
        # Таймаут
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Таймаут (мс):"))
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(100, 10000)
        self.timeout_input.setValue(1000)
        self.timeout_input.setSuffix(" мс")
        timeout_layout.addWidget(self.timeout_input)
        scan_layout.addLayout(timeout_layout)
        
        # Опции сканирования
        options_layout = QHBoxLayout()
        
        self.scan_ports_checkbox = QCheckBox("Сканировать порты")
        self.scan_ports_checkbox.setChecked(False)
        options_layout.addWidget(self.scan_ports_checkbox)
        
        self.auto_detect_checkbox = QCheckBox("Автоопределение типа")
        self.auto_detect_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_detect_checkbox)
        
        scan_layout.addLayout(options_layout)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Начать сканирование")
        self.start_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)
        
        scan_layout.addLayout(button_layout)
        layout.addWidget(scan_group)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Результаты сканирования
        results_group = QGroupBox("Результаты сканирования")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        # Статистика
        self.stats_label = QLabel("Найдено узлов: 0")
        results_layout.addWidget(self.stats_label)
        
        layout.addWidget(results_group)
        
    def setup_connections(self):
        """Настройка связей"""
        if hasattr(self.scanner, 'scanner_thread') and self.scanner.scanner_thread:
            self.scanner.scanner_thread.progress_updated.connect(self.update_progress)
            self.scanner.scanner_thread.node_discovered.connect(self.add_discovered_node)
            self.scanner.scanner_thread.scan_finished.connect(self.scan_finished)
            self.scanner.scanner_thread.error_occurred.connect(self.scan_error)
    
    def start_scan(self):
        """Запуск сканирования"""
        target_network = self.network_input.text().strip()
        
        if not target_network:
            QMessageBox.warning(self, "Ошибка", "Введите целевую сеть")
            return
            
        if not validate_subnet(target_network):
            QMessageBox.warning(self, "Ошибка", "Неверный формат сети. Используйте CIDR (например, 192.168.1.0/24)")
            return
        
        # Очищаем предыдущие результаты
        self.results_text.clear()
        self.scanner.clear_discovered_nodes()
        
        # Настраиваем UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Запускаем сканирование
        timeout = self.timeout_input.value()
        scan_ports = self.scan_ports_checkbox.isChecked()
        
        self.scanner.start_scan(target_network, timeout, scan_ports)
        
        # Настраиваем связи для нового потока
        if self.scanner.scanner_thread:
            self.scanner.scanner_thread.progress_updated.connect(self.update_progress)
            self.scanner.scanner_thread.node_discovered.connect(self.add_discovered_node)
            self.scanner.scanner_thread.scan_finished.connect(self.scan_finished)
            self.scanner.scanner_thread.error_occurred.connect(self.scan_error)
    
    def stop_scan(self):
        """Остановка сканирования"""
        self.scanner.stop_scan()
        self.scan_finished()
    
    def clear_results(self):
        """Очистка результатов"""
        self.results_text.clear()
        self.scanner.clear_discovered_nodes()
        self.stats_label.setText("Найдено узлов: 0")
    
    def update_progress(self, value: int):
        """Обновление прогресс-бара"""
        self.progress_bar.setValue(value)
    
    def add_discovered_node(self, node_info: Dict[str, Any]):
        """Добавление обнаруженного узла"""
        ip = node_info["ip"]
        name = node_info["name"]
        device_type = node_info["type"]
        status = node_info["status"]
        
        # Форматируем информацию об узле
        node_text = f"IP: {ip} | Имя: {name} | Тип: {device_type} | Статус: {status}"
        
        if node_info.get("ports"):
            ports_str = ", ".join(map(str, node_info["ports"]))
            node_text += f" | Порт(ы): {ports_str}"
        
        self.results_text.append(node_text)
        
        # Обновляем статистику
        discovered_count = len(self.scanner.get_discovered_nodes())
        self.stats_label.setText(f"Найдено узлов: {discovered_count}")
    
    def scan_finished(self):
        """Завершение сканирования"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        discovered_nodes = self.scanner.get_discovered_nodes()
        if discovered_nodes:
            self.results_text.append(f"\nСканирование завершено. Найдено {len(discovered_nodes)} узлов.")
            # Отправляем сигнал с обнаруженными узлами
            self.nodes_discovered.emit(discovered_nodes)
        else:
            self.results_text.append("\nСканирование завершено. Узлы не найдены.")
    
    def scan_error(self, error_message: str):
        """Обработка ошибки сканирования"""
        QMessageBox.critical(self, "Ошибка сканирования", error_message)
        self.scan_finished() 
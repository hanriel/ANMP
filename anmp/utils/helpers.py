#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import ipaddress
from typing import Tuple, Optional, List


def validate_ip(ip_str: str) -> bool:
    """
    Валидация IPv4 адреса
    
    Args:
        ip_str: Строка с IP-адресом
        
    Returns:
        True если адрес корректен, False иначе
    """
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_subnet(subnet_str: str) -> bool:
    """
    Валидация подсети в формате CIDR
    
    Args:
        subnet_str: Строка с подсетью (например, "192.168.1.0/24")
        
    Returns:
        True если подсеть корректна, False иначе
    """
    try:
        ipaddress.IPv4Network(subnet_str, strict=False)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def parse_subnet(subnet_str: str) -> Optional[Tuple[str, int]]:
    """
    Парсинг подсети в формате CIDR
    
    Args:
        subnet_str: Строка с подсетью
        
    Returns:
        Кортеж (network_address, prefix_length) или None при ошибке
    """
    try:
        network = ipaddress.IPv4Network(subnet_str, strict=False)
        return str(network.network_address), network.prefixlen
    except (ipaddress.AddressValueError, ValueError):
        return None


def get_subnet_mask(prefix_length: int) -> str:
    """
    Получение маски подсети по длине префикса
    
    Args:
        prefix_length: Длина префикса (0-32)
        
    Returns:
        Маска подсети в формате "255.255.255.0"
    """
    if not 0 <= prefix_length <= 32:
        raise ValueError("Длина префикса должна быть от 0 до 32")
    
    mask = (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF
    return ".".join(str((mask >> i) & 0xFF) for i in (24, 16, 8, 0))


def get_prefix_length(mask: str) -> int:
    """
    Получение длины префикса по маске подсети
    
    Args:
        mask: Маска подсети в формате "255.255.255.0"
        
    Returns:
        Длина префикса (0-32)
    """
    try:
        mask_parts = [int(x) for x in mask.split('.')]
        if len(mask_parts) != 4:
            raise ValueError("Неверный формат маски")
        
        binary_mask = sum(mask_parts[i] << (24 - i * 8) for i in range(4))
        return bin(binary_mask).count('1')
    except (ValueError, IndexError):
        raise ValueError("Неверный формат маски")


def is_ip_in_subnet(ip: str, subnet: str) -> bool:
    """
    Проверка принадлежности IP-адреса к подсети
    
    Args:
        ip: IP-адрес для проверки
        subnet: Подсеть в формате CIDR
        
    Returns:
        True если IP принадлежит подсети, False иначе
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        network = ipaddress.IPv4Network(subnet, strict=False)
        return ip_addr in network
    except (ipaddress.AddressValueError, ValueError):
        return False


def get_network_address(ip: str, mask: str) -> str:
    """
    Получение адреса сети по IP и маске
    
    Args:
        ip: IP-адрес
        mask: Маска подсети
        
    Returns:
        Адрес сети
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        prefix_length = get_prefix_length(mask)
        network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
        return str(network.network_address)
    except (ipaddress.AddressValueError, ValueError):
        raise ValueError("Неверный IP-адрес или маска")


def get_broadcast_address(ip: str, mask: str) -> str:
    """
    Получение широковещательного адреса по IP и маске
    
    Args:
        ip: IP-адрес
        mask: Маска подсети
        
    Returns:
        Широковещательный адрес
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        prefix_length = get_prefix_length(mask)
        network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
        return str(network.broadcast_address)
    except (ipaddress.AddressValueError, ValueError):
        raise ValueError("Неверный IP-адрес или маска")


def get_host_range(ip: str, mask: str) -> Tuple[str, str]:
    """
    Получение диапазона хостов в подсети
    
    Args:
        ip: IP-адрес
        mask: Маска подсети
        
    Returns:
        Кортеж (первый_хост, последний_хост)
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        prefix_length = get_prefix_length(mask)
        network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
        
        hosts = list(network.hosts())
        if hosts:
            return str(hosts[0]), str(hosts[-1])
        else:
            return str(network.network_address), str(network.broadcast_address)
    except (ipaddress.AddressValueError, ValueError):
        raise ValueError("Неверный IP-адрес или маска")


def check_ip_conflict(ip1: str, mask1: str, ip2: str, mask2: str) -> bool:
    """
    Проверка конфликта между двумя IP-адресами
    
    Args:
        ip1: Первый IP-адрес
        mask1: Маска первого IP
        ip2: Второй IP-адрес
        mask2: Маска второго IP
        
    Returns:
        True если есть конфликт, False иначе
    """
    try:
        network1 = ipaddress.IPv4Network(f"{ip1}/{get_prefix_length(mask1)}", strict=False)
        network2 = ipaddress.IPv4Network(f"{ip2}/{get_prefix_length(mask2)}", strict=False)
        
        return network1.overlaps(network2)
    except (ipaddress.AddressValueError, ValueError):
        return False


def format_cidr(ip: str, mask: str) -> str:
    """
    Форматирование IP и маски в формат CIDR
    
    Args:
        ip: IP-адрес
        mask: Маска подсети
        
    Returns:
        Строка в формате CIDR (например, "192.168.1.0/24")
    """
    try:
        prefix_length = get_prefix_length(mask)
        return f"{ip}/{prefix_length}"
    except ValueError:
        raise ValueError("Неверный формат маски")


def get_common_subnet(ips: List[str]) -> Optional[str]:
    """
    Поиск общей подсети для списка IP-адресов
    
    Args:
        ips: Список IP-адресов
        
    Returns:
        Общая подсеть в формате CIDR или None
    """
    if not ips:
        return None
    
    try:
        networks = []
        for ip in ips:
            # Пробуем разные маски для каждого IP
            for prefix in range(32, 0, -1):
                try:
                    network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                    if ipaddress.IPv4Address(ip) in network:
                        networks.append(network)
                        break
                except (ipaddress.AddressValueError, ValueError):
                    continue
        
        if not networks:
            return None
        
        # Находим пересечение всех сетей
        common_network = networks[0]
        for network in networks[1:]:
            if common_network.overlaps(network):
                # Находим наименьшую общую подсеть
                if network.prefixlen > common_network.prefixlen:
                    common_network = network
            else:
                return None
        
        return str(common_network)
    except Exception:
        return None


def is_private_ip(ip: str) -> bool:
    """
    Проверка является ли IP-адрес приватным
    
    Args:
        ip: IP-адрес для проверки
        
    Returns:
        True если IP приватный, False иначе
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        return ip_addr.is_private
    except ipaddress.AddressValueError:
        return False


def is_loopback_ip(ip: str) -> bool:
    """
    Проверка является ли IP-адрес loopback
    
    Args:
        ip: IP-адрес для проверки
        
    Returns:
        True если IP loopback, False иначе
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        return ip_addr.is_loopback
    except ipaddress.AddressValueError:
        return False


def is_multicast_ip(ip: str) -> bool:
    """
    Проверка является ли IP-адрес multicast
    
    Args:
        ip: IP-адрес для проверки
        
    Returns:
        True если IP multicast, False иначе
    """
    try:
        ip_addr = ipaddress.IPv4Address(ip)
        return ip_addr.is_multicast
    except ipaddress.AddressValueError:
        return False


def get_ip_type(ip: str) -> str:
    """
    Определение типа IP-адреса
    
    Args:
        ip: IP-адрес
        
    Returns:
        Тип IP-адреса: "private", "public", "loopback", "multicast", "invalid"
    """
    if not validate_ip(ip):
        return "invalid"
    
    if is_loopback_ip(ip):
        return "loopback"
    elif is_multicast_ip(ip):
        return "multicast"
    elif is_private_ip(ip):
        return "private"
    else:
        return "public" 
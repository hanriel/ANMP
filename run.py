#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication
from anmp.app.main_window import ANMPApp

def main():
    """Главная функция для запуска приложения."""
    app = QApplication(sys.argv)
    window = ANMPApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Главный файл приложения "Система управления библиотекой"
Запускает GUI приложение с использованием архитектуры MVC
"""

import os
import sys
from tkinter import messagebox

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from controllers.task_controller import TaskController as BookController
    from controllers.project_controller import ProjectController as LoanController
    from controllers.user_controller import UserController as ReaderController
    from database.database_manager import DatabaseManager
    from views.main_window import MainWindow
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все файлы проекта созданы согласно заданию")
    sys.exit(1)


def main():
    """Главная функция приложения"""
    try:
        # Инициализация базы данных
        db_manager = DatabaseManager("database/library.db")
        db_manager.create_tables()

        # Инициализация контроллеров
        book_controller = BookController(db_manager)
        reader_controller = ReaderController(db_manager)
        loan_controller = LoanController(db_manager)

        # Создание и запуск главного окна
        root = MainWindow(book_controller, reader_controller, loan_controller)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка запуска приложения: {e}")
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

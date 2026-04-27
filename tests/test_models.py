import pytest
from datetime import datetime, timedelta
from models.task import Task
from models.project import Project
from models.user import User

class TestModels:
    def test_task_creation(self):
        """Тест создания задачи"""
        срок = datetime.now() + timedelta(days=1)
        задача = Task("Тестовая задача", "Описание", 1, срок, 1, 1)
        assert задача.title == "Тестовая задача"
        assert задача.status == "pending"

    def test_task_methods(self):
        """Тест методов задачи"""
        задача = Task("Задача", "Д", 1, datetime.now() - timedelta(days=1), 1, 1)
        # Проверка статуса
        assert задача.update_status("completed") is True
        assert задача.status == "completed"
        # Проверка просрочки (завершенная не может быть просрочена)
        assert задача.is_overdue() is False
        
        задача.status = "pending"
        assert задача.is_overdue() is True

    def test_project_logic(self):
        """Тест логики проекта"""
        проект = Project("Проект", "Опис", datetime.now(), datetime.now())
        assert проект.status == "active"
        assert проект.get_progress() == 0.0
        проект.update_status("completed")
        assert проект.get_progress() == 100.0

    def test_user_logic(self):
        """Тест логики пользователя"""
        пользователь = User("иван", "ivan@mail.ru", "developer")
        assert пользователь.username == "иван"
        пользователь.update_info(username="петр")
        assert пользователь.username == "петр"
        # Валидация email
        пользователь.update_info(email="не_почта")
        assert пользователь.email == "ivan@mail.ru"

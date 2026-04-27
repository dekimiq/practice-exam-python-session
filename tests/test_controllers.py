import pytest
import tempfile
import os
from datetime import datetime, timedelta
from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController

class TestControllers:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.task_controller = TaskController(self.db_manager)
        self.project_controller = ProjectController(self.db_manager)
        self.user_controller = UserController(self.db_manager)

    def teardown_method(self):
        self.db_manager.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_user_controller(self):
        """Тест контроллера пользователей"""
        u_id = self.user_controller.add_user("админ", "admin@test.ru", "admin")
        assert u_id > 0
        user = self.user_controller.get_user(u_id)
        assert user.username == "админ"
        
        self.user_controller.update_user(u_id, username="новый_админ")
        assert self.user_controller.get_user(u_id).username == "новый_админ"

    def test_project_controller(self):
        """Тест контроллера проектов"""
        p_id = self.project_controller.add_project("Сайт", "Создание сайта", datetime.now(), datetime.now())
        assert p_id > 0
        self.project_controller.update_project_status(p_id, "completed")
        assert self.project_controller.get_project_progress(p_id) == 100.0

    def test_task_controller(self):
        """Тест контроллера задач"""
        p_id = self.project_controller.add_project("П", "Д", datetime.now(), datetime.now())
        u_id = self.user_controller.add_user("Юзер", "u@u.ru", "dev")
        
        # Будущая дата, чтобы не была просрочена сразу
        future = datetime.now() + timedelta(days=1)
        t_id = self.task_controller.add_task("Купить хлеб", "В магазине", 1, future, p_id, u_id)
        assert t_id > 0
        
        # Поиск
        results = self.task_controller.search_tasks("хлеб")
        assert len(results) == 1
        
        # Просроченные
        past = datetime.now() - timedelta(days=1)
        self.task_controller.add_task("Старая задача", "Д", 1, past, p_id, u_id)
        # 1 просрочка
        assert len(self.task_controller.get_overdue_tasks()) == 1

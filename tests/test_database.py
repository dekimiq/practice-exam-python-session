import os
import tempfile
import pytest
from datetime import datetime
from database.database_manager import DatabaseManager
from models.task import Task
from models.project import Project
from models.user import User

class TestDatabaseManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db.name)
        yield
        self.db_manager.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_user_crud(self):
        user = User("testuser", "test@example.com", "developer")
        user_id = self.db_manager.add_user(user)
        assert user_id is not None
        
        fetched_user = self.db_manager.get_user_by_id(user_id)
        assert fetched_user.username == "testuser"
        
        self.db_manager.update_user(user_id, username="updateduser")
        updated_user = self.db_manager.get_user_by_id(user_id)
        assert updated_user.username == "updateduser"
        
        all_users = self.db_manager.get_all_users()
        assert len(all_users) >= 1
        
        self.db_manager.delete_user(user_id)
        assert self.db_manager.get_user_by_id(user_id) is None

    def test_project_crud(self):
        project = Project("Тестовый проект", "Какое-то описание", datetime.now(), datetime.now())
        project_id = self.db_manager.add_project(project)
        assert project_id is not None
        
        fetched_project = self.db_manager.get_project_by_id(project_id)
        assert fetched_project.name == "Тестовый проект"
        
        self.db_manager.update_project(project_id, name="Обновленный проект")
        updated_project = self.db_manager.get_project_by_id(project_id)
        assert updated_project.name == "Обновленный проект"
        
        self.db_manager.delete_project(project_id)
        assert self.db_manager.get_project_by_id(project_id) is None

    def test_task_crud(self):
        user = User("worker", "worker@example.com", "developer")
        u_id = self.db_manager.add_user(user)
        project = Project("P1", "D1", datetime.now(), datetime.now())
        p_id = self.db_manager.add_project(project)
        
        task = Task("Задача 1", "Что-то там мутим", 1, datetime.now(), p_id, u_id)
        task_id = self.db_manager.add_task(task)
        assert task_id is not None
        
        fetched_task = self.db_manager.get_task_by_id(task_id)
        assert fetched_task.title == "Задача 1"
        
        results = self.db_manager.search_tasks("Задача")
        assert len(results) > 0
        
        p_tasks = self.db_manager.get_tasks_by_project(p_id)
        assert len(p_tasks) == 1
        
        u_tasks = self.db_manager.get_tasks_by_user(u_id)
        assert len(u_tasks) == 1
        
        self.db_manager.delete_task(task_id)
        assert self.db_manager.get_task_by_id(task_id) is None


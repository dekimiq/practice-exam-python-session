import sqlite3
from models.task import Task
from models.project import Project
from models.user import User
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="tasks.db") -> None:
        """Инициализация коннектора БД и создание таблиц."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def close(self) -> None:
        """Закрытие соединения с БД."""
        if self.conn:
            self.conn.close()

    def create_tables(self) -> None:
        """Создание таблиц если их нет"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                registration_date TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER,
                status TEXT NOT NULL,
                due_date TEXT,
                project_id INTEGER,
                assignee_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (assignee_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()


    def add_task(self, task: Task) -> int:
        """Добавить задачи в БД."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, status, due_date, project_id, assignee_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task.title, task.description, task.priority, task.status, 
              task.due_date.isoformat() if isinstance(task.due_date, datetime) else task.due_date,
              task.project_id, task.assignee_id))
        self.conn.commit()
        task.id = cursor.lastrowid
        return task.id

    def get_task_by_id(self, task_id) -> Task | None:
        """Стянуть задачу по id."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        if row:
            task = Task(row['title'], row['description'], row['priority'], 
                        row['due_date'], row['project_id'], row['assignee_id'])
            task.id = row['id']
            task.status = row['status']
            return task
        return None

    def get_all_tasks(self) -> list[Task]:
        """Получить все задачи."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = []
        for row in cursor.fetchall():
            task = Task(row['title'], row['description'], row['priority'], 
                        row['due_date'], row['project_id'], row['assignee_id'])
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)
        return tasks

    def update_task(self, task_id, **kwargs) -> bool:
        """Обновить задачу."""
        if not kwargs:
            return False
        
        keys = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values())
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(keys)} WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id) -> bool:
        """Удалить задачу по id."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def search_tasks(self, query) -> list[Task]:
        """Найти задачи по заголовку или описанию."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE title LIKE ? OR description LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        tasks = []
        for row in cursor.fetchall():
            task = Task(row['title'], row['description'], row['priority'], 
                        row['due_date'], row['project_id'], row['assignee_id'])
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)
        return tasks

    def get_tasks_by_project(self, project_id) -> list[Task]:
        """Извлечь задачи по проекту."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,))
        tasks = []
        for row in cursor.fetchall():
            task = Task(row['title'], row['description'], row['priority'], 
                        row['due_date'], row['project_id'], row['assignee_id'])
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)
        return tasks

    def get_tasks_by_user(self, user_id) -> list[Task]:
        """Извлечь задачу по пользователю."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE assignee_id = ?', (user_id,))
        tasks = []
        for row in cursor.fetchall():
            task = Task(row['title'], row['description'], row['priority'], 
                        row['due_date'], row['project_id'], row['assignee_id'])
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)
        return tasks


    def add_project(self, project: Project) -> int:
        """Добавить проект в БД."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, description, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (project.name, project.description, 
              project.start_date.isoformat() if isinstance(project.start_date, datetime) else project.start_date,
              project.end_date.isoformat() if isinstance(project.end_date, datetime) else project.end_date,
              project.status))
        self.conn.commit()
        project.id = cursor.lastrowid
        return project.id

    def get_project_by_id(self, project_id) -> Project | None:
        """Вытащить проект по id."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        if row:
            project = Project(row['name'], row['description'], row['start_date'], row['end_date'])
            project.id = row['id']
            project.status = row['status']
            return project
        return None

    def get_all_projects(self) -> list[Project]:
        """Получить все проекты."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects')
        projects = []
        for row in cursor.fetchall():
            project = Project(row['name'], row['description'], row['start_date'], row['end_date'])
            project.id = row['id']
            project.status = row['status']
            projects.append(project)
        return projects

    def update_project(self, project_id, **kwargs) -> bool:
        """Обновить атрибуты проекта."""
        if not kwargs:
            return False
        
        keys = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values())
        values.append(project_id)
        
        query = f"UPDATE projects SET {', '.join(keys)} WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_project(self, project_id) -> bool:
        """Удалить проект по id."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        self.conn.commit()
        return cursor.rowcount > 0


    def add_user(self, user: User) -> int:
        """Добавить пользователя в БД."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, role, registration_date)
            VALUES (?, ?, ?, ?)
        ''', (user.username, user.email, user.role, 
              user.registration_date.isoformat() if isinstance(user.registration_date, datetime) else user.registration_date))
        self.conn.commit()
        user.id = cursor.lastrowid
        return user.id

    def get_user_by_id(self, user_id) -> User | None:
        """Получить полльзователя по id."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            user = User(row['username'], row['email'], row['role'])
            user.id = row['id']
            user.registration_date = row['registration_date']
            return user
        return None

    def get_all_users(self) -> list[User]:
        """Получить всех пользователей."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = []
        for row in cursor.fetchall():
            user = User(row['username'], row['email'], row['role'])
            user.id = row['id']
            user.registration_date = row['registration_date']
            users.append(user)
        return users

    def update_user(self, user_id, **kwargs) -> bool:
        """Обновить атрибуты пользователя."""
        if not kwargs:
            return False
        
        keys = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values())
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(keys)} WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_user(self, user_id) -> bool:
        """Удалить полльзователя по id."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0

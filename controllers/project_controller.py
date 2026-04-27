from models.project import Project

class ProjectController:
    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager

    def add_project(self, name, description, start_date, end_date) -> int:
        """Добавить проект."""
        project = Project(name, description, start_date, end_date)
        return self.db_manager.add_project(project)

    def get_project(self, project_id) -> Project | None:
        """Получить проект."""
        return self.db_manager.get_project_by_id(project_id)

    def get_all_projects(self) -> list[Project]:
        """Получить все проекты."""
        return self.db_manager.get_all_projects()

    def update_project(self, project_id, **kwargs) -> bool:
        """Обновить проект."""
        return self.db_manager.update_project(project_id, **kwargs)

    def delete_project(self, project_id) -> bool:
        """Удалить проект."""
        return self.db_manager.delete_project(project_id)

    def update_project_status(self, project_id, new_status) -> bool:
        """Обновить статус проекта."""
        return self.db_manager.update_project(project_id, status=new_status)

    def get_project_progress(self, project_id) -> float:
        """Получить прогресс проекта."""
        project = self.get_project(project_id)
        if project:
            return project.get_progress()
        return 0.0

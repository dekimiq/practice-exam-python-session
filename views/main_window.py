import tkinter as tk
from tkinter import ttk
# Нашел не соответствие, существующие файлы названы так: task_view, project_view, user_view
# Но ожидались: book_view, reader_view, loan_view
from views.task_view import TaskView
from views.project_view import ProjectView
from views.user_view import UserView

class MainWindow(tk.Tk):
    def __init__(self, book_controller, reader_controller, loan_controller):
        super().__init__()
        self.title("Система управления задачами")
        self.geometry("1000x700")
        
        self.task_controller = book_controller
        self.user_controller = reader_controller
        self.project_controller = loan_controller
        
        self._setup_menu()
        self._setup_tabs()

    def _setup_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)

    def _setup_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.task_view = TaskView(
            self.notebook, 
            self.task_controller, 
            self.project_controller, 
            self.user_controller
        )
        self.notebook.add(self.task_view, text="Задачи")

        self.project_view = ProjectView(self.notebook, self.project_controller)
        self.notebook.add(self.project_view, text="Проекты")

        self.user_view = UserView(self.notebook, self.user_controller)
        self.notebook.add(self.user_view, text="Пользователи")
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 0:
            self.task_view.refresh_tasks()
        elif selected_tab == 1:
            self.project_view.refresh_projects()
        elif selected_tab == 2:
            self.user_view.refresh_users()

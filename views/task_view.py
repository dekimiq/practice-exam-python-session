import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TaskView(ttk.Frame):
    def __init__(self, parent, controller, project_controller, user_controller):
        super().__init__(parent)
        self.controller = controller
        self.project_controller = project_controller
        self.user_controller = user_controller
        self.selected_task_id = None
        
        self._setup_ui()
        self.refresh_tasks()

    def _setup_ui(self):
        filter_frame = ttk.LabelFrame(self, text="Поиск и фильтры")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_tasks())
        ttk.Entry(filter_frame, textvariable=self.search_var).grid(row=0, column=1, padx=5, pady=5)

        form_frame = ttk.LabelFrame(self, text="Детали задачи")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Заголовок:").grid(row=0, column=0, padx=5, pady=2)
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=2)
        self.desc_entry = ttk.Entry(form_frame)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Приоритет (1-3):").grid(row=2, column=0, padx=5, pady=2)
        self.priority_entry = ttk.Entry(form_frame)
        self.priority_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Срок (ДД.ММ.ГГГГ):").grid(row=3, column=0, padx=5, pady=2)
        self.due_date_entry = ttk.Entry(form_frame)
        self.due_date_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Проект:").grid(row=4, column=0, padx=5, pady=2)
        self.project_cb = ttk.Combobox(form_frame, state="readonly")
        self.project_cb.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Исполнитель:").grid(row=5, column=0, padx=5, pady=2)
        self.user_cb = ttk.Combobox(form_frame, state="readonly")
        self.user_cb.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить задачу", command=self.add_task).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить задачу", command=self.update_task).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить задачу", command=self.delete_task).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "title", "priority", "status", "due_date", "project", "assignee")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        column_names = {
            "id": "ID",
            "title": "Заголовок",
            "priority": "Приоритет",
            "status": "Статус",
            "due_date": "Срок",
            "project": "Проект",
            "assignee": "Исполнитель"
        }
        
        for col in columns:
            self.tree.heading(col, text=column_names[col])
            self.tree.column(col, width=100)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _format_date_for_display(self, date_val):
        if not date_val:
            return ""
        if isinstance(date_val, datetime):
            return date_val.strftime("%d.%m.%Y")
        if isinstance(date_val, str):
            try:
                clean_date = date_val.split('T')[0]
                dt = datetime.strptime(clean_date, "%Y-%m-%d")
                return dt.strftime("%d.%m.%Y")
            except ValueError:
                return date_val
        return str(date_val)

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = self.search_var.get()
        if query:
            tasks = self.controller.search_tasks(query)
        else:
            tasks = self.controller.get_all_tasks()

        for task in tasks:
            self.tree.insert("", "end", values=(
                task.id, task.title, task.priority, task.status, 
                self._format_date_for_display(task.due_date),
                task.project_id, task.assignee_id
            ))
        
        projects = self.project_controller.get_all_projects()
        self.project_cb['values'] = [f"{p.id}: {p.name}" for p in projects]
        
        users = self.user_controller.get_all_users()
        self.user_cb['values'] = [f"{u.id}: {u.username}" for u in users]

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        self.selected_task_id = values[0]
        
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, values[1])
        
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, values[2])
        
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, values[4])
        
        for i, val in enumerate(self.project_cb['values']):
            if val.startswith(f"{values[5]}:"):
                self.project_cb.current(i)
                break
        
        for i, val in enumerate(self.user_cb['values']):
            if val.startswith(f"{values[6]}:"):
                self.user_cb.current(i)
                break

    def _validate_and_get_data(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        priority_str = self.priority_entry.get().strip()
        due_date_str = self.due_date_entry.get().strip()
        project_val = self.project_cb.get()
        user_val = self.user_cb.get()

        if not all([title, priority_str, due_date_str, project_val, user_val]):
            raise ValueError("Пожалуйста, заполните все обязательные поля (Заголовок, Приоритет, Срок, Проект, Исполнитель)")

        try:
            priority = int(priority_str)
        except ValueError:
            raise ValueError("Приоритет должен быть числом (1, 2 или 3)")

        try:
            due_date = datetime.strptime(due_date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ (например, 04.05.2026)")

        project_id = int(project_val.split(":")[0])
        assignee_id = int(user_val.split(":")[0])

        return {
            "title": title,
            "description": desc,
            "priority": priority,
            "due_date": due_date,
            "project_id": project_id,
            "assignee_id": assignee_id
        }

    def add_task(self):
        try:
            data = self._validate_and_get_data()
            self.controller.add_task(**data)
            self.refresh_tasks()
            self.clear_form()
            messagebox.showinfo("Успех", "Задача успешно добавлена")
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить задачу: {str(e)}")

    def update_task(self):
        if not self.selected_task_id:
            messagebox.showwarning("Внимание", "Выберите задачу для обновления")
            return
        try:
            data = self._validate_and_get_data()
            self.controller.update_task(self.selected_task_id, **data)
            self.refresh_tasks()
            messagebox.showinfo("Успех", "Задача успешно обновлена")
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {str(e)}")

    def delete_task(self):
        if not self.selected_task_id:
            messagebox.showwarning("Внимание", "Выберите задачу для удаления")
            return
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            self.controller.delete_task(self.selected_task_id)
            self.refresh_tasks()
            self.clear_form()

    def clear_form(self):
        self.selected_task_id = None
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.project_cb.set('')
        self.user_cb.set('')

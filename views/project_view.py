import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ProjectView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_project_id = None
        
        self._setup_ui()
        self.refresh_projects()

    def _setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Детали проекта")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=2)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=2)
        self.desc_entry = ttk.Entry(form_frame)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Дата начала (ДД.ММ.ГГГГ):").grid(row=2, column=0, padx=5, pady=2)
        self.start_date_entry = ttk.Entry(form_frame)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Дата окончания (ДД.ММ.ГГГГ):").grid(row=3, column=0, padx=5, pady=2)
        self.end_date_entry = ttk.Entry(form_frame)
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить проект", command=self.add_project).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить проект", command=self.update_project).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить проект", command=self.delete_project).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "status", "progress", "start_date", "end_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        column_names = {
            "id": "ID",
            "name": "Название",
            "status": "Статус",
            "progress": "Прогресс",
            "start_date": "Начало",
            "end_date": "Конец"
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

    def refresh_projects(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        projects = self.controller.get_all_projects()
        for project in projects:
            progress = self.controller.get_project_progress(project.id)
            self.tree.insert("", "end", values=(
                project.id, project.name, project.status, f"{progress}%",
                self._format_date_for_display(project.start_date),
                self._format_date_for_display(project.end_date)
            ))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        self.selected_project_id = values[0]
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        
        project = self.controller.get_project(self.selected_project_id)
        if project:
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, project.description)
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, values[4])
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, values[5])

    def _validate_and_get_data(self):
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()

        if not all([name, start_date_str, end_date_str]):
            raise ValueError("Пожалуйста, заполните все обязательные поля (Название, Дата начала, Дата окончания)")

        try:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
            end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ (например, 04.05.2026)")

        return {
            "name": name,
            "description": desc,
            "start_date": start_date,
            "end_date": end_date
        }

    def add_project(self):
        try:
            data = self._validate_and_get_data()
            self.controller.add_project(**data)
            self.refresh_projects()
            self.clear_form()
            messagebox.showinfo("Успех", "Проект успешно добавлен")
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить проект: {str(e)}")

    def update_project(self):
        if not self.selected_project_id:
            messagebox.showwarning("Внимание", "Выберите проект для обновления")
            return
        try:
            data = self._validate_and_get_data()
            self.controller.update_project(self.selected_project_id, **data)
            self.refresh_projects()
            messagebox.showinfo("Успех", "Проект успешно обновлен")
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить проект: {str(e)}")

    def delete_project(self):
        if not self.selected_project_id:
            messagebox.showwarning("Внимание", "Выберите проект для удаления")
            return
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот проект?"):
            self.controller.delete_project(self.selected_project_id)
            self.refresh_projects()
            self.clear_form()

    def clear_form(self):
        self.selected_project_id = None
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)

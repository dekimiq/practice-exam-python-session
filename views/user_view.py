import tkinter as tk
from tkinter import ttk, messagebox

class UserView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_user_id = None
        
        self._setup_ui()
        self.refresh_users()

    def _setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Детали пользователя")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Имя пользователя:").grid(row=0, column=0, padx=5, pady=2)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=2)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(form_frame, text="Роль:").grid(row=2, column=0, padx=5, pady=2)
        self.role_cb = ttk.Combobox(form_frame, values=["admin", "manager", "developer"], state="readonly")
        self.role_cb.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить пользователя", command=self.add_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить пользователя", command=self.update_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить пользователя", command=self.delete_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "username", "email", "role", "registration_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        column_names = {
            "id": "ID",
            "username": "Имя",
            "email": "Email",
            "role": "Роль",
            "registration_date": "Дата регистрации"
        }
        
        for col in columns:
            self.tree.heading(col, text=column_names[col])
            self.tree.column(col, width=100)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def refresh_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = self.controller.get_all_users()
        for user in users:
            self.tree.insert("", "end", values=(
                user.id, user.username, user.email, user.role, user.registration_date
            ))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        self.selected_user_id = values[0]
        
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, values[1])
        
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, values[2])
        
        self.role_cb.set(values[3])

    def add_user(self):
        try:
            username = self.username_entry.get()
            email = self.email_entry.get()
            role = self.role_cb.get()
            
            self.controller.add_user(username, email, role)
            self.refresh_users()
            self.clear_form()
            messagebox.showinfo("Успех", "Пользователь успешно добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя для обновления")
            return
        try:
            data = {
                "username": self.username_entry.get(),
                "email": self.email_entry.get(),
                "role": self.role_cb.get()
            }
            self.controller.update_user(self.selected_user_id, **data)
            self.refresh_users()
            messagebox.showinfo("Успех", "Пользователь успешно обновлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя для удаления")
            return
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            self.controller.delete_user(self.selected_user_id)
            self.refresh_users()
            self.clear_form()

    def clear_form(self):
        self.selected_user_id = None
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.role_cb.set('')

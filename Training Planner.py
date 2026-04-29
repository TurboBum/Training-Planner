import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re

# Путь к файлу с данными
DATA_FILE = "trainings.json"

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("700x500")

        # Переменные для полей ввода
        self.date_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.duration_var = tk.StringVar()

        # Создание виджетов
        self.create_widgets()

        # Загрузка данных из JSON при запуске
        self.load_data()

    def create_widgets(self):
        # --- Фрейм для ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Тип тренировки (Combobox)
        ttk.Label(input_frame, text="Тип:").grid(row=1, column=0, sticky="w", pady=2)
        self.type_combobox = ttk.Combobox(
            input_frame, textvariable=self.type_var, 
            values=["Кардио", "Сила", "Растяжка", "Йога"], state="readonly"
        )
        self.type_combobox.grid(row=1, column=1, sticky="w", pady=2)

        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", pady=2)
        self.duration_entry = ttk.Entry(input_frame, textvariable=self.duration_var, width=15)
        self.duration_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training).grid(
            row=3, column=0, columnspan=2, pady=10)

        # --- Фрейм для фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        ttk.Label(filter_frame, text="По типу:").grid(row=0, column=0, sticky="w")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combobox = ttk.Combobox(
            filter_frame, textvariable=self.filter_type_var,
            values=["Все", "Кардио", "Сила", "Растяжка", "Йога"], state="readonly"
        )
        self.filter_type_combobox.current(0)  # По умолчанию "Все"
        self.filter_type_combobox.grid(row=0, column=1, sticky="w", padx=5)

        # Фильтр по дате (от)
        ttk.Label(filter_frame, text="Дата от:").grid(row=0, column=2, sticky="e")
        self.filter_date_from_var = tk.StringVar()
        self.filter_date_from_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_from_var, width=12)
        self.filter_date_from_entry.grid(row=0, column=3, sticky="w", padx=5)

         # Фильтр по дате (до)
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, sticky="e")
        self.filter_date_to_var = tk.StringVar()
        self.filter_date_to_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_to_var, width=12)
        self.filter_date_to_entry.grid(row=0, column=5, sticky="w", padx=5)

        # Кнопка фильтрации
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=6, padx=10)


        # --- Таблица для отображения тренировок ---
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)


    def add_training(self):
         date = self.date_var.get()
         tr_type = self.type_var.get()
         duration_str = self.duration_var.get()

         # Валидация даты (ГГГГ-ММ-ДД)
         if not re.match(r"\d{4}-\d{2}-\d{2}", date):
             messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например: 2026-04-29)")
             return

         # Валидация типа тренировки
         if not tr_type:
             messagebox.showerror("Ошибка", "Выберите тип тренировки")
             return

         # Валидация длительности (положительное число)
         if not duration_str.isdigit() or int(duration_str) <= 0:
             messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
             return

         duration = int(duration_str)

         # Добавление в таблицу и в список данных
         self.tree.insert("", "end", values=(date, tr_type, duration))
         
         # Очистка полей ввода
         self.date_var.set("")
         self.type_var.set("")
         self.duration_var.set("")
         
         # Сохранение данных в JSON
         self.save_data()

    def save_data(self):
         """Сохраняет все данные из таблицы в файл trainings.json"""
         data = []
         for child in self.tree.get_children():
             values = self.tree.item(child)["values"]
             data.append({
                 "date": values[0],
                 "type": values[1],
                 "duration": values[2]
             })
         
         with open(DATA_FILE, 'w', encoding='utf-8') as f:
             json.dump(data, f, ensure_ascii=False, indent=4)
    
    def load_data(self):
        """Загружает данные из файла trainings.json и заполняет таблицу"""
        self.tree.delete(*self.tree.get_children())  # Очистка таблицы перед загрузкой

        if not os.path.exists(DATA_FILE):
            return

        try:
          with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                  self.tree.insert("", "end", values=(item["date"], item["type"], item["duration"]))
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showwarning("Внимание", "Файл данных повреждён или отсутствует. Будет создан новый.")
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
    
    def apply_filter(self):
          """Фильтрует записи в таблице по выбранным параметрам"""
          filter_type = self.filter_type_var.get()
          date_from = self.filter_date_from_var.get()
          date_to = self.filter_date_to_var.get()
          
          # Валидация дат фильтра (если указаны)
          if date_from and not re.match(r"\d{4}-\d{2}-\d{2}", date_from):
              messagebox.showerror("Ошибка", "Дата 'от' должна быть в формате ГГГГ-ММ-ДД")
              return
          if date_to and not re.match(r"\d{4}-\d{2}-\d{2}", date_to):
              messagebox.showerror("Ошибка", "Дата 'до' должна быть в формате ГГГГ-ММ-ДД")
              return

          # Скрыть все записи
          for child in self.tree.get_children():
              self.tree.item(child, tags='hidden')
              self.tree.tag_configure('hidden', font=[self.tree.tag_configure('hidden'), 'gray'])
          
          # Показать подходящие записи
          for child in self.tree.get_children():
              values = self.tree.item(child)["values"]
              date_ok = True
              type_ok = True

              # Проверка по типу
              if filter_type != "Все" and values[1] != filter_type:
                  type_ok = False

              # Проверка по дате (от)
              if date_from and values[0] < date_from:
                  date_ok = False

              # Проверка по дате (до)
              if date_to and values[0] > date_to:
                  date_ok = False

              if type_ok and date_ok:
                  self.tree.item(child, tags='')  # Сброс тега 'hidden'


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()

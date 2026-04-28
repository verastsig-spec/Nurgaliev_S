import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (Личная кинотека)")
        self.root.geometry("850x600")
        self.movies = []
        self.data_file = "movies.json"

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Панель ввода ---
        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Год:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.rating_entry = ttk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=2)

        self.add_btn = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=8)

        # --- Панель фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").pack(side=tk.LEFT, padx=5)
        self.filter_genre = ttk.Entry(filter_frame, width=15)
        self.filter_genre.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Год:").pack(side=tk.LEFT, padx=5)
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # --- Таблица ---
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=250)
        self.tree.column("genre", width=120)
        self.tree.column("year", width=70, anchor=tk.CENTER)
        self.tree.column("rating", width=80, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Кнопки JSON ---
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_data).pack(side=tk.LEFT, padx=10)

    def validate_input(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        if not title or not genre:
            messagebox.showerror("Ошибка ввода", "Название и жанр не могут быть пустыми.")
            return None

        try:
            year = int(year_str)
            if not (1888 <= year <= 2099):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Год должен быть целым числом (1888–2099).")
            return None

        try:
            rating = float(rating_str)
            if not (0.0 <= rating <= 10.0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть числом от 0 до 10.")
            return None

        return {"title": title, "genre": genre, "year": year, "rating": rating}

    def add_movie(self):
        movie = self.validate_input()
        if movie:
            self.movies.append(movie)
            self.save_data()  # автосохранение
            self.update_table()
            self.clear_entries()
            messagebox.showinfo("Успех", f"Фильм «{movie['title']}» добавлен!")

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    def update_table(self, data=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        display_data = data if data is not None else self.movies
        for m in display_data:
            self.tree.insert("", tk.END, values=(m["title"], m["genre"], m["year"], m["rating"]))

    def apply_filters(self):
        genre_q = self.filter_genre.get().strip().lower()
        year_q = self.filter_year.get().strip()

        filtered = [
            m for m in self.movies
            if (not genre_q or genre_q in m["genre"].lower())
            and (not year_q or str(m["year"]) == year_q)
        ]
        self.update_table(filtered)

    def reset_filters(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.update_table()

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные сохранены в movies.json")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if not os.path.exists(self.data_file):
            self.movies = []
            self.update_table()
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.movies = json.load(f)
            self.update_table()
            messagebox.showinfo("Успех", "Данные загружены из movies.json")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка загрузки", "Файл повреждён или имеет неверный формат JSON.")
            self.movies = []
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()

import datatest as dataset
import tkinter as tk
from tkinter import ttk, colorchooser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from datetime import datetime

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class DataDrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация данных с рисованием")
        self.root.geometry("1100x800")

        self.df = dataset.df

        self.numeric_columns = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.categorical_columns = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

        self.all_columns = self.numeric_columns + self.categorical_columns

        self.selected_x = tk.StringVar(value=self.all_columns[0] if self.all_columns else "")
        self.selected_y = tk.StringVar(
            value=self.all_columns[1] if len(self.all_columns) > 1 else self.all_columns[0] if self.all_columns else "")

        self.color_scheme = tk.StringVar(value="BuGn")
        self.color_schemes = ['BuGn', 'Blues', 'Greens', 'Oranges', 'Reds', 'Purples', 'Greys', 'viridis', 'plasma',
                              'inferno', 'magma', 'cividis']

        # ID студента: 70227954
        student_id = "70227954"
        # Цвет по умолчанию из последних 6 цифр ID
        r = int(student_id[-6:-4])  # 5я и 6я с конца: 22
        g = int(student_id[-4:-2])  # 3я и 4я с конца: 79
        b = int(student_id[-2:])  # 1я и 2я с конца: 54
        self.default_pen_color = f'#{r:02x}{g:02x}{b:02x}'  # #164f36

        # Толщина линии: рекурсивная сумма ID / 2 + 5
        # 7+0+2+2+7+9+5+4 = 36
        self.default_pen_width = 36 // 2 + 5  # 23

        self.pen_color = self.default_pen_color
        self.pen_width = self.default_pen_width

        self.drawing_mode = False
        self.drawing_active = False
        self.lines_history = []
        self.current_line = []
        self.temp_line = None
        self.saved_xlim = None
        self.saved_ylim = None

        self.current_plot_type = "scatter"

        self.setup_ui()
        self.update_plot()

        print("=" * 50)
        print("НАСТРОЙКИ ПО УМОЛЧАНИЮ (из ID 70227954):")
        print(f"  Цвет кисти: RGB({r}, {g}, {b}) -> {self.default_pen_color}")
        print(f"  Толщина линии: {self.default_pen_width} пикселей")
        print("=" * 50)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.root.quit()
        self.root.destroy()
        plt.close('all')

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_frame, text="Ось X:", font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        x_canvas = tk.Canvas(left_frame, height=250, width=200)
        x_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=x_canvas.yview)
        x_scrollable_frame = ttk.Frame(x_canvas)

        x_scrollable_frame.bind("<Configure>", lambda e: x_canvas.configure(scrollregion=x_canvas.bbox("all")))
        x_canvas.create_window((0, 0), window=x_scrollable_frame, anchor="nw")
        x_canvas.configure(yscrollcommand=x_scrollbar.set)

        for col in self.all_columns:
            btn = ttk.Button(x_scrollable_frame, text=col, command=lambda c=col: self.change_x(c))
            btn.pack(fill=tk.X, pady=1)

        x_canvas.pack(side="left", fill="both", expand=True)
        x_scrollbar.pack(side="right", fill="y")

        ttk.Label(left_frame, text="Ось Y:", font=('Arial', 12, 'bold')).pack(pady=(10, 10))

        y_canvas = tk.Canvas(left_frame, height=250, width=200)
        y_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=y_canvas.yview)
        y_scrollable_frame = ttk.Frame(y_canvas)

        y_scrollable_frame.bind("<Configure>", lambda e: y_canvas.configure(scrollregion=y_canvas.bbox("all")))
        y_canvas.create_window((0, 0), window=y_scrollable_frame, anchor="nw")
        y_canvas.configure(yscrollcommand=y_scrollbar.set)

        for col in self.all_columns:
            btn = ttk.Button(y_scrollable_frame, text=col, command=lambda c=col: self.change_y(c))
            btn.pack(fill=tk.X, pady=1)

        y_canvas.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        draw_frame = ttk.LabelFrame(left_frame, text="Рисование", padding=5)
        draw_frame.pack(fill=tk.X, pady=(10, 0))

        self.draw_button = ttk.Button(draw_frame, text="✏️ Режим рисования", command=self.toggle_drawing_mode)
        self.draw_button.pack(fill=tk.X, pady=2)

        color_frame = ttk.Frame(draw_frame)
        color_frame.pack(fill=tk.X, pady=5)
        ttk.Label(color_frame, text="Цвет:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, width=8, height=1, bg=self.pen_color, command=self.choose_color)
        self.color_button.pack(side=tk.RIGHT, padx=5)

        width_frame = ttk.Frame(draw_frame)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text="Толщина:").pack(side=tk.LEFT)
        self.width_spinbox = ttk.Spinbox(width_frame, from_=1, to=50, width=8,
                                         textvariable=tk.IntVar(value=self.pen_width))
        self.width_spinbox.pack(side=tk.RIGHT, padx=5)
        self.width_spinbox.bind('<KeyRelease>', lambda e: self.update_pen_width())

        ttk.Label(draw_frame, text="Ctrl+Z - отменить линию", font=('Arial', 8)).pack(pady=2)
        ttk.Label(draw_frame, text="ПКМ - выход из режима", font=('Arial', 8)).pack(pady=1)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figure, self.ax = plt.subplots(figsize=(9, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.root.bind('<Control-z>', self.undo_last_line)
        self.root.bind('<Control-Z>', self.undo_last_line)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Label(bottom_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.x_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_x, values=self.all_columns,
                                    state="readonly", width=20)
        self.x_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.x_combo.bind('<<ComboboxSelected>>', lambda e: self.on_column_change())

        ttk.Label(bottom_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.y_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_y, values=self.all_columns,
                                    state="readonly", width=20)
        self.y_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.y_combo.bind('<<ComboboxSelected>>', lambda e: self.on_column_change())

        ttk.Label(bottom_frame, text="Цветовая схема:").pack(side=tk.LEFT, padx=(20, 5))
        self.color_combo = ttk.Combobox(bottom_frame, textvariable=self.color_scheme, values=self.color_schemes,
                                        state="readonly", width=10)
        self.color_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.color_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())

        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.pack(side=tk.RIGHT)

        self.plot_type_label = ttk.Label(bottom_frame, text="", font=('Arial', 10, 'italic'))
        self.plot_type_label.pack(side=tk.RIGHT, padx=(0, 20))

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет кисти", initialcolor=self.pen_color)
        if color_code:
            self.pen_color = color_code[1]
            self.color_button.config(bg=self.pen_color)

    def update_pen_width(self):
        try:
            self.pen_width = int(self.width_spinbox.get())
        except:
            self.pen_width = self.default_pen_width

    def toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.draw_button.config(text="✏️ Режим рисования (ВКЛ)")
            self.draw_button.state(['pressed'])
            self.canvas.get_tk_widget().config(cursor="pencil")
        else:
            self.draw_button.config(text="✏️ Режим рисования")
            self.draw_button.state(['!pressed'])
            self.canvas.get_tk_widget().config(cursor="")

    def on_column_change(self):
        if self.drawing_mode:
            self.drawing_mode = False
            self.draw_button.config(text="✏️ Режим рисования")
            self.draw_button.state(['!pressed'])
            self.canvas.get_tk_widget().config(cursor="")
        self.update_plot()

    def change_x(self, col):
        self.selected_x.set(col)
        self.on_column_change()

    def change_y(self, col):
        self.selected_y.set(col)
        self.on_column_change()

    def save_limits(self):
        """Сохраняет текущие пределы осей"""
        self.saved_xlim = self.ax.get_xlim()
        self.saved_ylim = self.ax.get_ylim()

    def restore_limits(self):
        """Восстанавливает сохранённые пределы осей"""
        if self.saved_xlim is not None and self.saved_ylim is not None:
            self.ax.set_xlim(self.saved_xlim)
            self.ax.set_ylim(self.saved_ylim)

    def on_press(self, event):
        if not self.drawing_mode:
            return
        if event.inaxes != self.ax:
            return
        if event.button == 1:
            self.drawing_active = True
            self.current_line = [(event.xdata, event.ydata)]
            # Сохраняем текущие пределы осей
            self.save_limits()
            self.draw_point(event.xdata, event.ydata)
        elif event.button == 3:
            if self.drawing_mode:
                self.toggle_drawing_mode()

    def on_motion(self, event):
        if not self.drawing_mode or not self.drawing_active:
            return
        if event.inaxes != self.ax:
            return
        if self.current_line:
            # Удаляем предыдущую временную линию
            if self.temp_line:
                try:
                    self.temp_line.pop(0).remove()
                    self.temp_line = None
                except:
                    pass

            last_x, last_y = self.current_line[-1]
            self.temp_line = self.ax.plot([last_x, event.xdata], [last_y, event.ydata],
                                          color=self.pen_color, linewidth=self.pen_width,
                                          solid_capstyle='round')
            self.current_line.append((event.xdata, event.ydata))
            # Восстанавливаем пределы осей после каждого обновления
            self.restore_limits()
            self.canvas.draw_idle()

    def draw_point(self, x, y):
        half = self.pen_width / 2
        rect = plt.Rectangle((x - half, y - half), self.pen_width, self.pen_width,
                             facecolor=self.pen_color, edgecolor=self.pen_color, alpha=0.8)
        self.ax.add_patch(rect)
        self.restore_limits()
        self.canvas.draw_idle()

    def on_release(self, event):
        if not self.drawing_mode or not self.drawing_active:
            return
        if event.button == 1:
            # Удаляем временную линию
            if self.temp_line:
                try:
                    self.temp_line.pop(0).remove()
                    self.temp_line = None
                except:
                    pass

            # Сохраняем постоянную линию, если есть что сохранять
            if len(self.current_line) > 1:
                xs, ys = zip(*self.current_line)
                self.ax.plot(xs, ys, color=self.pen_color, linewidth=self.pen_width,
                             solid_capstyle='round')
                self.lines_history.append(self.current_line.copy())
                # Восстанавливаем пределы осей
                self.restore_limits()
                self.canvas.draw_idle()

        self.drawing_active = False
        self.current_line = []

    def undo_last_line(self, event=None):
        if self.drawing_active:
            return
        if not self.lines_history:
            return
        self.lines_history.pop()
        self.redraw_with_lines()

    def redraw_with_lines(self):
        self.update_plot()
        for line in self.lines_history:
            if len(line) > 1:
                xs, ys = zip(*line)
                self.ax.plot(xs, ys, color=self.pen_color, linewidth=self.pen_width,
                             solid_capstyle='round')
        self.restore_limits()
        self.canvas.draw_idle()

    def determine_plot_type(self):
        x_col = self.selected_x.get()
        y_col = self.selected_y.get()

        x_is_numeric = x_col in self.numeric_columns
        y_is_numeric = y_col in self.numeric_columns

        if x_col == y_col:
            if x_is_numeric:
                return "histogram"
            else:
                return "pie"
        elif not x_is_numeric and y_is_numeric:
            return "bar"
        elif x_is_numeric and not y_is_numeric:
            return "boxplot"
        else:
            return "scatter"

    def get_cmap(self):
        scheme = self.color_scheme.get()
        try:
            return plt.colormaps[scheme]
        except:
            return plt.colormaps['BuGn']

    def get_single_color(self):
        scheme = self.color_scheme.get()
        if scheme in ['BuGn', 'Blues', 'Greens', 'Oranges', 'Reds', 'Purples', 'Greys']:
            cmap = plt.colormaps[scheme]
            return cmap(0.7)
        else:
            return 'steelblue'

    def update_plot(self):
        self.ax.clear()

        x_col = self.selected_x.get()
        y_col = self.selected_y.get()

        self.current_plot_type = self.determine_plot_type()

        plot_names = {
            "scatter": "Точечная диаграмма",
            "histogram": "Гистограмма",
            "pie": "Круговая диаграмма",
            "bar": "Столбчатая диаграмма",
            "boxplot": "Коробочная диаграмма"
        }
        self.plot_type_label.config(text=f"Тип: {plot_names[self.current_plot_type]}")

        if self.current_plot_type == "scatter":
            self.plot_scatter(x_col, y_col)
        elif self.current_plot_type == "histogram":
            self.plot_histogram(x_col)
        elif self.current_plot_type == "pie":
            self.plot_pie(x_col)
        elif self.current_plot_type == "bar":
            self.plot_bar(x_col)
        elif self.current_plot_type == "boxplot":
            self.plot_boxplot(x_col, y_col)

        # Сохраняем пределы осей после построения графика
        self.save_limits()
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_scatter(self, x_col, y_col):
        x_data = self.df[x_col].dropna()
        y_data = self.df.loc[x_data.index, y_col].dropna()
        common_idx = x_data.index.intersection(y_data.index)

        color = self.get_single_color()

        self.ax.scatter(x_data[common_idx], y_data[common_idx], marker='<', color=color, alpha=0.6, s=80,
                        edgecolors='darkblue', linewidth=0.5)
        self.ax.set_xlabel(x_col, fontsize=12)
        self.ax.set_ylabel(y_col, fontsize=12)
        self.ax.set_title(f'Точечная диаграмма: {x_col} vs {y_col}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

    def plot_histogram(self, col):
        data = self.df[col].dropna()
        cmap = self.get_cmap()

        counts, bins, patches = self.ax.hist(data, bins=10, edgecolor='black', alpha=0.7)

        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / 10))

        self.ax.set_xlabel(col, fontsize=12)
        self.ax.set_ylabel('Частота', fontsize=12)
        self.ax.set_title(f'Гистограмма: {col} (10 интервалов)', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, axis='y')

    def plot_pie(self, col):
        data = self.df[col].dropna()
        value_counts = data.value_counts()

        if len(value_counts) > 10:
            top = value_counts.head(9)
            other = pd.Series([value_counts[9:].sum()], index=['Другие'])
            value_counts = pd.concat([top, other])

        cmap = self.get_cmap()
        colors = [cmap(i / len(value_counts)) for i in range(len(value_counts))]

        self.ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%',
                    colors=colors, startangle=90, textprops={'fontsize': 10})
        self.ax.set_title(f'Круговая диаграмма: {col}', fontsize=14, fontweight='bold')
        self.ax.axis('equal')

    def plot_bar(self, cat_col):
        data = self.df[cat_col].dropna()
        value_counts = data.value_counts()

        cmap = self.get_cmap()
        colors = [cmap(i / len(value_counts)) for i in range(len(value_counts))]

        bars = self.ax.bar(range(len(value_counts)), value_counts.values,
                           color=colors, edgecolor='black', alpha=0.7)
        self.ax.set_xticks(range(len(value_counts)))
        self.ax.set_xticklabels(value_counts.index, rotation=45, ha='right', fontsize=9)
        self.ax.set_xlabel(cat_col, fontsize=12)
        self.ax.set_ylabel('Количество', fontsize=12)
        self.ax.set_title(f'Столбчатая диаграмма: {cat_col}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3, axis='y')

    def plot_boxplot(self, num_col, cat_col):
        data = self.df[[num_col, cat_col]].dropna()

        categories = data[cat_col].unique()
        categories = [c for c in categories if pd.notna(c)]

        box_data = []
        for cat in categories:
            values = data[data[cat_col] == cat][num_col].dropna()
            if len(values) > 0:
                box_data.append(values)

        if len(categories) > 10:
            top_cats = data[cat_col].value_counts().head(10).index
            box_data = []
            categories = []
            for cat in top_cats:
                values = data[data[cat_col] == cat][num_col].dropna()
                if len(values) > 0:
                    box_data.append(values)
                    categories.append(cat)

        bp = self.ax.boxplot(box_data, tick_labels=categories, patch_artist=True)

        cmap = self.get_cmap()
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(cmap(i / len(box_data)))
            patch.set_alpha(0.7)

        self.ax.set_xlabel(cat_col, fontsize=12)
        self.ax.set_ylabel(num_col, fontsize=12)
        self.ax.set_title(f'Коробочная диаграмма: {num_col} по категориям {cat_col}', fontsize=14, fontweight='bold')
        self.ax.tick_params(axis='x', rotation=45, labelsize=9)
        self.ax.grid(True, alpha=0.3, axis='y')

    def save_plot(self):
        now = datetime.now()
        filename = f"graph{now.hour:02d}_{now.minute:02d}_{now.second:02d}.png"
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"График сохранён: {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataDrawApp(root)
    root.mainloop()

import datatest as dataset
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from datetime import datetime

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class DataVisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация данных")
        self.root.geometry("1000x750")

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

        self.current_plot_type = "scatter"

        self.setup_ui()
        self.update_plot()

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

        x_canvas = tk.Canvas(left_frame, height=300, width=200)
        x_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=x_canvas.yview)
        x_scrollable_frame = ttk.Frame(x_canvas)

        x_scrollable_frame.bind("<Configure>", lambda e: x_canvas.configure(scrollregion=x_canvas.bbox("all")))
        x_canvas.create_window((0, 0), window=x_scrollable_frame, anchor="nw")
        x_canvas.configure(yscrollcommand=x_scrollbar.set)

        for col in self.all_columns:
            btn = ttk.Button(x_scrollable_frame, text=col, command=lambda c=col: self.change_x(c))
            btn.pack(fill=tk.X, pady=2)

        x_canvas.pack(side="left", fill="both", expand=True)
        x_scrollbar.pack(side="right", fill="y")

        ttk.Label(left_frame, text="Ось Y:", font=('Arial', 12, 'bold')).pack(pady=(10, 10))

        y_canvas = tk.Canvas(left_frame, height=300, width=200)
        y_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=y_canvas.yview)
        y_scrollable_frame = ttk.Frame(y_canvas)

        y_scrollable_frame.bind("<Configure>", lambda e: y_canvas.configure(scrollregion=y_canvas.bbox("all")))
        y_canvas.create_window((0, 0), window=y_scrollable_frame, anchor="nw")
        y_canvas.configure(yscrollcommand=y_scrollbar.set)

        for col in self.all_columns:
            btn = ttk.Button(y_scrollable_frame, text=col, command=lambda c=col: self.change_y(c))
            btn.pack(fill=tk.X, pady=2)

        y_canvas.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figure, self.ax = plt.subplots(figsize=(9, 7))
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Label(bottom_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.x_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_x, values=self.all_columns,
                                    state="readonly", width=20)
        self.x_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.x_combo.bind('<<ComboboxSelected>>', lambda e: self.change_x(self.selected_x.get()))

        ttk.Label(bottom_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.y_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_y, values=self.all_columns,
                                    state="readonly", width=20)
        self.y_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.y_combo.bind('<<ComboboxSelected>>', lambda e: self.change_y(self.selected_y.get()))

        ttk.Label(bottom_frame, text="Цветовая схема:").pack(side=tk.LEFT, padx=(20, 5))
        self.color_combo = ttk.Combobox(bottom_frame, textvariable=self.color_scheme, values=self.color_schemes,
                                        state="readonly", width=10)
        self.color_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.color_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())

        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.pack(side=tk.RIGHT)

        self.plot_type_label = ttk.Label(bottom_frame, text="", font=('Arial', 10, 'italic'))
        self.plot_type_label.pack(side=tk.RIGHT, padx=(0, 20))

    def change_x(self, col):
        self.selected_x.set(col)
        self.update_plot()

    def change_y(self, col):
        self.selected_y.set(col)
        self.update_plot()

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

        self.figure.tight_layout()
        self.canvas.draw()

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
    app = DataVisualApp(root)
    root.mainloop()

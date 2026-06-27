import datatest as dataset
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class ScatterPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Точечная диаграмма")
        self.root.geometry("900x700")

        self.df = dataset.df
        self.numeric_columns = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        self.selected_x = tk.StringVar(value=self.numeric_columns[0] if self.numeric_columns else "")
        self.selected_y = tk.StringVar(
            value=self.numeric_columns[1] if len(self.numeric_columns) > 1 else self.numeric_columns[
                0] if self.numeric_columns else "")

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

        for col in self.numeric_columns:
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

        for col in self.numeric_columns:
            btn = ttk.Button(y_scrollable_frame, text=col, command=lambda c=col: self.change_y(c))
            btn.pack(fill=tk.X, pady=2)

        y_canvas.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Label(bottom_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.x_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_x, values=self.numeric_columns,
                                    state="readonly", width=20)
        self.x_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.x_combo.bind('<<ComboboxSelected>>', lambda e: self.change_x(self.selected_x.get()))

        ttk.Label(bottom_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.y_combo = ttk.Combobox(bottom_frame, textvariable=self.selected_y, values=self.numeric_columns,
                                    state="readonly", width=20)
        self.y_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.y_combo.bind('<<ComboboxSelected>>', lambda e: self.change_y(self.selected_y.get()))

        save_btn = ttk.Button(bottom_frame, text="Сохранить график", command=self.save_plot)
        save_btn.pack(side=tk.RIGHT)

    def change_x(self, col):
        self.selected_x.set(col)
        self.update_plot()

    def change_y(self, col):
        self.selected_y.set(col)
        self.update_plot()

    def update_plot(self):
        if not self.numeric_columns:
            return

        self.ax.clear()

        x_col = self.selected_x.get()
        y_col = self.selected_y.get()

        x_data = self.df[x_col].dropna()
        y_data = self.df.loc[x_data.index, y_col].dropna()
        common_idx = x_data.index.intersection(y_data.index)

        self.ax.scatter(x_data[common_idx], y_data[common_idx], marker='<', color='blue', alpha=0.6, s=80,
                        edgecolors='darkblue', linewidth=0.5)
        self.ax.set_xlabel(x_col, fontsize=12)
        self.ax.set_ylabel(y_col, fontsize=12)
        self.ax.set_title(f'Точечная диаграмма: {x_col} vs {y_col}', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()

    def save_plot(self):
        now = datetime.now()
        filename = f"graph{now.hour:02d}_{now.minute:02d}_{now.second:02d}.png"
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"График сохранён: {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScatterPlotApp(root)
    root.mainloop()

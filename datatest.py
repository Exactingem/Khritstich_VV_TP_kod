import pandas as pd
import os
from io import StringIO

df = None


def load_dataset():
    global df
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'dataset.csv')
    df = pd.read_csv(file_path, index_col=0)


def save_and_print(text, file_handle):
    print(text)
    file_handle.write(text + '\n')


def analyze_dataset():
    global df

    if df is None:
        print("Датасет не загружен")
        return

    with open('report.txt', 'w', encoding='utf-8') as f:
        save_and_print(f"Размер датасета: {df.shape}", f)
        save_and_print("", f)

        save_and_print("Информация о типах данных:", f)
        buffer = StringIO()
        df.info(buf=buffer)
        save_and_print(buffer.getvalue(), f)
        save_and_print("", f)

        save_and_print("Количество пропущенных значений в каждой колонке:", f)
        for col in df.columns:
            save_and_print(f"{col}: {df[col].isnull().sum()}", f)
        save_and_print("", f)

        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        save_and_print("Статистика для числовых колонок (среднее, медиана, стандартное отклонение):", f)
        save_and_print("Колонка>\tсреднее\tмедиана\tотклонение", f)
        for col in numeric_cols:
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            save_and_print(f"{col}>\t{mean_val:.2f};\t{median_val:.2f};\t{std_val:.2f}", f)
        save_and_print("", f)

        cat_cols = df.select_dtypes(include=['object']).columns
        save_and_print("Статистика для категориальных колонок (уникальные значения и частота):", f)
        for col in cat_cols:
            save_and_print(f"\n{col}:", f)
            for value, count in df[col].value_counts().items():
                save_and_print(f"  {value}: {count}", f)


load_dataset()

if __name__ == "__main__":
    if df is not None:
        analyze_dataset()
        print("Анализ завершён. Результаты сохранены в report.txt")
    else:
        print("Не удалось загрузить датасет")

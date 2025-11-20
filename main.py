# Импортируем необходимые библиотеки
import streamlit as st  # для создания веб-приложения
import pandas as pd  # для работы с таблицами (DataFrame)
import yfinance as yf  # для загрузки котировок акций
import matplotlib.pyplot as plt  # для построения графиков
import plotly.graph_objects as go  # для интерактивных графиков Plotly
from io import BytesIO  # для создания буфера памяти (скачивание графиков)

# Заголовок приложения
st.title("Учебное приложение Streamlit")
st.sidebar.header("Меню")  # заголовок боковой панели

# Выбор раздела через боковую панель
page = st.sidebar.selectbox(
    "Выберите раздел", ["Котировки Apple", "Tips.csv", "Загрузка CSV"]
)

# Раздел 1 — котировки Apple
if page == "Котировки Apple":
    st.header("Котировки Apple (AAPL)")

    # Выбор периода
    period = st.sidebar.selectbox("Период", ["1mo", "3mo", "6mo", "1y"])

    # Загрузка данных
    data = yf.download("AAPL", period=period)

    st.write("Таблица данных")
    st.dataframe(data.head(10))

    st.write("График цены закрытия (matplotlib, без st.pyplot)")

    # Создаём matplotlib-график
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data["Close"], color="red")
    ax.set_title("Котировки Apple — Цена закрытия")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Цена закрытия")
    ax.grid(True)

    # Сохраняем график в буфер памяти
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    buf.seek(0)

    # Выводим как изображение
    st.image(
        buf, caption="Линейный график цены закрытия AAPL", use_container_width=True
    )

    # Кнопка скачивания
    st.download_button(
        label="Скачать график", data=buf, file_name="apple.png", mime="image/png"
    )


# Раздел 2 и 3 — Tips.csv и Загрузка CSV
elif page in ["Tips.csv", "Загрузка CSV"]:
    st.header("Анализ датасета")  # заголовок раздела

    # Загрузка датасета
    if page == "Tips.csv":
        # если выбран Tips.csv, скачиваем готовый датасет
        df = pd.read_csv(
            "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
        )
    else:
        # если пользователь загружает свой CSV
        uploaded_file = st.sidebar.file_uploader("Загрузите свой CSV файл", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)  # читаем CSV в DataFrame
        else:
            st.info(
                "Пожалуйста, загрузите CSV файл."
            )  # сообщение, если файл не загружен
            st.stop()  # останавливаем выполнение, чтобы не было ошибок

    # Показываем первые строки датасета
    st.write("Первые строки датасета:")
    st.dataframe(df.head())

    # Выбор переменных для графика через боковую панель
    choice_x = st.sidebar.selectbox("Выберите X переменную", options=df.columns)
    choice_y = st.sidebar.selectbox(
        "Выберите Y переменную (если есть)", options=[None] + list(df.columns)
    )

    # Создаем график
    fig, ax = plt.subplots(figsize=(8, 5))

    if choice_y is None:
        # Если выбрана только одна переменная
        if pd.api.types.is_numeric_dtype(df[choice_x]):
            # Числовая переменная — строим гистограмму
            ax.hist(df[choice_x], bins=10, color="skyblue", edgecolor="black")
            ax.set_xlabel(choice_x)
            ax.set_ylabel("Количество")
            ax.set_title(f"Гистограмма {choice_x}")
        else:
            # Категориальная переменная — строим столбчатую диаграмму
            df[choice_x].value_counts().plot(kind="bar", color="skyblue", ax=ax)
            ax.set_xlabel(choice_x)
            ax.set_ylabel("Количество")
            ax.set_title(f"Столбчатая диаграмма {choice_x}")
    else:
        # Если выбраны две переменные
        if pd.api.types.is_numeric_dtype(
            df[choice_x]
        ) and pd.api.types.is_numeric_dtype(df[choice_y]):
            # Обе числовые — scatter plot
            ax.scatter(df[choice_x], df[choice_y], color="red")
            ax.set_xlabel(choice_x)
            ax.set_ylabel(choice_y)
            ax.set_title(f"Точечный график {choice_x} vs {choice_y}")
        elif pd.api.types.is_numeric_dtype(df[choice_y]):
            # X категориальный, Y числовой — barplot средних
            grouped = df.groupby(choice_x)[choice_y].mean()  # среднее Y по категориям X
            grouped.plot(kind="bar", color="skyblue", ax=ax)
            ax.set_xlabel(choice_x)
            ax.set_ylabel(f"Среднее {choice_y}")
            ax.set_title(f"Среднее {choice_y} по {choice_x}")
        else:
            # Если обе переменные категориальные или Y не числовой
            st.warning(
                f"Невозможно построить график для выбранных колонок: {choice_x}, {choice_y}"
            )

    # Отображение графика на странице
    st.pyplot(fig)

    # Кнопка для скачивания графика
    buffer = BytesIO()  # создаем буфер в памяти
    fig.savefig(buffer, format="png")  # сохраняем график в PNG
    buffer.seek(0)  # возвращаем курсор в начало буфера
    st.sidebar.download_button(
        "Скачать график", data=buffer, file_name="graph.png", mime="image/png"
    )

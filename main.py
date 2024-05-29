import random
import streamlit as st
import matplotlib.pyplot as plt
import json
import os

# Функция для отрисовки полигона по заданным вершинам
def draw_polygon(vertices, interior_walls, length, width):
    fig, ax = plt.subplots()
    polygon = plt.Polygon(vertices, closed=True, fill=False, linewidth=2)
    ax.add_patch(polygon)

    for wall in interior_walls:
        x1, y1, x2, y2 = wall['x1'], wall['y1'], wall['x2'], wall['y2']
        ax.plot([x1, x2], [y1, y2], color='red', linewidth=2)

    # Настраиваем пределы осей согласно размерам участка
    ax.set_xlim([0, length])
    ax.set_ylim([0, width])

    # Устанавливаем одинаковый масштаб для обеих осей
    ax.set_aspect('equal')

    # Дополнительная настройка графика
    plt.tight_layout()
    plt.close()
    return fig

def will_fit(vertices, length, width):
    # Вычисление координат ограничивающего прямоугольника
    x_coordinates = [vertex['x'] for vertex in vertices]
    y_coordinates = y_coordinates = [vertex.get('y', 0) for vertex in vertices]

    min_x = min(x_coordinates)
    max_x = max(x_coordinates)
    min_y = min(y_coordinates)
    max_y = max(y_coordinates)

    # Вычисление ширины и длины ограничивающего прямоугольника
    bounding_box_length = max_x - min_x
    bounding_box_width = max_y - min_y

    # Сравнение размеров ограничивающего прямоугольника с заданными размерами
    if (bounding_box_length <= length and bounding_box_width <= width) or (bounding_box_length <= width and bounding_box_width <= length):
        return True
    else:
        return False


def move_section_to_origin(vertices, interior_walls):
    # Находим минимальные x и y среди всех вершин
    min_x = min(vertex['x'] for vertex in vertices)
    min_y = min(vertex['y'] for vertex in vertices)

    # Сдвиг всех вершин
    new_vertices = [
        {'x': vertex['x'] - min_x, 'y': vertex['y'] - min_y}
        for vertex in vertices
    ]

    # Находим максимальные x и y среди всех вершин
    max_x = max(vertex['x'] for vertex in new_vertices)
    max_y = max(vertex['y'] for vertex in new_vertices)


    # Сдвиг всех внутренних стен
    new_interior_walls = [
        {'x1': wall['x1'] - min_x, 'y1': wall['y1'] - min_y,
         'x2': wall['x2'] - min_x, 'y2': wall['y2'] - min_y}
        for wall in interior_walls
    ]

    return new_vertices, new_interior_walls, max_x, max_y
def new_section(max_length, max_width):
    sections = data['sections']

    # Фильтруем секции, чтобы найти только те, которые подходят по размеру
    suitable_sections = [section for section in sections if will_fit(section['vertices'], max_length, max_width)]

    # Если есть хотя бы одна подходящая секция, выбираем из них случайную
    if suitable_sections:
        section = random.choice(suitable_sections)
        vertices = section['vertices']
    else:
        # Обрабатываем ситуацию, когда нет подходящих секций
        st.write("Нет секций, удовлетворяющих заданным размерам.")
        return None

    st.write(section['building'] + '. Секция: ' + str(section['number']))

    new_vertices, new_interior_walls, max_x, max_y = move_section_to_origin(section['vertices'], section['interior_walls'])

    # Преобразование каждого элемента массива в кортеж
    converted_vertices = [tuple(vertex.values()) for vertex in new_vertices]

    if max_x > length:
        image = draw_polygon(converted_vertices, new_interior_walls, max_width, max_length)
    else:
        image = draw_polygon(converted_vertices, new_interior_walls, max_length, max_width)

    st.pyplot(image)

st.header('Размеры пятна застройки')

# Устанавливаем случайные значения по умолчанию с округлением до двух знаков после запятой
if 'length' not in st.session_state:
    st.session_state['length'] = round(random.uniform(10.0, 100.0), 2)

if 'width' not in st.session_state:
    st.session_state['width'] = round(random.uniform(10.0, 100.0), 2)

# Виджеты для ввода длины и ширины участка с использованием сохраненных значений
# Формат '%.2f' обеспечивает вывод с точностью до двух знаков после запятой
length = st.number_input('Длина (м):', min_value=0.0, format='%.2f', value=st.session_state['length'])
width = st.number_input('Ширина (м):', min_value=0.0, format='%.2f', value=st.session_state['width'])

# Устанавливаем ключи для различения виджетов ввода
keys = ['one', 'two', 'three', 'studio']

st.header('Целевое распределение')

# Инициализация значений, если они ещё не установлены
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 25.0  # начальное распределение

# Функция-обработчик изменения значений, которая обновляет поля ввода
def on_change():
    total = 100.0
    # Вычисляем сумму всех полей кроме последнего
    current_total = sum(st.session_state[key] for key in keys[:-1])
    # Обновляем последнее поле значением оставшегося процента
    st.session_state[keys[-1]] = total - current_total

# Сгруппируем виджеты в строку
cols = st.columns(4)  # Создаем 4 колонки

with cols[0]:
    st.number_input('Однокомнатные (в %)', min_value=0.0, max_value=100.0, key=keys[0], on_change=on_change)
with cols[1]:
    st.number_input('Двухкомнатные (в %)', min_value=0.0, max_value=100.0, key=keys[1], on_change=on_change)
with cols[2]:
    st.number_input('Трехкомнатные (в %)', min_value=0.0, max_value=100.0, key=keys[2], on_change=on_change)
with cols[3]:
    st.number_input('Студии (в %)', min_value=0.0, max_value=100.0, key=keys[3], disabled=True)

# Путь к файлу sections.json
file_path = "sections.json"

# Проверьте, существует ли файл
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Преобразуйте содержимое файла в массив
        data = json.load(f)
        new_section(length, width)
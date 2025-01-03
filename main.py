from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


# Создание и подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        order_amount INTEGER
    )
    ''')
    cursor.executemany('''
    INSERT INTO Orders (order_id, customer_name, order_amount)
    VALUES (?, ?, ?)
    ''', [
        (1, 'Alice', 150),
        (2, 'Bob', 200),
        (3, 'Alice', 300),
        (4, 'Bob', 400),
        (5, 'Alice', 500),
        (6, 'Alice', 600),
        (7, 'Bob', 700),
        (8, 'Charlie', 800),
        (9, 'Charlie', 900),
    ])

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY,
        category TEXT,
        price INTEGER
    )
    ''')

    cursor.executemany('''
    INSERT INTO Products (product_id, category, price)
    VALUES (?, ?, ?)
    ''', [
        (1, 'Electronics', 500),
        (2, 'Electronics', 700),
        (3, 'Electronics', 700),
        (4, 'Furniture', 1000),
        (5, 'Furniture', 1500),
        (6, 'Furniture', 1500),
        (7, 'Clothing', 200),
        (8, 'Clothing', 300),
        (9, 'Clothing', 300)
    ])

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY,
        subject TEXT,
        score INTEGER
    )
    ''')

    cursor.executemany('''
    INSERT INTO Students (student_id, subject, score)
    VALUES (?, ?, ?)
    ''', [
        (1, 'Math', 95),
        (2, 'Math', 90),
        (3, 'Math', 90),
        (4, 'Math', 85),
        (5, 'Science', 80),
        (6, 'Science', 90),
        (7, 'Science', 90),
        (8, 'History', 70),
        (9, 'History', 70),
        (10, 'History', 60)
    ])

    conn.commit()
    return conn


# Эталонные SQL-запросы
correct_query_1 = """
SELECT customer_name, order_id, order_amount
FROM (
    SELECT customer_name, order_id, order_amount,
           ROW_NUMBER() OVER (PARTITION BY customer_name ORDER BY order_amount DESC) as row_num
    FROM Orders
) WHERE row_num <= 3;
"""

correct_query_2 = """
SELECT category, product_id, price
FROM (
    SELECT category, product_id, price,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY price ASC) as dense_rank
    FROM Products
) WHERE dense_rank <= 2;
"""

correct_query_3 = """
SELECT subject, student_id, score, rank
FROM (
    SELECT subject, student_id, score,
           RANK() OVER (PARTITION BY subject ORDER BY score DESC) as rank
    FROM Students
) ORDER BY subject, rank;
"""


# Главная страница с формами ввода
@app.route('/')
def index():
    return render_template('index.html')


# Обработка запросов
@app.route('/execute', methods=['POST'])
def execute():
    query = request.form['query']
    task_number = request.form['task']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if task_number == '1':
            cursor.execute(correct_query_1)
            correct_results = cursor.fetchall()
            return jsonify({'results': results, 'correct': correct_results})

        elif task_number == '2':
            cursor.execute(correct_query_2)
            correct_results = cursor.fetchall()
            return jsonify({'results': results, 'correct': correct_results})

        elif task_number == '3':
            cursor.execute(correct_query_3)
            correct_results = cursor.fetchall()
            return jsonify({'results': results, 'correct': correct_results})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

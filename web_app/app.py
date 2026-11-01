from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from database import DatabaseConnection
from reports import generate_movies_report
from charts import create_person_statistics_chart, create_budget_distribution_chart
from api import setup_api_routes
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Підключення до бази даних у Docker контейнері
db = DatabaseConnection(
    dbname='movies',
    user='postgres',
    password='password',
    host='localhost',
    port=5432
)
db.connect()

# Підключаємо REST API ендпоінти з api.py
setup_api_routes(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies')
def movies():
    query = """
        SELECT movie_id, title, release_year, duration_minutes, rating, budget
        FROM movies
        ORDER BY title
    """
    cursor = db.execute_query(query)
    movies_list = cursor.fetchall() if cursor else []
    return render_template('movies.html', movies=movies_list)

@app.route('/movies/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        year = int(request.form['year'])
        duration = int(request.form['duration'])
        rating = float(request.form['rating'])
        budget = float(request.form['budget'])

        query = """
            INSERT INTO movies (title, release_year, duration_minutes, rating, budget)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING movie_id
        """
        cursor = db.execute_query(query, (title, year, duration, rating, budget))

        if cursor:
            movie_id = cursor.fetchone()[0]
            # Логуємо дію у таблицю аутентифікації/аудиту (наприклад, під admin_id = 1)
            log_query = "SELECT log_activity(1, 'CREATE', 'movies', %s, 'Додано новий фільм через веб')"
            db.execute_query(log_query, (movie_id,))

            flash('Фільм успішно додано!', 'success')
            return redirect(url_for('movies'))
        else:
            flash('Помилка додавання фільму', 'error')

    return render_template('add_movie.html')

@app.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if request.method == 'POST':
        title = request.form['title']
        rating = float(request.form['rating'])
        budget = float(request.form['budget'])

        query = "UPDATE movies SET title = %s, rating = %s, budget = %s WHERE movie_id = %s"
        cursor = db.execute_query(query, (title, rating, budget, movie_id))

        if cursor:
            # Логуємо оновлення
            db.execute_query("SELECT log_activity(1, 'UPDATE', 'movies', %s, 'Оновлено дані фільму')", (movie_id,))
            flash('Фільм успішно оновлено!', 'success')
            return redirect(url_for('movies'))
        else:
            flash('Помилка оновлення фільму', 'error')

    query = "SELECT * FROM movies WHERE movie_id = %s"
    cursor = db.execute_query(query, (movie_id,))
    movie = cursor.fetchone() if cursor else None

    return render_template('edit_movie.html', movie=movie)

@app.route('/movies/delete/<int:movie_id>')
def delete_movie(movie_id):
    query = "DELETE FROM movies WHERE movie_id = %s"
    cursor = db.execute_query(query, (movie_id,))

    if cursor:
        db.execute_query("SELECT log_activity(1, 'DELETE', 'movies', %s, 'Видалено фільм')", (movie_id,))
        flash('Фільм успішно видалено!', 'success')
    else:
        flash('Помилка видалення фільму', 'error')

    return redirect(url_for('movies'))

@app.route('/authors')
def authors():
    query = "SELECT * FROM person_statistics ORDER BY total_movies DESC"
    cursor = db.execute_query(query)
    authors_list = cursor.fetchall() if cursor else []
    return render_template('authors.html', authors=authors_list)

# --- НОВІ МАРШРУТИ ДЛЯ РІВНЯ 3 ---

@app.route('/analytics')
def analytics():
    """Сторінка з графіками (charts.py)"""
    chart1 = create_person_statistics_chart(db)
    chart2 = create_budget_distribution_chart(db)
    return render_template('analytics.html', chart1=chart1, chart2=chart2)

@app.route('/report/pdf')
def download_pdf_report():
    """Маршрут для завантаження PDF-звіту (reports.py)"""
    query = "SELECT movie_id, title, release_year, duration_minutes, rating, budget FROM movies ORDER BY title"
    cursor = db.execute_query(query)
    movies_list = cursor.fetchall() if cursor else []
    
    report_path = generate_movies_report(movies_list)
    return send_file(report_path, as_attachment=True)

@app.route('/admin/users')
def admin_users():
    """Сторінка перегляду користувачів з бази"""
    cursor = db.execute_query("SELECT user_id, username, email, role, created_at FROM users ORDER BY user_id")
    users = cursor.fetchall() if cursor else []
    return render_template('admin_users.html', users=users)

@app.route('/admin/audit')
def admin_audit():
    """Сторінка перегляду журналу аудиту (activity_log)"""
    query = """
        SELECT l.log_id, u.username, l.action, l.table_name, l.record_id, l.details, l.created_at
        FROM activity_log l
        LEFT JOIN users u ON l.user_id = u.user_id
        ORDER BY l.created_at DESC
    """
    cursor = db.execute_query(query)
    logs = cursor.fetchall() if cursor else []
    return render_template('admin_audit.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
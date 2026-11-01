from flask import Flask, render_template, request, redirect, url_for, flash
from database import DatabaseConnection

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Підключення до бази даних у Docker контейнері (база movies)
db = DatabaseConnection(
    dbname='movies',
    user='postgres',
    password='password',
    host='localhost',
    port=5432
)
db.connect()

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
        """
        cursor = db.execute_query(query, (title, year, duration, rating, budget))

        if cursor:
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
        flash('Фільм успішно видалено!', 'success')
    else:
        flash('Помилка видалення фільму', 'error')

    return redirect(url_for('movies'))

@app.route('/authors')
def authors():
    # Використовуємо наше створене раніше View: person_statistics
    query = "SELECT * FROM person_statistics ORDER BY total_movies DESC"
    cursor = db.execute_query(query)
    authors_list = cursor.fetchall() if cursor else []
    return render_template('authors.html', authors=authors_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
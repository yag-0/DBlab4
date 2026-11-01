from flask import jsonify, request
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-api-key-here':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def setup_api_routes(app, db):
    @app.route('/api/movies', methods=['GET'])
    @require_api_key
    def api_movies():
        query = "SELECT movie_id, title, release_year, duration_minutes, rating, budget FROM movies ORDER BY title"
        cursor = db.execute_query(query)

        if cursor:
            movies = cursor.fetchall()
            movies_list = [
                {
                    'id': m[0],
                    'title': m[1],
                    'year': m[2],
                    'duration_minutes': m[3],
                    'rating': float(m[4]) if m[4] is not None else None,
                    'budget': float(m[5]) if m[5] is not None else None
                }
                for m in movies
            ]
            return jsonify({
                'success': True,
                'count': len(movies_list),
                'data': movies_list
            })

        return jsonify({'error': 'Failed to fetch movies'}), 500

    @app.route('/api/movies/<int:movie_id>', methods=['GET'])
    @require_api_key
    def api_movie_detail(movie_id):
        query = "SELECT movie_id, title, release_year, duration_minutes, rating, budget FROM movies WHERE movie_id = %s"
        cursor = db.execute_query(query, (movie_id,))

        if cursor:
            m = cursor.fetchone()
            if m:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': m[0],
                        'title': m[1],
                        'year': m[2],
                        'duration_minutes': m[3],
                        'rating': float(m[4]) if m[4] is not None else None,
                        'budget': float(m[5]) if m[5] is not None else None
                    }
                })

        return jsonify({'error': 'Movie not found'}), 404

    @app.route('/api/movies', methods=['POST'])
    @require_api_key
    def api_create_movie():
        data = request.get_json()

        required_fields = ['title', 'release_year', 'duration_minutes', 'rating', 'budget']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = """
            INSERT INTO movies (title, release_year, duration_minutes, rating, budget)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING movie_id
        """

        cursor = db.execute_query(query, (
            data['title'], data['release_year'], data['duration_minutes'],
            data['rating'], data['budget']
        ))

        if cursor:
            movie_id = cursor.fetchone()[0]
            return jsonify({
                'success': True,
                'message': 'Movie created successfully',
                'movie_id': movie_id
            }), 201

        return jsonify({'error': 'Failed to create movie'}), 500
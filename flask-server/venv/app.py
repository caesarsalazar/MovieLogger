from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Flask server is running"})

@app.route('/api/debug/create-table', methods=['POST'])
def create_table():
    """Debug endpoint to create the movielog table"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Create the table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movielog (
                movie_id SERIAL PRIMARY KEY,
                movie_name TEXT NOT NULL,
                watch_date DATE NOT NULL,
                rating INTEGER CHECK (rating >= 0 AND rating <= 10),
                review TEXT
            );
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO movielog (movie_name, watch_date, rating, review) VALUES 
                ('The Shawshank Redemption', '2024-01-15', 9, 'An incredible story of hope and friendship'),
                ('Inception', '2024-02-20', 8, 'Mind-bending plot that keeps you thinking'),
                ('The Dark Knight', '2024-03-10', 9, 'Heath Ledger''s Joker was phenomenal')
            ON CONFLICT DO NOTHING;
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Table created successfully with sample data"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/tables', methods=['GET'])
def debug_tables():
    """Debug endpoint to show all tables"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"tables": [table['tablename'] for table in tables]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-db', methods=['GET'])  
def test_database():
    """Test database connection"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"message": "Database connected successfully", "version": db_version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Movie CRUD endpoints

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "movieLog" ORDER BY watch_date DESC, movie_id DESC;')
        movies = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert date objects to strings for JSON serialization
        for movie in movies:
            if movie['watch_date']:
                movie['watch_date'] = movie['watch_date'].strftime('%Y-%m-%d')
        
        return jsonify(movies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies', methods=['POST'])
def create_movie():
    """Create a new movie review"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['movie_name', 'watch_date', 'rating']
    for field in required_fields:
        if not data or field not in data or data[field] is None or data[field] == '':
            return jsonify({"error": f"{field} is required"}), 400
    
    # Validate rating is between 1-10 (or your preferred scale)
    try:
        rating = int(data['rating'])
        if rating < 0 or rating > 10:
            return jsonify({"error": "Rating must be between 0 and 10"}), 400
    except ValueError:
        return jsonify({"error": "Rating must be a valid integer"}), 400
    
    # Validate date format
    try:
        datetime.strptime(data['watch_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO "movieLog" (movie_name, watch_date, rating, review) 
               VALUES (%s, %s, %s, %s) RETURNING movie_id;''',
            (data['movie_name'], data['watch_date'], data['rating'], data.get('review', ''))
        )
        movie_id = cursor.fetchone()['movie_id']
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Movie review created successfully", "movie_id": movie_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    """Update a movie review"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'movie_name' in data and data['movie_name']:
            update_fields.append("movie_name = %s")
            values.append(data['movie_name'])
        
        if 'watch_date' in data and data['watch_date']:
            # Validate date format
            try:
                datetime.strptime(data['watch_date'], '%Y-%m-%d')
                update_fields.append("watch_date = %s")
                values.append(data['watch_date'])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        if 'rating' in data and data['rating'] is not None:
            try:
                rating = int(data['rating'])
                if rating < 0 or rating > 10:
                    return jsonify({"error": "Rating must be between 0 and 10"}), 400
                update_fields.append("rating = %s")
                values.append(rating)
            except ValueError:
                return jsonify({"error": "Rating must be a valid integer"}), 400
        
        if 'review' in data:
            update_fields.append("review = %s")
            values.append(data['review'])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        values.append(movie_id)
        query = f'UPDATE "movieLog" SET {", ".join(update_fields)} WHERE movie_id = %s;'
        
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Movie not found"}), 404
        
        cursor.close()
        conn.close()
        return jsonify({"message": "Movie review updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """Delete a movie review"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "movieLog" WHERE movie_id = %s;', (movie_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Movie not found"}), 404
        
        cursor.close()
        conn.close()
        return jsonify({"message": "Movie review deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie by ID"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "movieLog" WHERE movie_id = %s;', (movie_id,))
        movie = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not movie:
            return jsonify({"error": "Movie not found"}), 404
        
        # Convert date object to string for JSON serialization
        if movie['watch_date']:
            movie['watch_date'] = movie['watch_date'].strftime('%Y-%m-%d')
        
        return jsonify(movie)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
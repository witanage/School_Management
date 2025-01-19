from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

app = Flask(__name__)

# Enable CORS for all routes (you can be more specific if needed)
# CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})
CORS(app)

# Secret key for JWT encoding/decoding
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a strong secret key

# Database connection details
db_config = {
    # "host": "localhost",
    # "user": "root",
    # "password": "",
    # "database": "school"
    "host": "y83h6.h.filess.io",
    "user": "schoollk_mustbranch",
    "port": 3307,
    "password": "4594fa9129855d7914edb028baddeef34ab23a70",
    "database": "schoollk_mustbranch"
}


def connect_to_db():
    return pymysql.connect(**db_config)


# Add a new student
@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        student_data = request.json
        name = student_data.get('name')
        age = student_data.get('age')
        class_id = student_data.get('class_id')
        language_stream_id = student_data.get('language_stream_id')
        stream_id = student_data.get('stream_id')

        # Validate input
        if not name or not isinstance(age, int) or not class_id or not language_stream_id or not stream_id:
            return jsonify({"error": "Invalid input"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Check if the referenced IDs exist
            cursor.execute("SELECT id FROM classes WHERE id = %s", (class_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Invalid class_id"}), 400

            cursor.execute("SELECT id FROM language_streams WHERE id = %s", (language_stream_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Invalid language_stream_id"}), 400

            cursor.execute("SELECT id FROM streams WHERE id = %s", (stream_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Invalid stream_id"}), 400

            # Insert student data
            sql = """
                INSERT INTO students (name, age, class_id, language_stream_id, stream_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, age, class_id, language_stream_id, stream_id))
            connection.commit()

        return jsonify({"message": "Student added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Add a new class
@app.route('/api/classes', methods=['POST'])
def add_class():
    try:
        class_data = request.json
        name = class_data.get('name')

        if not name:
            return jsonify({"error": "Invalid input"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = "INSERT INTO classes (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            connection.commit()

        return jsonify({"message": "Class added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Add a new language stream
@app.route('/api/language_streams', methods=['POST'])
def add_language_stream():
    try:
        stream_data = request.json
        name = stream_data.get('name')

        if not name:
            return jsonify({"error": "Invalid input"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = "INSERT INTO language_streams (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            connection.commit()

        return jsonify({"message": "Language stream added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Add a new stream
@app.route('/api/streams', methods=['POST'])
def add_stream():
    try:
        stream_data = request.json
        name = stream_data.get('name')

        if not name:
            return jsonify({"error": "Invalid input"}), 400

        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = "INSERT INTO streams (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            connection.commit()

        return jsonify({"message": "Stream added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Add a new administrator
@app.route('/api/administrators', methods=['POST'])
def add_administrator():
    try:
        admin_data = request.json
        name = admin_data.get('name')
        username = admin_data.get('username')
        password = admin_data.get('password')

        # Validate input
        if not name or not username or not password:
            return jsonify({"error": "Invalid input"}), 400

        # Hash the password using PBKDF2
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the administrator into the database
        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = "INSERT INTO administrators (name, username, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, username, hashed_password))
            connection.commit()

        return jsonify({"message": "Administrator added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Login administrator
@app.route('/api/login', methods=['POST'])
def login():
    try:
        login_data = request.json
        username = login_data.get('username')
        password = login_data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Check if the administrator exists
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM administrators WHERE username = %s", (username,))
            admin = cursor.fetchone()

        if not admin:
            return jsonify({"error": "Invalid username or password"}), 401

        # Check if the password is correct
        if not check_password_hash(admin[1], password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate JWT token
        token = jwt.encode(
            {'user_id': admin[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Helper function to format query results with column names
def format_results(cursor, results):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in results]


# Retrieve all students with class, stream, and language stream names
@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Use JOIN to get class, stream, and language stream names
            sql = """
                SELECT 
                    s.id, s.name, s.age,
                    c.name AS class_name, 
                    ls.name AS language_stream_name, 
                    st.name AS stream_name
                FROM students s
                JOIN classes c ON s.class_id = c.id
                JOIN language_streams ls ON s.language_stream_id = ls.id
                JOIN streams st ON s.stream_id = st.id
            """
            cursor.execute(sql)
            students = cursor.fetchall()
            return jsonify({"students": format_results(cursor, students)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Retrieve all classes
@app.route('/api/classes', methods=['GET'])
def get_classes():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM classes")
            classes = cursor.fetchall()
            return jsonify({"classes": format_results(cursor, classes)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Retrieve all streams
@app.route('/api/streams', methods=['GET'])
def get_streams():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM streams")
            streams = cursor.fetchall()
            return jsonify({"streams": format_results(cursor, streams)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Retrieve all language streams
@app.route('/api/language_streams', methods=['GET'])
def get_language_streams():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM language_streams")
            language_streams = cursor.fetchall()
            return jsonify({"language_streams": format_results(cursor, language_streams)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Retrieve all administrators
@app.route('/api/administrators', methods=['GET'])
def get_administrators():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, username FROM administrators")
            administrators = cursor.fetchall()
            return jsonify({"administrators": format_results(cursor, administrators)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()


# Logout administrator (invalidate the token)
@app.route('/api/logout', methods=['POST'])
def logout():
    # Invalidate the token by simply not sending it back
    return jsonify({"message": "Logged out successfully"}), 200


if __name__ == '__main__':
    app.run(debug=False)

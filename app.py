from flask import Flask, render_template, request
import hashlib
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY, filename TEXT, filehash TEXT UNIQUE, status TEXT)''')
    conn.commit()
    conn.close()

def get_file_hash(file_data):
    return hashlib.sha256(file_data).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        file = request.files['file']
        if file:
            data = file.read()
            file_hash = get_file_hash(data)
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM files WHERE filehash=?", (file_hash,))
            existing = c.fetchone()
            if existing:
                message = f"❌ REDUNDANT DATA! File '{file.filename}' already exists."
            else:
                c.execute("INSERT INTO files VALUES (NULL,?,?,?)", (file.filename, file_hash, "Unique"))
                message = f"✅ UNIQUE DATA! File '{file.filename}' added."
            conn.commit()
            conn.close()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM files")
    all_files = c.fetchall()
    conn.close()
    return render_template('index.html', message=message, files=all_files)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Просто подсказка пользователю
ALLOWED_AUTHORS = ["Джордж Оруэлл", "Олдос Хаксли", "Рэй Брэдбери"]

# HTML-шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Поиск книг</title>
    <style>
        body { font-family: sans-serif; padding: 2em; max-width: 600px; margin: auto; }
        input[type="text"] { padding: 0.5em; width: 100%; margin-bottom: 1em; }
        button { padding: 0.5em 1em; }
        .error { color: darkred; margin-top: 1em; }
        .result { margin-top: 1em; }
        .book { margin-bottom: 0.5em; }
        .hint { font-size: 0.9em; color: gray; }
    </style>
</head>
<body>
    <h2>Поиск книг по автору</h2>
    <p class="hint">Введите имя и/или фамилию одного из авторов: <strong>{{ allowed }}</strong></p>
    <form method="GET">
        <input type="text" name="author" placeholder="Например: Хаксли Олдос" value="{{ query or '' }}" />
        <button type="submit">Поиск</button>
    </form>

    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}

    {% if books %}
        <div class="result">
            <h3>Найдено книг: {{ books|length }}</h3>
            {% for book in books %}
                <div class="book">📖 <strong>{{ book.title }}</strong> — {{ book.author }}</div>
            {% endfor %}
        </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("author", "")
    error = None
    books = []

    if query:
        try:
            # Во время разработки без Docker используй localhost
            resp = requests.get("http://backend:5000/search", params={"author": query}, timeout=3)
            if resp.status_code == 200:
                books = resp.json()
                if not books:
                    error = "Книг не найдено. Попробуйте ввести имя и/или фамилию автора (например, 'Оруэлл', 'Хаксли Олдос')."
            else:
                error = "Ошибка при обращении к серверу."
        except Exception:
            error = "Не удалось подключиться к серверу."

    return render_template_string(HTML_TEMPLATE,
                                  books=books,
                                  error=error,
                                  query=query,
                                  allowed=", ".join(ALLOWED_AUTHORS))

if __name__ == "__main__":
    # Работает как локально, так и в Docker
    app.run(host="0.0.0.0", port=5001)

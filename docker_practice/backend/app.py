from flask import Flask, request, Response
import json

app = Flask(__name__)

BOOKS = [
    {"title": "Скотный двор", "author": "Джордж Оруэлл"},
    {"title": "1984", "author": "Джордж Оруэлл"},
    {"title": "О дивный новый мир", "author": "Олдос Хаксли"},
    {"title": "Остров", "author": "Олдос Хаксли"},
    {"title": "451° по Фаренгейту", "author": "Рэй Брэдбери"},
    {"title": "Марсианские хроники", "author": "Рэй Брэдбери"},
]

def normalize(text):
    return text.strip().lower()

def name_matches(query: str, author: str) -> bool:
    q_words = normalize(query).split()
    a_words = normalize(author).split()

    if len(q_words) == 1:
        return q_words[0] in a_words
    elif len(q_words) == 2:
        return (
            q_words == a_words or
            q_words[::-1] == a_words
        )
    else:
        return False

@app.route("/search")
def search():
    query = request.args.get("author", "")
    if not query:
        return Response("[]", content_type="application/json; charset=utf-8")

    results = [book for book in BOOKS if name_matches(query, book["author"])]

    return Response(
        json.dumps(results, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

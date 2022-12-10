import json
from main import app


def test_index_route():
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.data.decode("utf-8") == "Hello world!"


def test_get_all_books():
    response = app.test_client().get("/books")

    book = json.loads(response.data.decode("utf-8")).get("books")
    assert response.status_code == 200
    assert len(book) == 2
    assert book[0]["id"] == 1
    assert book[0]["title"] == "Harry Potter and the Goblet of Fire"
    assert book[0]["author"] == "J.K. Rowling"
    assert book[0]["isbn"] == "1512379298"
    assert book[1]["id"] == 2
    assert book[1]["title"] == "Lord of the Flies"
    assert book[1]["author"] == "William Golding"
    assert book[1]["isbn"] == "0399501487"


def test_get_goblet_of_fire():
    response = app.test_client().get("/books/1")

    book = json.loads(response.data.decode("utf-8")).get("book")
    assert response.status_code == 200
    assert book["id"] == 1
    assert book["title"] == "Harry Potter and the Goblet of Fire"
    assert book["author"] == "J.K. Rowling"
    assert book["isbn"] == "1512379298"


def test_get_lord_of_the_flies():
    response = app.test_client().get("/books/2")

    book = json.loads(response.data.decode("utf-8")).get("book")
    assert response.status_code == 200
    assert book["id"] == 2
    assert book["title"] == "Lord of the Flies"
    assert book["author"] == "William Golding"
    assert book["isbn"] == "0399501487"
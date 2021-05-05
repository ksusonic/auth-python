from fastapi import FastAPI, Form
from fastapi.responses import Response


app = FastAPI()

users = {
    "dan@user.com": {
        "name": "Даниил",
        "password": "some_password_1",
        "balance": 100_000
    },
    "petr@user.com": {
        "name": "Пётр",
        "password": "some_password_2",
        "balance": 555_555
    }
}

@app.get('/')
def index_page():
    with open("templates/login.html", 'r') as f:
        login_page = f.read()
    return Response(login_page, media_type="text/html")

@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return Response("Я вас не знаю!", media_type="text/html")

    response = Response(
        f"Привет, {user['name']}<br />Баланс: {user['balance']}", 
    media_type="text/html")
    response.set_cookie(key="username", value=username)
    return response
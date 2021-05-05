from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response
from typing import Optional


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
def index_page(username: Optional[str] = Cookie(default=None)):
    with open("templates/login.html", 'r') as f:
        login_page = f.read()
    if username:
        try:
            user = users[username]
        except KeyError:
            response = Response(login_page, media_type="text/html")
            response.delete_cookie(key="username")
            return response
        return Response(f"Привет, {users[username]['name']}!", media_type="text/html")
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
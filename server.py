from typing import Optional
import base64
import hmac
import hashlib

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "34d77c401b36c22caa14ee8029362992d0f32d088a2484ccac496b088865c2ce"


def sign_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_b64, sign = username_signed.split(".")

    username = base64.b64decode(username_b64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username

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
    if not username:
        return Response(login_page, media_type="text/html")

    valid_username = get_username_from_signed_string(username)
    print(valid_username)
    if not valid_username:
        print("not valid username")
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response

    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(f"Привет, {users[valid_username]['name']}!", media_type="text/html")


@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return Response("Я вас не знаю!", media_type="text/html")

    response = Response(
        f"Привет, {user['name']}<br />Баланс: {user['balance']}",
        media_type="text/html")

    username_signed = base64.b64encode(username.encode()).decode() + '.' + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response

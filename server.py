from typing import Optional
import json
import base64
import hmac
import hashlib

from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "34d77c401b36c22caa14ee8029362992d0f32d088a2484ccac496b088865c2ce"
PASSWORD_SALT = "3efcc56db8a7ab12b2fe388aa7bf52d1a32b8cb12b79af4a7cbb94c65e87db42"


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


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256(
        (password + PASSWORD_SALT).encode()).hexdigest().lower()
    stored_password_hash = users[username]['password'].lower()
    return password_hash == stored_password_hash


users = {
    "dan@user.com": {
        "name": "Даниил",
        "password": "5b0697de8cfeca89106ec0f41ad4c3d4f25ac458ac19afb611361d470754d870",
        "balance": 100_000
    },
    "petr@user.com": {
        "name": "Пётр",
        "password": "d7d2090da3754c4cabb8a9647c28e243780cf80d7b7a0a7a96b814fca1b72215",
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
    return Response(f"Привет, {users[valid_username]['name']}!<br />Баланс: {users[valid_username]['balance']}", media_type="text/html")


@app.post('/login')
def process_login_page(data: dict = Body(...)):
    username = data['username']
    password = data['password']
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю!"
            }), 
            media_type="application/json")

    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}<br />Баланс: {user['balance']}"
        }),
        media_type="application/json")

    username_signed = base64.b64encode(username.encode()).decode() + '.' + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response

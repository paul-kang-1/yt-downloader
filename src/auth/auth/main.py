import datetime
import os
from http import HTTPStatus as status
from pathlib import Path
from typing import Tuple

import jwt
from dotenv import load_dotenv
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
if os.environ.get("WORK_ENV", "development") == "development":
    load_dotenv(os.path.join(Path(__file__).parents[1], '.env.local'))
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")


# routes
@server.route("/login", methods=["POST"])
def login() -> Tuple[str, int]:
    # access basic auth header from request
    auth = request.authorization
    if not auth:
        return "missing credentials", status.UNAUTHORIZED

    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )
    if res > 0:
        user_row = cur.fetchone()
        email, password = user_row[:2]

        if auth.username != email or auth.password != password:
            return "invalid credentials", status.UNAUTHORIZED
        else:
            return (
                create_jwt(
                    str(auth.username or ""),
                    str(os.environ.get("JWT_SECRET") or ""),
                    True,
                ),
                status.OK,
            )
    return "invalid credentials", status.UNAUTHORIZED


@server.route("/validate", methods=["POST"])
def validate() -> Tuple[str, int]:
    encoded_jwt: str = request.headers["Authorization"]
    if not encoded_jwt:
        return "missing credentials", status.UNAUTHORIZED
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError as e:
        return f"not authorized: {e}", status.FORBIDDEN
    return f"Hi {decoded['username']}!", status.OK


def create_jwt(username: str, secret: str, is_admin: bool) -> str:
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "admin": is_admin,
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=3101)

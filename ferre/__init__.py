import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import find_dotenv, load_dotenv

db = SQLAlchemy()
app = Flask(__name__)

def create_app(test_config=None):
    load_dotenv(find_dotenv(usecwd=True), override=False)

    db_user = os.getenv("USER_DB")
    db_password = os.getenv("PASSWORD_DB")
    db_host = os.getenv("HOST_DB", "localhost")
    db_port = os.getenv("PORT_DB", "5432")
    db_name = os.getenv("NAME_DB")

    missing_vars = [
        name
        for name, value in {
            "USER_DB": db_user,
            "PASSWORD_DB": db_password,
            "NAME_DB": db_name,
        }.items()
        if not value
    ]
    if missing_vars:
        raise RuntimeError(
            "Faltan variables de entorno requeridas: " + ", ".join(missing_vars)
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    db.init_app(app)

    from . import routes

    return app


create_app()

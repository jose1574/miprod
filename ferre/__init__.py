import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def _resolve_main_code(code: str):
    main_code = None
    result = (
        db.session.execute(
            text("SELECT * FROM products_codes WHERE other_code = :code"),
            {"code": code},
        )
        .mappings()
        .fetchone()
    )
    if result:
        main_code = dict(result)["main_code"]
    else:
        flash("Código no encontrado en la base de datos", "warning")
    return main_code


# funcion que devuelve todos los codigos realacionados a un codigo principal, incluyendo el mismo codigo principal
def _resolve_related_codes(main_code: str):
    related_codes = []
    result = (
        db.session.execute(
            text("SELECT * FROM products_codes WHERE main_code = :main_code"),
            {"main_code": main_code},
        )
        .mappings()
        .fetchall()
    )
    if result:
        related_codes = [dict(row)["other_code"] for row in result]
    else:
        flash("No se encontraron códigos relacionados en la base de datos", "warning")
    return dict(related_codes=related_codes)


def _resolve_product_info(main_code: str):
    product_info = None
    result = (
        db.session.execute(
            text(
                "SELECT p.*, d.description as department_description FROM products p "
                "LEFT JOIN department d ON p.department = d.code "
                "WHERE p.code = :code"
            ),
            {"code": main_code},
        )
        .mappings()
        .fetchone()
    )
    if result:
        product_info = dict(result)
    else:
        flash("No se encontró información del producto en la base de datos", "warning")
    return dict(product_info=product_info)


def create_app(test_config=None):
    app = Flask(__name__)
    db_user = os.getenv("USER_DB", "postgres")
    db_password = os.getenv("PASSWORD_DB", "root")
    db_host = os.getenv("HOST_DB", "localhost")
    db_port = os.getenv("PORT_DB", "5432")
    db_name = os.getenv("NAME_DB")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    db.init_app(app)

    @app.route("/")
    def home():
        product_code = request.args.get("product-code")
        product_info = None
        related_codes_result = {"related_codes": []}

        try:
            if product_code:
                main_code = _resolve_main_code(product_code)
                if main_code:
                    related_codes_result = _resolve_related_codes(main_code)
                    product_info_result = _resolve_product_info(main_code)
                    product_info = product_info_result["product_info"]
        except Exception as e:
            flash(f"Error al procesar la solicitud: {str(e)}", "danger")

        return render_template(
            "index.html",
            product=product_info,
            code_search=product_code,
            related_codes=related_codes_result["related_codes"],
        )

    @app.route("/save_product", methods=["POST"])
    def save_product():
        code = request.form.get("code")
        bar_code = request.form.get("bar_code")
        description = request.form.get("description")
        department = request.form.get("department")
        mark = request.form.get("mark")
        price = request.form.get("price")

        try:
            db.session.execute(
                text(
                    "INSERT INTO ferre.new_products (code, bar_code, description, department, mark, price) "
                    "VALUES (:code, :bar_code, :description, :department, :mark, :price)"
                ),
                {
                    "code": code,
                    "bar_code": bar_code,
                    "description": description,
                    "department": department,
                    "mark": mark,
                    "price": price,
                },
            )
            db.session.commit()
            flash("Producto guardado exitosamente", "success")

        except Exception as e:
            db.session.rollback()
            error = f"Error al guardar el producto: {str(e)}"
            flash(error, "danger")

        return redirect(url_for("home"))

    return app

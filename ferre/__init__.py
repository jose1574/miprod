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
                "SELECT p.*, d.description as department_description, u.description as unit_description FROM products p "
                "LEFT JOIN department d ON p.department = d.code "
                "LEFT JOIN products_units pu ON p.code = pu.product_code "
                "LEFT JOIN units u ON pu.unit = u.code "
                "WHERE p.code = :code "
                "AND pu.main_unit = true"
            ),
            {"code": main_code},
        )
        .mappings()
        .fetchone()
    )
    if result:
        product_info = dict(result)
        print(f"Información del producto encontrada: {product_info}")
    else:
        flash("No se encontró información del producto en la base de datos", "warning")
    return dict(product_info=product_info)


def create_app(test_config=None):
    app = Flask(__name__)
    db_user = os.getenv("USER_DB", "postgres")
    db_password = os.getenv("PASSWORD_DB", "root")
    db_host = os.getenv("HOST_DB", "localhost")
    db_port = os.getenv("PORT_DB", "5432")
    db_name = os.getenv("NAME_DB", "cadm_v1029")
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
        unit = request.form.get("unit")
        price = request.form.get("price")

        try:
            db.session.execute(
                text(
                    "INSERT INTO ferre.new_products (code, bar_code, description, department, mark, unit, price) "
                    "VALUES (:code, :bar_code, :description, :department, :mark, :unit, :price)"
                ),
                {
                    "code": code,
                    "bar_code": bar_code,
                    "description": description,
                    "department": department,
                    "mark": mark,
                    "unit": unit,
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
    
    @app.route("/productos-nuevos")
    def new_products():
        new_products = []
        try:
            result = (
                db.session.execute(
                    text("SELECT * FROM ferre.new_products ")
                )
                .mappings()
                .fetchall()
            )
            new_products = [dict(row) for row in result]
        except Exception as e:
            flash(f"Error al obtener los productos nuevos: {str(e)}", "danger")

        return render_template("new_products.html", products=new_products)
    
    @app.route("/delete_product/<int:product_id>", methods=["POST"])
    def delete_product(product_id):
        try:
            db.session.execute(
                text("DELETE FROM ferre.new_products WHERE id = :id"),
                {"id": product_id},
            )
            db.session.commit()
            flash("Producto eliminado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar el producto: {str(e)}", "danger")
        return redirect(url_for("new_products"))

    @app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
    def edit_product(product_id):
        if request.method == "POST":
            code = request.form.get("code")
            bar_code = request.form.get("bar_code")
            description = request.form.get("description")
            department = request.form.get("department")
            mark = request.form.get("mark")
            unit = request.form.get("unit")
            price = request.form.get("price")

            try:
                db.session.execute(
                    text(
                        "UPDATE ferre.new_products "
                        "SET code = :code, bar_code = :bar_code, description = :description, "
                        "department = :department, mark = :mark, unit = :unit, price = :price "
                        "WHERE id = :id"
                    ),
                    {
                        "id": product_id,
                        "code": code,
                        "bar_code": bar_code,
                        "description": description,
                        "department": department,
                        "mark": mark,
                        "unit": unit,
                        "price": price,
                    },
                )
                db.session.commit()
                flash("Producto actualizado exitosamente", "success")
                return redirect(url_for("new_products"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar el producto: {str(e)}", "danger")

        try:
            result = (
                db.session.execute(
                    text("SELECT * FROM ferre.new_products WHERE id = :id"),
                    {"id": product_id},
                )
                .mappings()
                .fetchone()
            )

            if not result:
                flash("Producto no encontrado", "warning")
                return redirect(url_for("new_products"))

            product = dict(result)
            return render_template("edit_product.html", product=product)
        except Exception as e:
            flash(f"Error al obtener el producto: {str(e)}", "danger")
            return redirect(url_for("new_products"))

    return app

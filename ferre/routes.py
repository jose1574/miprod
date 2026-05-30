#importacion de app 
from . import app, db
from sqlalchemy import text



from flask import flash, render_template, request, redirect, url_for
from .services.query import (
    _resolve_main_code,
    _resolve_product_codes,
    _resolve_product,
    _resolve_product_units,
    _departments,
    _marks,
    _units,
    _resolve_product_main_unit
)






@app.route("/")
def home():
    code_search = request.args.get("product-code")
    product = None
    existing_new_product = None
    products_codes = []
    product_units = []
    product_main_unit = None
    departments = _departments()
    marks = _marks()
    units = _units()

    

    
    try:
        if code_search:
            main_code = _resolve_main_code(code_search)
            if main_code:
                product = _resolve_product(main_code)
                products_codes = _resolve_product_codes(main_code)
                product_units = _resolve_product_units(main_code)
                product_main_unit = _resolve_product_main_unit(main_code)

                existing_row = (
                    db.session.execute(
                        text("SELECT id, code, description FROM ferre.new_products WHERE code = :code"),
                        {"code": main_code},
                    )
                    .mappings()
                    .fetchone()
                )
                if existing_row:
                    existing_new_product = dict(existing_row)
    except Exception as e:
        flash(f"Error al procesar la solicitud: {str(e)}", "danger")

    return render_template(
        "index.html",
        code_search=code_search,
        product=product,
        product_codes=products_codes,
        product_units=product_units,
        product_unit=product_main_unit,
        departments=departments,
        marks=marks,
        units=units,
        existing_new_product=existing_new_product,
    )












@app.route("/save_product", methods=["POST"])
def save_product():
    code = request.form.get("code")
    bar_code = request.form.get("bar_code")
    description = request.form.get("description")
    department = request.form.get("department")
    mark = request.form.get("mark")
    unit = request.form.get("unit")
    unitary_cost = request.form.get("unitary_cost")
    maximum_price = request.form.get("maximum_price")
    offer_price = request.form.get("offer_price")
    higher_price = request.form.get("higher_price")
    minimum_price = request.form.get("minimum_price")

    try:
        db.session.execute(
            text(
                "INSERT INTO ferre.new_products (code," \
                " description, " \
                "department, " \
                "mark, " \
                "unit, " \
                "unitary_cost, " \
                "maximum_price, " \
                "offer_price, " \
                "higher_price, " \
                "minimum_price " \
                ") "
                "VALUES (:code, :description, :department, :mark, :unit, :unitary_cost, :maximum_price, :offer_price, :higher_price, :minimum_price)"
            ),
            {
                "code": code,
                "description": description,
                "department": department,
                "mark": mark,
                "unit": unit,
                "unitary_cost": request.form.get("unitary_cost"),
                "maximum_price": request.form.get("maximum_price"),
                "offer_price": request.form.get("offer_price"),
                "higher_price": higher_price,
                "minimum_price": minimum_price,
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
        unitary_cost = request.form.get("unitary_cost")
        maximum_price = request.form.get("maximum_price")
        offer_price = request.form.get("offer_price")
        higher_price = request.form.get("higher_price")
        minimum_price = request.form.get("minimum_price")

        try:
            db.session.execute(
                text(
                    "UPDATE ferre.new_products "
                    "SET code = :code, description = :description, "
                    "department = :department, mark = :mark, unit = :unit, unitary_cost = :unitary_cost, "
                    "maximum_price = :maximum_price, offer_price = :offer_price, "
                    "higher_price = :higher_price, minimum_price = :minimum_price "
                    "WHERE id = :id"
                ),
                {
                    "id": product_id,
                    "code": code,
                    "description": description,
                    "department": department,
                    "mark": mark,
                    "unit": unit,
                    "unitary_cost": unitary_cost,
                    "maximum_price": maximum_price,
                    "offer_price": offer_price,
                    "higher_price": higher_price,
                    "minimum_price": minimum_price,
                },
            )
            db.session.commit()
            flash("Producto actualizado exitosamente", "success")
            return redirect(url_for("new_products"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el producto: {str(e)}", "danger")

    departments = _departments()
    marks = _marks()
    units = _units()

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
        return render_template(
            "partials/update_product_form.html",
            product=product,
            departments=departments,
            marks=marks,
            units=units,
        )
    except Exception as e:
        flash(f"Error al obtener el producto: {str(e)}", "danger")
        return redirect(url_for("new_products"))


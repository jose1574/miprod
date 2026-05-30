from flask import flash

from .. import db
from sqlalchemy import text



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
def _resolve_product_codes(main_code: str):
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
        related_codes = [dict(row) for row in result]
    else:
        flash("No se encontraron códigos relacionados en la base de datos", "warning")
    return related_codes


def _resolve_product(main_code: str):
    product_info = None
    result = (
        db.session.execute(
            text(
                "SELECT * FROM products p "
                "WHERE code = :code "
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
    return product_info


def _resolve_product_main_unit(main_code: str):
    product_main_unit = None
    result = (
        db.session.execute(
            text("SELECT "
            "ROUND((unitary_cost * 1.16)::numeric, 2) as unitary_cost,"
            "unit," \
            "ROUND((maximum_price * 1.16)::numeric, 2) as maximum_price," \
            "ROUND((offer_price * 1.16)::numeric, 2) as offer_price," \
            "ROUND((higher_price * 1.16)::numeric, 2) as higher_price," \
            "ROUND((minimum_price * 1.16)::numeric, 2) as minimum_price " \
            "FROM products_units WHERE product_code = :code AND main_unit = true"
            ),
            {"code": main_code},
        )
        .mappings()
        .fetchone()
    )
    if result:
        product_main_unit = dict(result)
    else:
        flash("No se encontró la unidad principal del producto en la base de datos", "warning")
    return product_main_unit


def _resolve_product_units(main_code: str):
    product_units = []
    result = (
        db.session.execute(
            text(
                "SELECT * FROM products_units WHERE product_code = :code"
            ),
            {"code": main_code},
        )
        .mappings()
        .fetchall()
    )
    if result:
        product_units = [dict(row) for row in result]
    else:
        flash("No se encontraron unidades de producto en la base de datos", "warning")
    return product_units

def _departments():
    departments = []
    result = (
        db.session.execute(
            text("SELECT * FROM department")
        )
        .mappings()
        .fetchall()
    )
    if result:
        departments = [dict(row) for row in result]
    else:
        flash("No se encontraron departamentos en la base de datos", "warning")
    return departments


def _marks():
    marks = []
    result = (
        db.session.execute(
            text("SELECT * FROM marks")
        )
        .mappings()
        .fetchall()
    )
    if result:
        marks = [dict(row) for row in result]
    else:
        flash("No se encontraron marcas en la base de datos", "warning")
    return marks


def _units():
    units = []
    result = (
        db.session.execute(
            text("SELECT * FROM units")
        )
        .mappings()
        .fetchall()
    )
    if result:
        units = [dict(row) for row in result]
    else:
        flash("No se encontraron unidades en la base de datos", "warning")
    return units
import os
from flask import Flask, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    conn_string = "postgresql://postgres:root@localhost:5432/cadm_v1029"

    app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'
    
    db.init_app(app)

    @app.route('/')
    def home():
        product_code = request.args.get('product-code')
        product_info = None
        error = None

        if product_code:
            try:
                result = db.session.execute(
                    text("SELECT * FROM products WHERE code = :code"),
                    {"code": product_code}
                ).mappings().fetchone()

                if result:
                    product_info = dict(result)
                    print(f"Producto encontrado: {product_info}")
                else:
                    print(f"Producto no encontrado para codigo: {product_code}")
                    flash("Producto no encontrado", "warning")
            except Exception as e:
                error = str(e)
                flash(f"Error fetching product information: {error}", "danger")

        return render_template('index.html', product=product_info)

    return app
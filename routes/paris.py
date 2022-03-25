from flask import Blueprint, render_template, abort, jsonify
import db
from models.Articulo import Articulo
from models.Precio import Precio

paris_bp = Blueprint('paris_bp', __name__, template_folder="templates")

@paris_bp.route('/paris/productos')
def productosParis():
    return render_template('paris.html')

@paris_bp.route('/paris/producto/<id>')
def productoParis(id):
    try:
        producto = db.session.query(Articulo).get(id)
        if producto:
            return render_template('detalle_producto_paris.html', producto=producto)
        else:
            return abort(404)
    except Exception as e:
        print("Error al obtener precios", e)
        return abort(500)
    finally:
        db.session.close()

@paris_bp.route('/api/paris')
def apiParis():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Paris", Articulo.descuento >= 20).order_by(Articulo.descuento.desc())
    productos = [{
        "id": a.id,
        "nombre": a.nombre,
        "marca": a.marca,
        "precio": a.last_precio,
        "mejor_precio": a.best_precio,
        "descuento": a.descuento,
        "url": a.url
    } for a in res]
    db.session.close()

    return jsonify(
        {
            "data": productos,
            "recordsTotal": len(productos),
            "recordsFiltered": len(productos),
            "draw": 1,
        }
    )

@paris_bp.route('/api/paris/producto/<id>')
def apiProductoParis(id):
    res = db.session.query(Precio).filter(id == Precio.articulo_id).all()
    precios = [{
        "precio": p.valor,
        "date": p.create_date
    } for p in res]
    db.session.close()

    return jsonify(
        {
            "data": precios,
        }
    )
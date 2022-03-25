from flask import Blueprint, render_template, jsonify, abort
import db
from models.Articulo import Articulo
from models.Precio import Precio

hites_bp = Blueprint('hites_bp', __name__, template_folder="templates")

@hites_bp.route('/hites/productos')
def productosHites():
    return render_template('hites.html')

@hites_bp.route('/hites/producto/<int:id>')
def productoHites(id):
    try:
        producto = db.session.query(Articulo).get(id)
        if producto:
            return render_template('detalle_producto_abcdin.html', producto=producto)
        else:
            return abort(404)
    except Exception as e:
        print("Error al obtener precios", e)
        return abort(500)
    finally:
        db.session.close()

@hites_bp.route('/api/hites')
def apiHites():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Hites", Articulo.descuento >= 20).order_by(Articulo.descuento.desc())
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

@hites_bp.route('/api/hites/producto/<int:id>')
def apiProductoHites(id):
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
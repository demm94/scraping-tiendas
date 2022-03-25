from flask import Blueprint, render_template, abort, jsonify
import db
from models.Articulo import Articulo
from models.Precio import Precio

ripley_bp = Blueprint('ripley_bp', __name__, template_folder="templates")

@ripley_bp.route('/ripley/productos')
def productosRipley():
    return render_template('ripley.html')

@ripley_bp.route('/api/ripley')
def apiRipley():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Ripley", Articulo.descuento >= 30).order_by(Articulo.descuento.desc())
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

@ripley_bp.route('/ripley/producto/<id>')
def productoRipley(id):
    try:
        producto = db.session.query(Articulo).get(id)
        if producto:
            return render_template('detalle_producto_ripley.html', producto=producto)
        else:
            return abort(404)
    except Exception as e:
        print("Error al obtener precios", e)
        return abort(500)
    finally:
        db.session.close()


@ripley_bp.route('/api/ripley/producto/<id>')
def apiProductoRipley(id):
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
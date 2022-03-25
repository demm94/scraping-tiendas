from flask import Blueprint, render_template, jsonify, abort
import db
from models.Articulo import Articulo
from models.Precio import Precio

abcdin_bp = Blueprint('abcdin_bp', __name__, template_folder="templates")

@abcdin_bp.route('/abcdin/productos')
def productosAbcdin():
    return render_template('abcdin.html')

@abcdin_bp.route('/abcdin/producto/<int:id>')
def productoAbcdin(id):
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

@abcdin_bp.route('/api/abcdin')
def apiAbcdin():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Abcdin").all()
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

@abcdin_bp.route('/api/abcdin/producto/<int:id>')
def apiProductoAbcdin(id):
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
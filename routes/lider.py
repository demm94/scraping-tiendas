from flask import Blueprint, render_template, abort, jsonify
import db
from models.Articulo import Articulo
from models.Precio import Precio

lider_bp = Blueprint('lider_bp', __name__, template_folder="templates")

@lider_bp.route('/lider/productos')
def productosLider():
    return render_template('lider.html')

@lider_bp.route('/api/lider')
def apiLider():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Lider", Articulo.descuento >= 15).order_by(Articulo.descuento.desc())
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

@lider_bp.route('/lider/producto/<id>')
def productoLider(id):
    try:
        producto = db.session.query(Articulo).get(id)
        if producto:
            return render_template('detalle_producto_lider.html', producto=producto)
        else:
            return abort(404)
    except Exception as e:
        print("Error al obtener precios", e)
        return abort(500)
    finally:
        db.session.close()


@lider_bp.route('/api/lider/producto/<id>')
def apiProductoLider(id):
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
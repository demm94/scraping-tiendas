from flask import Blueprint, render_template, jsonify, abort
import db
from models.Articulo import Articulo
from models.Precio import Precio

lapolar_bp = Blueprint('lapolar_bp', __name__, template_folder="templates")

@lapolar_bp.route('/lapolar/productos')
def productosLapolar():
    return render_template('lapolar.html')

@lapolar_bp.route('/api/lapolar')
def apiLapolar():
    res = db.session.query(Articulo).filter(Articulo.tienda == "Lapolar", Articulo.descuento >= 15).order_by(Articulo.descuento.desc())
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

@lapolar_bp.route('/lapolar/producto/<int:id>')
def productoLapolar(id):
    try:
        producto = db.session.query(Articulo).get(id)
        if producto:
            return render_template('detalle_producto_lapolar.html', producto=producto)
        else:
            return abort(404)
    except Exception as e:
        print("Error al obtener precios", e)
        return abort(500)
    finally:
        db.session.close()


@lapolar_bp.route('/api/lapolar/producto/<int:id>')
def apiProductoLapolar(id):
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
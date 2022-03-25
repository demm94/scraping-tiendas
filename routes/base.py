from flask import Blueprint, render_template, abort, url_for, redirect
import db
from models.Articulo import Articulo
from models.Precio import Precio

base_bp = Blueprint('base_bp', __name__, template_folder="templates")

@base_bp.route('/')
def index():
    return render_template('home.html')

@base_bp.route('/historial/producto/<id>')
def historial_producto(id):
    try:
        articulo = db.session.query(Articulo).get(id)
        if articulo:
            if articulo.tienda == "Falabella":
                return redirect(url_for('falabella_bp.productoFalabella', id=id))
            elif articulo.tienda == "Ripley":
                return redirect(url_for('ripley_bp.productoRipley', id=id))
            elif articulo.tienda == "Paris":
                return redirect(url_for('paris_bp.productoParis', id=id))
            elif articulo.tienda == "Abcdin":
                return redirect(url_for('abcdin_bp.productoAbcdin', id=id))
            elif articulo.tienda == "Lapolar":
                return redirect(url_for('lapolar_bp.productoLapolar', id=id))
            elif articulo.tienda == "Lider":
                return redirect(url_for('lider_bp.productoLider', id=id))
    except Exception as e:
        print("Error al obtener articulo", e)
        return abort(500)
    finally:
        db.session.close()
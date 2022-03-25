from flask import Blueprint, render_template, request, jsonify
import db
from models.Articulo import Articulo
from models.Favorito import Favorito

favoritos_bp = Blueprint('favoritos_bp', __name__, template_folder="templates")

@favoritos_bp.route('/favoritos')
def favoritos():
    return render_template('favoritos.html')

@favoritos_bp.route('/api/favoritos')
def apiFavoritos():
    try:
        res = db.session.query(Articulo, Favorito).filter(Articulo.id == Favorito.articulo_id).filter(Favorito.active == True).all()
        favoritos = [{
            "id": a.id,
            "nombre": a.nombre,
            "marca": a.marca,
            "tienda": a.tienda,
            "precio": a.last_precio,
            "mejor_precio": a.best_precio,
            "descuento": a.descuento,
            "url": a.url
        } for a, f in res]

        return jsonify(
            {
                "data": favoritos,
                "recordsTotal": len(favoritos),
                "recordsFiltered": len(favoritos),
                "draw": 1,
            }
        )
    except Exception as e:
        print("Error al obtener favoritos", e)
    finally:
        db.session.close()

@favoritos_bp.route('/api/favoritos/add', methods=['POST'])
def apiAddFavoritos():
    if request.method == "POST":
        data = request.get_json()
        if data:
            try:
                articulo = db.session.query(Articulo).get(data['articulo_id'])
                if articulo:
                    ## Agregar a favoritos
                    articulo_favorito = Favorito(articulo_id=data['articulo_id'])
                    db.session.add(articulo_favorito)
                    db.session.commit()

                    ## Agregar a favoritos
                    if articulo_favorito.id:
                        return jsonify({
                            "message": f"Artículo ID: {data['articulo_id']} agregado correctamente"
                        })
                else:
                    return jsonify({
                        "message": f"Artículo ID: {data['articulo_id']} no encontrado"
                    })
            except Exception as e:
                print(f"Error al recuperar articulo ID: { data['articulo_id'] }", e)
                return jsonify({
                    "message": "Internal Server Error"
                })
            finally:
                db.session.close()
        else:
            return jsonify({
                "message": "formato de datos incorrecto"
            })
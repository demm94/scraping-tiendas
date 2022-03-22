import db
from models.Articulo import Articulo
from models.Precio import Precio

if __name__ == '__main__':
    id = "MKF0V19CGX"
    producto = db.session.query(Articulo).get(id)
    print(producto)
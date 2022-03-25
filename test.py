import db
from models.Articulo import Articulo
from models.Precio import Precio
from sqlalchemy import delete

if __name__ == '__main__':
    id = "PROD_1153300"
    producto = db.session.query(Articulo).get(id)
    print(producto)
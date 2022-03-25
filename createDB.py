import db
from models.Articulo import Articulo
from models.Precio import Precio
from models.Favorito import Favorito

def run():
    pass

if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    run()
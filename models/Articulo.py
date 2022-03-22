import db

from sqlalchemy import Column, String, Float, Integer

class Articulo(db.Base):
    __tablename__ = 'articulo'
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    marca = Column(String, nullable=False)
    tienda = Column(String, nullable=False)
    url = Column(String, nullable=False)
    best_precio = Column(Float, nullable=False)
    last_precio = Column(Float, nullable=False)
    descuento = Column(Integer, nullable=False)

    def __init__(self, id, nombre, marca, tienda, url, best_precio, last_precio, descuento):
        self.id = id
        self.nombre = nombre
        self.marca = marca
        self.tienda = tienda
        self.url = url
        self.best_precio = best_precio
        self.last_precio = last_precio
        self.descuento = descuento

    def __repr__(self):
        return f'Articulo({self.id}, {self.nombre})'

    def __str__(self):
        return self.nombre
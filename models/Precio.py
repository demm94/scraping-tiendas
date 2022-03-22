from email.policy import default
from xmlrpc.client import DateTime
import db, datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime

class Precio(db.Base):
    __tablename__ = 'precio'
    id = Column(Integer, primary_key=True)
    articulo_id = Column(Integer, ForeignKey('articulo.id'))
    articulo = relationship('Articulo')
    valor = Column(Float, nullable=False)
    create_date = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, articulo_id, valor):
        self.articulo_id = articulo_id
        self.valor = valor

    def __repr__(self):
        return f'Precio({self.id}, {self.valor}'
        
    def __str__(self):
        return self.valor
from enum import unique
import db, datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean

class Favorito(db.Base):
    __tablename__ = 'favorito'
    id = Column(Integer, primary_key=True)
    articulo_id = Column(Integer, ForeignKey('articulo.id'), unique=True)
    articulo = relationship('Articulo')
    add_date = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=True)

    def __init__(self, articulo_id, active=True):
        self.articulo_id = articulo_id
        self.active = active

    def __repr__(self):
        return f'Precio({self.id}, {self.active}'
        
    def __str__(self):
        return self.id
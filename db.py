from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///tiendas.sqlite')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory) 
session = Session()

Base = declarative_base()
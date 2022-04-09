import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .model import Base

db_url = 'sqlite:///' + os.path.join(os.path.abspath(os.path.curdir), 'datebase.db')
engine = create_engine(db_url, echo=False)  # , echo=True)
# engine = create_engine('sqlite:///:memory:', echo=True)


Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

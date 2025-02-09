import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_user = os.environ.get('DB_USER', "postgres")
db_password = os.environ.get('DB_PASSWORD', "my_password")
db_host = os.environ.get('DB_HOST', "localhost")
db_port = os.environ.get('DB_PORT', "5432")
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres')
database_url = f'postgresql+psycopg2://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWORD")}@{os.environ.get("DB_HOST", "localhost")}:5432/{os.environ.get("DB_NAME")}'
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#engine = create_engine('sqlite:///ProjectDB.db', connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
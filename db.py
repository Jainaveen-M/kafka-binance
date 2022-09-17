from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker

username = 'root'
password = 'root12345'
host = 'localhost'
port = 3306
db_name = "binance"
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}",echo=True,pool_size=20, max_overflow=0)
    
Session = sessionmaker(bind=engine)
Inspect= sqlalchemy.inspect(engine)
    
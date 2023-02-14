import DataBase.connect as _database
import sqlalchemy.orm as _orm
import DataBase.Models as _models

_models._connect.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_Venue(db: _orm.Session):
   return db.query(_models.Venue).all()

def get_venue_id(db: _orm.Session,name:str):
   return db.query(_models.Venue.id).filter(_models.Venue.VenueName.like(f'{name}%')).first()  


def add_venue(db: _orm.Session, name:str):
    if not db.query(_models.Venue).filter(_models.Venue.VenueName.like(f'{name}%')).first():
        details = _models.Venue(
            VenueName=name,
        )
        db.add(details)
        db.commit()
        db.refresh(details) 
        return details.id
    else:
        return None
    
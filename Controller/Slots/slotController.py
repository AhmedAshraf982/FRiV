import DataBase.connect as _database
import sqlalchemy.orm as _orm
import DataBase.Models as _models
import DataBase.connect as _connect


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_Slot(db: _orm.Session):
   return db.query(_models.Slot).all()


def get_slot_id(name:str):
    id = None
    with _connect.engine.connect() as con:
        rs = con.execute(f"SELECT id\
                            from Slots\
                            where StartTime = '{name}'")
        for row in rs:
            id = row[0]
    
    return id

def add_slot(db: _orm.Session, start_slot:str, end_slot:str):
    if not db.query(_models.Slot).filter(_models.Slot.StartTime.like(start_slot)).first():
        details = _models.Slot(
            StartTime=start_slot,
            EndTime=end_slot,
        )
        db.add(details)
        db.commit()
        db.refresh(details)
        return details.id
    else:
        return None
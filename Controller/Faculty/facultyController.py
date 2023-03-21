import DataBase.connect as _connect
import sqlalchemy.orm as _orm
import DataBase.Models as _models
import datetime as dt

_models._connect.Base.metadata.create_all(bind=_connect.engine)

def get_db():
    db = _connect.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_faculty(db: _orm.Session):
   return db.query(_models.Faculty).all()


def createSchedule(db: _orm.Session, fID: int, day: str, sId: int, vId: int):
    details = _models.Schedule(
        facultyID = fID,
        Day = day,
        slotId = sId,
        venueId =  vId
    )
    db.add(details)
    db.commit()
    db.refresh(details)


def add_faculty_data(db: _orm.Session, facultyId:int , checkTim: str, checkOutTime: str, day:str, venueId: int,time:str):
    """
    this method will add a new record to database. and perform the commit and refresh operation to db
    :param db: database session object
    :param movie: Object of class schema.MovieAdd
    :return: a dictionary object of the record which has inserted
    """
    date = dt.datetime.strptime(day, "%d-%b-%Y")
    details = _models.Faculty_Time_Info(
        facultyId=facultyId,
        checkInTime=checkTim,
        checkOutTime=checkOutTime,
        time=time,
        VenueId=venueId,
        Date=date,
    )
    db.add(details)
    db.commit()
    db.refresh(details)
    return None

    

def get_faculty_id(name:str):
    id = None
    with _connect.engine.connect() as con:
        rs = con.execute(f"SELECT id\
                            from Faculty\
                            where Name = '{name}'")
        for row in rs:
            id = row[0]
    
    return id



def get_faculty_name(venueName: str, startTime: str, Day: str):
    verifyName = None
    endTime = None
    fId = None
    vId = None
    day = dt.datetime.strptime(Day, "%d-%b-%Y")
    day = dt.datetime.strftime(day, "%A").upper()
    print(day)
    
    with _connect.engine.connect() as con:
        rs = con.execute(f"SELECT f.Name, s.Day, sl.StartTime, sl.EndTime, v.VenueName, f.id, v.id\
                            from Schedule s JOIN Faculty f \
                            ON s.facultyId = f.id\
                            JOIN slots sl\
                            ON s.slotId = sl.id\
                            Join venue v\
                            On s.venueId = v.id where v.VenueName Like '{venueName}%'\
                            and sl.StartTime = '{startTime}' and s.Day = '{day}'")
        for row in rs:
            verifyName = row[0]
            endTime = row[3]
            fId = row[5]
            vId = row[6]

    return [verifyName,endTime, fId, vId]

    
def get_faculty_info(date: str):
    DateObj = dt.datetime.strptime(date, "%d-%b-%Y")
    DateObj = dt.datetime.strftime(DateObj, "%Y-%m-%d")
    data = []
    with _connect.engine.connect() as con:
        rs = con.execute(f"SELECT fti.id, f.Name,f.Email,f.FullName, v.VenueName, fti.Date, fti.checkInTime, fti.checkOutTime, fti.time \
                            from Faculty_Time_Info fti JOIN Faculty f ON fti.FacultyId = f.id \
                            JOIN Venue v ON v.id = fti.VenueId  where fti.Date='{DateObj}'")
        data = rs.fetchall()
       
    return data

def addFaculty(db: _orm.Session, firstName:str, email:str, fullName: str):
    if not findfacultyByFullName(db=db,Name=firstName, Email=None):
        details = _models.Faculty(
            Name=firstName,
            Email=email,
            FullName=fullName,
        )
        db.add(details)
        db.commit()
        db.refresh(details)
        return details.id
    return None
    

def findfacultyByFullName(db: _orm.Session, Name: str, Email: str):
    user = db.query(_models.Faculty).filter(_models.Faculty.Name.like(Name)).first()
    if user:
        if user.Email is None:
           user =  db.query(_models.Faculty).filter(_models.Faculty.Name.like(Name)).update({_models.Faculty.Email: Email}, synchronize_session=False)
           db.commit()
    return user
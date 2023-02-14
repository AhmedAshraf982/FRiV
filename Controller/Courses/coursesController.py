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

def get_course_id(name:str):
    id = None
    with _connect.engine.connect() as con:
        rs = con.execute(f"SELECT id\
                            from Courses\
                            where shortTitle = '{name}'")
        for row in rs:
            id = row[0]
    
    return id

def add_courses(db: _orm.Session, courseTitle:str, shortTitle:str, courseCode: str):
    if not db.query(_models.Courses).filter(_models.Courses.CourseCode.like(courseCode)).first():
        details = _models.Courses(
            Title=courseTitle,
            shortTitle=shortTitle,
            CourseCode=courseCode
        )
        db.add(details)
        db.commit()
        db.refresh(details)
        return details.id
    else:
        return None


def addFacultyCourse(db: _orm.Session, facultyId: int,courseId: int):
    isPresent = db.query(_models.Courses_Teachers).filter(_models.Courses_Teachers.course_id==courseId, _models.Courses_Teachers.teacher_id == facultyId).first()
    if not isPresent:
        details = _models.Courses_Teachers(
            teacher_id=facultyId,
            course_id=courseId
        )
        db.add(details)
        db.commit()
        db.refresh(details)
    
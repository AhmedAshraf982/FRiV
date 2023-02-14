import sqlalchemy as _sql

import DataBase.connect as _connect

class Slot(_connect.Base):
    __tablename__ = 'Slots'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    StartTime = _sql.Column(_sql.String, nullable=False)
    EndTime = _sql.Column(_sql.String, nullable=False)
    

class Venue(_connect.Base):
    __tablename__ = 'Venue'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    VenueName = _sql.Column(_sql.String, nullable=False)


class Courses(_connect.Base):
    __tablename__ = 'Courses'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    CourseCode = _sql.Column(_sql.String, nullable=False, unique=True)
    Title = _sql.Column(_sql.String, nullable=False)
    shortTitle = _sql.Column(_sql.String, nullable=False, unique=True)


class Faculty(_connect.Base):
    __tablename__ = 'Faculty'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    Name = _sql.Column(_sql.String, nullable=False)
    Email = _sql.Column(_sql.String)
    FullName = _sql.Column(_sql.String)



class FacultyInfo(_connect.Base):
    __tablename__ = 'FacultyInfo'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    facultyID = _sql.Column(_sql.Integer, _sql.ForeignKey('Faculty.id'))
    Present = _sql.Column(_sql.Integer)
    Absent = _sql.Column(_sql.Integer)


class Schedule(_connect.Base):
    __tablename__ = 'Schedule'
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    facultyID = _sql.Column(_sql.Integer, _sql.ForeignKey('Faculty.id'))
    Day = _sql.Column(_sql.String)
    slotId = _sql.Column(_sql.Integer, _sql.ForeignKey('Slots.id'))
    venueId =  _sql.Column(_sql.Integer, _sql.ForeignKey('Venue.id'))





class Courses_Teachers(_connect.Base):
    __tablename__ = 'Courses_Teachers'
    id = _sql.Column(_sql.Integer, primary_key=True,autoincrement=True, index=True)
    teacher_id = _sql.Column(_sql.Integer, _sql.ForeignKey('Faculty.id'))
    course_id = _sql.Column(_sql.Integer, _sql.ForeignKey('Courses.id'))
    
    


class Faculty_Time_Info(_connect.Base):
    __tablename__ = "Faculty_Time_Info"
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    facultyId = _sql.Column(_sql.Integer,  _sql.ForeignKey('Faculty.id'))
    checkInTime = _sql.Column(_sql.String)
    checkOutTime = _sql.Column(_sql.String)
    time = _sql.Column(_sql.String)
    VenueId = _sql.Column(_sql.Integer, _sql.ForeignKey('Venue.id'))
    Date = _sql.Column(_sql.DATE)

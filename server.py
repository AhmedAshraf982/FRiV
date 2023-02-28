import fastapi as _fastapi
import shutil
from typing import List
from video_editor import trim
from fastapi.middleware.cors import CORSMiddleware
from model.vggface import *
import sqlalchemy.orm as _orm 
from Controller.Slots import slotController 
from Controller.Venue import venueController
from Controller.Faculty import facultyController
from Controller.TimeTable import timetableController
from Controller.Courses import coursesController
import Schema.SlotSchema as _slotSchemas
import Schema.VenueSchema as _venueSchema
import Schema.FacultySchema as _facultySchema
import pandas as pd
import time
import os

app = _fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get/all/slots", response_model=List[_slotSchemas.Slot])
def getAllSlots(db: _orm.Session=_fastapi.Depends(slotController.get_db)):
    try:
        slots = slotController.get_all_Slot(db=db)
        return slots
    except Exception as e:
        raise _fastapi.HTTPException(
            status_code = 400, detail=str(e)
        )

@app.get("/get/all/venue", response_model=List[_venueSchema.Venue])
def getAllVenue(db: _orm.Session=_fastapi.Depends(venueController.get_db)):
    try:
        venues = venueController.get_all_Venue(db=db)
        return venues
    except Exception as e:
        raise _fastapi.HTTPException(
            status_code = 400, detail=str(e)
        )

@app.get("/get/all/faculty", response_model=List[_facultySchema.Faculty])
def getAllFaculty(db: _orm.Session=_fastapi.Depends(facultyController.get_db)):
    try:
        faculties = facultyController.get_all_faculty(db=db)
        return faculties
    except Exception as e:
        raise _fastapi.HTTPException(
            status_code = 400, detail=str(e)
        )



@app.get("/summary/faculty/{date}")
def getFacultySummary(date: str):
    return {"data":facultyController.get_faculty_info(date)}


@app.post("/add/timetable")
def addTimetable(file: _fastapi.UploadFile = _fastapi.File(),db: _orm.Session=_fastapi.Depends(facultyController.get_db),db1: _orm.Session=_fastapi.Depends(venueController.get_db),db2: _orm.Session=_fastapi.Depends(slotController.get_db),db3: _orm.Session=_fastapi.Depends(coursesController.get_db)):
    try:
        ext = file.filename.split(".")[1]

        with open(f"./data/timetable.{ext}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        timetableController.extract_data(f"./data/timetable.{ext}", db=db, db1=db1, db2=db2, db3=db3)

        os.remove(f"./data/timetable.{ext}")

        return {
            "status": True,
            "message": "Timetable added successfully"
        }
    except Exception as e:
        raise _fastapi.HTTPException(
            status_code = 400, detail=str(e)
        )

def addFacultyData(db: _orm.Session, firstName: str,lastName:str,email: str, path:str):
    user = facultyController.findfacultyByFullName(db=db, Name=firstName, Email=email)
    if user:    
        return { 
            "status" : False,
            "message":"Faculty is already available"
        }
    
    res = train(path, Name=firstName)
    os.remove(path)
    
    if len(res) == 1:
        facultyController.addFaculty(db=db, firstName=firstName, fullName=firstName+" "+lastName, email=email)
        return {
            "status": True,
            "message": "Faculty added successfully"
        }
    else:
        return {
            "status": False,
            "message": res[1]
        }

@app.post("/add/faculty")
def addFaculty(db: _orm.Session=_fastapi.Depends(facultyController.get_db), file: _fastapi.UploadFile = _fastapi.File(), firstName: str = _fastapi.Form(), email: str = _fastapi.Form(), lastName: str = _fastapi.Form()):
        ext = file.filename.split(".")[1]
        with open(f"./data/temp.{ext}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        path = f"./data/temp.{ext}"
        return addFacultyData(db=db, firstName=firstName, lastName=lastName,email=email,path=path)



@app.post("/add/faculty/files")
async def upload_File(db: _orm.Session=_fastapi.Depends(facultyController.get_db), file: _fastapi.UploadFile = _fastapi.File()):
    ext = file.filename.split(".")[1]

    with open(f"./data/facultyData.{ext}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_csv(f"./data/facultyData.{ext}")
    res = None
    for _, row in df.iterrows():
        filename = row["Picture"].split("\\")[-1]
        path = f"./data/{filename}"
        with open(row["Picture"], 'rb') as ifile:
            with open(path, 'wb') as ofile:
                data = ifile.read(1024 * 1024)
                while data:
                    ofile.write(data)
                    data = ifile.read(1024 * 1024)
        res = addFacultyData(db=db, firstName=row["FirstName"], lastName=row["LastName"],email=row["Email"],path=path)
        if res["status"] == False:
            return res
    return res

@app.post("/files")
async def create_file(file: _fastapi.UploadFile = _fastapi.File(), starttime: str = _fastapi.Form(), venue: str = _fastapi.Form(), day: str = _fastapi.Form(), db: _orm.Session=_fastapi.Depends(facultyController.get_db)):
        
        ext = file.filename.split(".")[1]
        
        with open(f"./data/destination.{ext}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        fps = int(trim("./data/destination.mp4"))
        
        facultyName,endtime = facultyController.get_faculty_name(venue,starttime,day)

        if facultyName is None:
            return {"status": False,
                    "message":"No Faculty Class on this venue and time"
                }

        facultyId = facultyController.get_faculty_id(facultyName)

        venueId = venueController.get_venue_id(db=db, name=venue)[0]

        data = run(facultyName, fps)

        if None in data:
            return {
                "status": False,
                "message":"Teacher is not present in the class"
            }
        _, minutes = data
        time_object = time.strptime(starttime, '%H:%M')
        th = time_object.tm_hour
        tm = time_object.tm_min

        tm = tm + int(minutes)
        if tm > 59:
            if th == 12:
                th = 1
            else:
                th += 1
            tm = tm - 60
        checkTim = str(th)+":"+str(tm)

        end_time = time.strptime(endtime, '%H:%M')
        eth = end_time.tm_hour
        etm = end_time.tm_min 


        end_data = last(facultyName, fps)
        if None in end_data:
            etm = etm - 10
            if etm == 0:
                if eth == 12:
                    eth = 11
                else:
                    eth -= 1
                etm = etm - 60
        else:
            _, end_minutes = end_data
            
            etm = etm - int(end_minutes)
            if etm == 0:
                if eth == 12:
                    eth = 11
                else:
                    eth -= 1
                etm = etm - 60
        
        checkOutTim = str(eth)+":"+str(etm)

        facultyController.add_faculty_data(db=db, facultyId=facultyId, checkTim=checkTim, checkOutTime=checkOutTim, day=day,venueId=venueId,time=f"{starttime}-{endtime}")

        return {
            "status": True,
            "message": "Processing Completed",
            "name": facultyName,
            "check-in": checkTim,
            "check-out": checkOutTim,
        }

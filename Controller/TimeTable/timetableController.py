import DataBase.connect as _connect
import sqlalchemy.orm as _orm
import DataBase.Models as _models
import datetime as dt
from collections import defaultdict
import pandas as pd
import openpyxl
import re
from Controller.Slots import slotController 
from Controller.Faculty import facultyController
from Controller.Venue import venueController
from Controller.Courses import coursesController

_models._connect.Base.metadata.create_all(bind=_connect.engine)
CourseList = set()
dic = {}

DEFAULTVALUE = "NOT PRESENT"



def extractSheetData(filename: str, sheetName: str):
    return pd.read_excel(filename, sheet_name=sheetName,engine='openpyxl').fillna(DEFAULTVALUE)

def extractFaculty(data):
    nameList = []
    for teacherName in data.split("("):
        if "Course Planning" not in teacherName:
            teacherName = re.sub(",", "", teacherName.split(")")[-1]).strip()
            if len(teacherName) > 1:
                nameList.append(teacherName.strip())
    return nameList


def extractCourseAndFaculty(dataFrame, dict_):
    columnList = ["Unnamed: 4", "Unnamed: 3", "Unnamed: 2", "Unnamed: 8"]
    value = None
    for i in columnList:
        for ind, j in enumerate(dataFrame[i][5:]):
            if j != DEFAULTVALUE and i == columnList[0]:
                j = j.strip()
                j = re.sub(". ",".",j)
                if j not in dict_.keys():
                    dict_[j] = {"Course-Title": "", "Course-Code": "", "Instructors": set()}
            elif i == columnList[1] and j != DEFAULTVALUE:
                dict_[re.sub(". ",".",dataFrame[columnList[0]][ind + 5].strip())]["Course-Title"] = j
            elif i == columnList[2] and j != DEFAULTVALUE:
                dict_[re.sub(". ",".",dataFrame[columnList[0]][ind + 5].strip())]["Course-Code"] = j
            elif i == columnList[3] and j != DEFAULTVALUE:
                tempList = extractFaculty(j)
                dict_[re.sub(". ",".",dataFrame[columnList[0]][ind + 5].strip())]["Instructors"].update(tempList)


def extractTimeTable(dataFrame, dict_):
    keyList = list(dataFrame.keys())
    venueList = None
    tempInd = 0
    prevFaculty = None
    prevCourse = None
    count = 0
    courseCode = None
    dict_[keyList[0]] = {}
    for ind, k in enumerate(keyList):
        for ind1, value in enumerate(dataFrame[k][3:]):
            if value != DEFAULTVALUE and k == keyList[0] and value != "LABS":
                if value != "EE MPI Lab":
                    cleaningValue = "".join(" ".join(value.split(" ")[0:2]).split("(")[0])
                    if cleaningValue not in dict_[keyList[0]].keys():
                        dict_[keyList[0]][cleaningValue] = []
                else:
                    dict_[keyList[0]][value] = [{}]
            elif k != keyList[0]:
                if venueList is None:
                    venueList = list(dict_[keyList[0]].keys())
                startTime, endTime = dataFrame[k][1].split("-")
                if len(startTime) == 1:
                    startTime = startTime.rjust(2, '0')
                if len(startTime) == 2:
                    startTime = startTime.ljust(3, ':')
                    startTime = startTime.ljust(5, '0')
                if len(endTime) < 5:
                    endTime = endTime.rjust(5, '0')
                if value != DEFAULTVALUE and value != "RESERVED FOR EE" and value != "RESERVED FOR BBA":
                    splitValue = value.split("\n")
                    courseCode = splitValue[0].split(" ")
                    if "Lab" in courseCode:
                        courseCode[0] = courseCode[0].upper()
                        courseCode = "-".join(courseCode[0:2])
                    else:
                        courseCode = re.sub(". ", ".", courseCode[0].strip())
                    value = splitValue[1]
                if value != "LABS" and value != "RESERVED FOR EE" and value != "RESERVED FOR BBA":
                    # if courseCode != None and "Lab" in courseCode:
                    #     count = 1
                    #     prevCourse = courseCode
                    #     prevFaculty = value
                    dict12 = {"Slots": {"StartTime": startTime, "EndTime": endTime}, "Faculty": value,
                              "CourseCode": courseCode, "FACULTY-FULLNAME": set()}
                    courseCode = None
                if dataFrame[keyList[0]][ind1 + 3] != "LABS":
                    if tempInd != 0:
                        if tempInd > len(venueList) - 1:
                            tempInd = 0
                        ind1 = tempInd
                        tempInd = tempInd + 1
                    dict_[keyList[0]][venueList[ind1]].append(dict12.copy())
                else:
                    tempInd = ind1




def extract_data(path, db: _orm.Session,db1: _orm.Session,db2: _orm.Session, db3: _orm.Session):
    
    wb = openpyxl.load_workbook(path)
    sheetNames = wb.sheetnames
    
    
    sheetDataDictionary = defaultdict(lambda: DEFAULTVALUE)
    courseAndFaculty = defaultdict(lambda: DEFAULTVALUE)
    timeTable = defaultdict(lambda: DEFAULTVALUE)

    for sheetName in sheetNames:
        if "BATCH" in sheetName:
            sheetDataDictionary[sheetName] = extractSheetData(path, sheetName)
            extractCourseAndFaculty(sheetDataDictionary[sheetName], courseAndFaculty)
        elif "SPRING" not in sheetName and "Course" not in sheetName:
            sheetDataDictionary[sheetName] = extractSheetData(path, sheetName)
            extractTimeTable(sheetDataDictionary[sheetName], timeTable)


    for key, value in timeTable.items():
        for k2, value2 in value.items():
            for v in value2:
                if "CourseCode" in v.keys() and v["CourseCode"] is not None:
                    courseCode = v["CourseCode"]
                    if courseAndFaculty[courseCode] != DEFAULTVALUE:
                        Faculties = courseAndFaculty[courseCode]["Instructors"]
                        for faculty in Faculties:
                            if v["Faculty"].strip().upper() in faculty.strip().upper():
                                v["FACULTY-FULLNAME"].add(faculty.strip())
                        if len(Faculties) == 1:
                            v["FACULTY-FULLNAME"].add(list(Faculties)[0].strip())

    

    venueList = list(timeTable["FRIDAY"].keys())

    for venue in venueList:
        _ = venueController.add_venue(db=db1, name=venue)
        

    for i in timeTable["FRIDAY"][venueList[0]]:
        a,b =i["Slots"]["StartTime"], i["Slots"]["EndTime"]
        _ = slotController.add_slot(db=db2, start_slot=a, end_slot=b)
        

    for key, value in timeTable.items():
        for k1, v1 in value.items():
            for v in v1:
                if v.get("Faculty") != "NOT PRESENT" and v.get("Faculty") is not None:
                    if v.get("FACULTY-FULLNAME") is not None and len(v.get("FACULTY-FULLNAME")) > 0:
                        _ = facultyController.addFaculty(db=db, firstName=v["Faculty"].strip(), email=None, fullName=list(v["FACULTY-FULLNAME"])[0])
                    else:
                        _ = facultyController.addFaculty(db=db, firstName=v["Faculty"].strip(), email=None, fullName=None)
                    

    for key, value in courseAndFaculty.items():
        coursesController.add_courses(db=db3,courseCode=value["Course-Code"], shortTitle=key, courseTitle=value["Course-Title"])

    for key, value in timeTable.items():
        for k1, v1 in value.items():
            for v in v1:
                if v.get("Faculty") != "NOT PRESENT" and v.get("Faculty") is not None:
                    res = facultyController.get_faculty_id(v["Faculty"].strip())
                    if res is not None:
                        a = i["Slots"]["StartTime"] 
                        sId = slotController.get_slot_id(v["Slots"]["StartTime"])
                        vId = venueController.get_venue_id(db=db1,name=k1)[0]
                        facultyController.createSchedule(db=db, fID= res, day= key, sId=sId, vId=vId)
                        
                        

    for key, value in timeTable.items():
        for k1, v1 in value.items():
            for v in v1:
                if v.get("Faculty") != "NOT PRESENT" and v.get("Faculty") is not None:
                    res = facultyController.get_faculty_id(v["Faculty"].strip())
                    if res is not None:
                        res1 = coursesController.get_course_id(v["CourseCode"])
                        if res1 is not None:
                            coursesController.addFacultyCourse(db=db3, facultyId=res, courseId=res1)


    
    





import pydantic as _pydantic

class FacultyInfo(_pydantic.BaseModel):
    id: int
    faculty: str
    exntryTime: str
    exitTime: str
    Venue: str
    date: str
    
    class Config:
        orm_mode = True


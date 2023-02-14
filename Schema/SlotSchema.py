import pydantic as _pydantic

class Slot(_pydantic.BaseModel):
    id: int
    StartTime: str
    EndTime: str

    class Config:
        orm_mode = True


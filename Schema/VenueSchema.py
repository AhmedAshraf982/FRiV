import pydantic as _pydantic

class Venue(_pydantic.BaseModel):
    id: int
    VenueName: str

    class Config:
        orm_mode = True


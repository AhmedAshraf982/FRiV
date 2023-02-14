import pydantic as _pydantic

class Faculty(_pydantic.BaseModel):
    id: int
    Name: str

    class Config:
        orm_mode = True


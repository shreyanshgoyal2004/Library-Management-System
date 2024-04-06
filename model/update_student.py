from pydantic import BaseModel

class updobt(BaseModel):
    country: str|None = None
    city: str|None = None

class updateItem(BaseModel):
    name: str|None = None
    age: int|None = None
    address: updobt|None = None
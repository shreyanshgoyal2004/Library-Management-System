from pydantic import BaseModel

# Define a data model
class obt(BaseModel):
    city: str
    country: str

class Item(BaseModel):
    name: str
    age: int
    address: obt
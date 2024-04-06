from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from dotenv import dotenv_values
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Annotated

config = dotenv_values(".env")

app = FastAPI()

# connect to Mongodb

client = MongoClient(config["MONGODB_CONNECTION_URI"])
db = client[config["DB_NAME"]]
collection = db[config["COLLECTION_NAME"]]

print("Connected to Mongodb")


@app.get("/")
def home():
    return {"Hello world"}

# Define a data model
class obt(BaseModel):
    city: str
    country: str

class Item(BaseModel):
    name: str
    age: int
    address: obt

class updobt(BaseModel):
    country: str|None = None
    city: str|None = None

class updateItem(BaseModel):
    name: str|None = None
    age: int|None = None
    address: updobt|None = None

# Define route to create an item

@app.post("/students/")
async def create_student(item: Item):
    data = item.dict()
    result = collection.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/students")
async def get_student(country:str|None=None, age: Annotated[int|None, Query(ge=0)]=None):
    query = {}
    if country:
        query.update({"country":country})
    if age:
        query.update({"age": {"$gte":age}})
                     
    item = list(collection.find(query, {"_id":0}))
    if item:
        return item
    else:
        return "Name or age is required"



# Define route to get an student by ID
@app.get("/students/{students_id}")
async def read_item(students_id: str):
    # return type(students_id)
    try:
        objectinstance = ObjectId(students_id)
        item = collection.find_one({"_id": objectinstance},{"_id":0})
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        # raise HTTPException(status_code=500, detail="Internal server error")
        return e
    
@app.patch("/students/{students_id}")
async def update_item(students_id: str, upd: updateItem|None = None):
    # return upd
    try:
        # Check if student exists
        objectinstance = ObjectId(students_id)
        existing_student = collection.find_one({"_id": objectinstance},{"_id":0})
        # return existing_student["address"]["country"]
        if not existing_student:
            raise HTTPException(status_code=404, detail="student not found")
        
        # Construct update fields
        # return existing_student
        if upd.name:
            existing_student["name"] = upd.name
        if upd.age:
            existing_student["age"] = upd.age
        if upd.address and upd.adddress.country:
            existing_student["address"]["country"] = upd.address.country
        if upd.address and upd.address.city:
            existing_student['address']['city'] = upd.address.city
        
        # return existing_student
        # Update item
        updated_item = {"$set": existing_student}
        objectinstance = ObjectId(students_id)
        collection.update_one({"_id": objectinstance}, updated_item)
        
        return {"message": "student updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=204, detail="Unable to update")
    
@app.delete("/students/{students_id}")
def delete_item(students_id: str):
    try:
        # Check if student exists
        student = collection.find_one({"_id": ObjectId(students_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Delete student
        collection.delete_one({"_id": ObjectId(students_id)})
        
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


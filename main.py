from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query, status
from typing import Annotated
from model.create_student import Item
from model.update_student import updateItem
from db import collection

app = FastAPI()

# @app.get("/")
# def home():
#     return {"Hello world"}


# Define route to create an item

@app.post("/students/", status_code=status.HTTP_201_CREATED, description= "API to create a student in the system. All fields are mandatory and required while creating the student in the system.")
async def create_students(item: Item):
    data = item.dict()
    result = collection.insert_one(data)
    return {"id": str(result.inserted_id)}


@app.get("/students/", status_code=status.HTTP_200_OK, description="An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.")
async def list_students(country:str|None=None, age: Annotated[int|None, Query(ge=0)]=None):
    query = {}
    if country:
        query.update({"address.country":country})
    if age:
        query.update({"age": {"$gte":age}})
                     
    item = list(collection.find(query, {"_id":0}))
    if item:
        return item
    else:
        return "Name or age is required"



# Define route to get an student by ID

@app.get("/students/{students_id}", status_code=status.HTTP_200_OK)
async def fetch_students(students_id: str):
    # return type(students_id)
    try:
        objectinstance = ObjectId(students_id)
        item = collection.find_one({"_id": objectinstance},{"_id":0})
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.patch("/students/{students_id}", status_code=status.HTTP_204_NO_CONTENT, description="API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.")
async def update_students(students_id: str, upd: updateItem|None = None):
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
    
@app.delete("/students/{students_id}", status_code=status.HTTP_200_OK)
def delete_students(students_id: str):
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


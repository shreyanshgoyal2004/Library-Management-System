from fastapi import FastAPI, HTTPException, Header, Depends, status, Query
from typing import Annotated
from model.create_student import Item
from model.update_student import updateItem
from db import collection
from datetime import datetime, timedelta
from redis import Redis
from bson.objectid import ObjectId
from dotenv import dotenv_values
import os

app = FastAPI()

config = dotenv_values(os.getcwd() + "/.env")

# Redis connection
password = config['REDIS_PASSWORD']
redis = Redis(host='redis-14380.c258.us-east-1-4.ec2.redns.redis-cloud.com', port=14380, password=password, db=0)
print(redis.ping())

# getting user_id from header
def get_user_id(user_id: str = Header(None)):
    if user_id:
        return user_id
    else:
        raise HTTPException(status_code=400, detail="User-Id header is missing")

# getting rate of that id if it present in redis db
async def get_rate(redis: Redis, user_id: str):
    return int(redis.get(f"rate_limit:{user_id}") or 0)

# function to add new user with count 1
async def add_rate(redis: Redis, user_id: str, count: int):
    redis.set(f"rate_limit:{user_id}", count, ex=86400)

# function to increase count of the existing user
async def update_rate(redis: Redis, user_id: str):
    redis.incr(f"rate_limit:{user_id}")

# function to not allow user to acces route if they exceed a particular rate limit
# async def check_rate_limit(x_user_id: str = Depends(get_user_id), rate: int = Depends(get_rate)) -> None:
#     if rate >= 3:
#         raise HTTPException(status_code=429, detail="Rate limit exceeded")

@app.middleware("http")
async def add_rate_limit_header(request, call_next):
    user_id = request.headers.get("user_id", None)
    if not redis.get(f"rate_limit:{user_id}"):
        # rate = await get_rate(redis, user_id)
        # await check_rate_limit(x_user_id=user_id, rate=rate)
        await add_rate(redis, user_id,1)
    else:
        rate = await get_rate(redis, user_id)
        await update_rate(redis,user_id)
    response = await call_next(request)
    return response

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
    try:
        # Check if student exists
        objectinstance = ObjectId(students_id)
        existing_student = collection.find_one({"_id": objectinstance},{"_id":0})
        if not existing_student:
            raise HTTPException(status_code=404, detail="student not found")
        
        # Construct update fields
        if upd.name:
            existing_student["name"] = upd.name
        if upd.age:
            existing_student["age"] = upd.age
        if upd.address and upd.adddress.country:
            existing_student["address"]["country"] = upd.address.country
        if upd.address and upd.address.city:
            existing_student['address']['city'] = upd.address.city
        
        # Update student
        updated_item = {"$set": existing_student}
        objectinstance = ObjectId(students_id)
        collection.update_one({"_id": objectinstance}, updated_item)
        
        return {"message": "student updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=422, detail="Validation error")
    
@app.delete("/students/{students_id}", status_code=status.HTTP_200_OK)
async def delete_students(students_id: str):
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

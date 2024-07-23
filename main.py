from fastapi import FastAPI,status,HTTPException,Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime,timedelta
from typing import Dict
from jose import jwt,JWTError
from pymongo import MongoClient
from sendMail import send_with_template
from fastapi.middleware.cors import CORSMiddleware

import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["users"].verifyData


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(email:str,response:Response):
    user = db.find_one({"email":email})
    if(not user):
        response.status_code=status.HTTP_404_NOT_FOUND
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No user found")
    if(not db.find_one({"access_token":{"$exists":True}})):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized")
    
    decoded_user = jwt.decode(user["access_token"],os.getenv("JWT_SECRET"),algorithms="HS256")
    if(decoded_user["exp"] > int(round(datetime.now().timestamp()))):
        response.status_code = status.HTTP_200_OK
        return HTTPException(status_code=status.HTTP_200_OK,detail={"message":"Successful login","token":user["access_token"]})
    
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized")


@app.post("/generate_token")
def start(data:Dict):
    info = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=2)
    info.update({"exp":expire})
    token = jwt.encode(info,os.getenv("JWT_SECRET"),algorithm="HS256")

    isVerifiedUser = db.find_one({"email":data["email"]})
    if(isVerifiedUser and isVerifiedUser["exp"] > int(round(datetime.now().timestamp()))):
        return JSONResponse({"success":False,"message":"Link is already sent to your gmail , new link will be generated after 2 mins."},status_code=503)
    elif(isVerifiedUser):
        db.update_one({"email":data["email"]},{"$set":{"exp":info["exp"]}})
    else:
        db.insert_one(info)
    return JSONResponse({"token":token})

    
@app.post("/sendMail")
async def sendMail(token:str):
    decoded_user = jwt.decode(token,os.getenv("JWT_SECRET"),algorithms="HS256")
    email = decoded_user["email"]
    await send_with_template(token,email)
    return True


@app.get("/verify")
def verify(token:str):
    try:
        user = jwt.decode(token,os.getenv("JWT_SECRET"),algorithms="HS256")
        expire = datetime.utcnow() + timedelta(hours=24)
        user.update({"exp":expire})
        token = jwt.encode(user,os.getenv("JWT_SECRET"),algorithm="HS256")
        db.update_one({"email":user["email"]},{"$set":{"access_token":token}})

        return True
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Timeout , generate new verify link again"
        )

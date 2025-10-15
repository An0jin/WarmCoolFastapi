from pydantic import BaseModel
from datetime import date
from typing import Optional
class Chat(BaseModel):
    token:str
    msg:str

class LLM(BaseModel):
    token:str
    msg:str
    
class User(BaseModel):
    user_id:str
    pw:str
    name:str
    year:int
    gender:str
    version:float
    platform:str
    
class Update(BaseModel):
    token:str
    pw:str
    name:str
    year:int
    gender:str

class Login(BaseModel):
    user_id:str
    pw:str
    platform:str
    version:float
class Lipstick(BaseModel):
    token:Optional[str]=None
    hex_code:str
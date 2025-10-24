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
    email:str
    gender:str
    
class Update(BaseModel):
    token:str
    pw:str
    name:str
    email:str
    gender:str

class Login(BaseModel):
    user_id:str
    pw:str

class Lipstick(BaseModel):
    token:Optional[str]=None
    hex_code:str

class Email(BaseModel):
    email:str
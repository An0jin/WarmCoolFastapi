from pydantic import BaseModel
from datetime import date
from typing import Optional
class Chat(BaseModel):
    token:str
    msg:str
    color_id:str

class LLM(BaseModel):
    token:str
    msg:str
    
class User(BaseModel):
    pw:str
    name:str
    email:str
    
class Update(BaseModel):
    token:str
    pw:str
    name:str

class Login(BaseModel):
    email:str
    pw:str

class Lipstick(BaseModel):
    token:Optional[str]=None
    hex_code:str

class Email(BaseModel):
    email:str
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
    sex:str
    year:str
    
class User(BaseModel):
    pw:str
    name:str
    email:str
    
class Update(BaseModel):
    token:str
    pw:Optional[str]=None
    name:Optional[str]=None
    sex:str
    year:int

class Login(BaseModel):
    email:str
    pw:str

class Lipstick(BaseModel):
    token:str
    hex_code:str

class Email(BaseModel):
    email:str
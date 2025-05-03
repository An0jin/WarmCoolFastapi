from pydantic import BaseModel
from datetime import date
from typing import Optional
class Chat(BaseModel):
    user_id:str
    msg:str
    
class User(BaseModel):
    user_id:str
    pw:Optional[str]=None
    name:Optional[str]=None
    year:Optional[int]=None
    gender:Optional[str]=None

class Login(BaseModel):
    user_id:str
    pw:str

class Lipstick(BaseModel):
    user_id:str
    hex_code:str
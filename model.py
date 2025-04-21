from pydantic import BaseModel
from datetime import date

class Chat(BaseModel):
    user_id:str
    msg:str
class User(BaseModel):
    user_id:str
    pw:str
    name:str
    birthday:date
    gender:str
class Login(BaseModel):
    user_id:str
    pw:str
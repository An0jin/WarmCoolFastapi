import hashlib
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()
from jose import JWTError,jwt

def connect():
    """데이터베이스에 접근하는 함수"""
    return psycopg2.connect(host=os.getenv("host"),
                            port=int(os.getenv("port")),
                            user=os.getenv("user"),
                            password=os.getenv("password"),
                            dbname=os.getenv("dbname"))


def to_response(x):
    """응답을 JSON 형식으로 변환하는 함수"""
    if isinstance(x, pd.DataFrame):
        return {"result": x.to_dict(orient="records")}
    elif hasattr(x, 'tolist'):  # NumPy 배열 처리
        return {"result": x.tolist()}
    else:
        return {"result": x}


def hashpw(pw):
    """패스워드를 해싱하는 함수"""
    c = ord(pw[-1])
    for i in range(c % 5):
        func = hashlib.blake2b if bool(i % 2) else hashlib.sha256
        pw = func(pw.encode()).hexdigest()
    return pw

class JWT:
    @staticmethod
    def encode(user_id):
        return jwt.encode({'user_id':user_id}, os.getenv("jwtSecret"), algorithm='HS256')
    @staticmethod
    def decode(token):
        try:
            return jwt.decode(token, os.getenv("jwtSecret"), algorithms=['HS256'])['user_id']
        except:
            return None


class LipstickLLM:
    def __init__(self,api_key):
        self.client = genai.Client(api_key=os.getenv("gemini"))
    def invoke(self,text,colors):
        result = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
        config={"tools": [{"google_search": {}}],
        "system_instruction":f"You're given a situation where you must choose a lipstick color from {colors}. Please respond with a color code, such as #ffffff, and avoid any other answers. Furthermore, if the answer isn't readily available (e.g., 'What lipstick color would be appropriate for an idol concert'), you must use the web search function."}
        )
        return result.text

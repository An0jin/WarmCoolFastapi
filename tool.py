import hashlib
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()
from jose import JWTError,jwt
from email.mime.text import MIMEText
import smtplib
from google import genai


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
    """
    패스워드를 해싱합니다.
    """
    return hashlib.sha256(pw.encode()).hexdigest()

class JWT:
    @staticmethod
    def encode(email):
        return jwt.encode({'email':email}, os.getenv("jwtSecret"), algorithm='HS256')
    @staticmethod
    def decode(token):
        try:
            return jwt.decode(token, os.getenv("jwtSecret"), algorithms=['HS256'])['email']
        except:
            return None


class LipstickLLM:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("gemini"))
        
    def invoke(self,text,colors):
        result = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
        config={"tools": [{"google_search": {}}],
        "system_instruction":f"You're given a situation where you must choose a lipstick color from {colors}. Please respond with a color code, such as #ffffff, and avoid any other answers. Furthermore, if the answer isn't readily available (e.g., 'What lipstick color would be appropriate for an idol concert'), you must use the web search function."}
        )
        return result.text

def SendEmail(email,subject,body):
    my_email = "an0jin0106@gmail.com"
    my_password = os.getenv("stmplibpw")
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = my_email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as conn: # 표준 포트 587 사용
            conn.starttls()
            conn.login(user=my_email, password=my_password)
            conn.send_message(msg, from_addr=my_email, to_addrs=[email])
            print("이메일 전송 성공: UTF-8 인코딩 처리 완료")
    except smtplib.SMTPAuthenticationError:
        print("오류: SMTP 인증 실패. G메일 2단계 인증 및 앱 비밀번호 사용 여부를 확인하세요.")
    except Exception as e:
        print(f"오류 발생: {e}")
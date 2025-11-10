from fastapi import APIRouter,Form
from tool import *
import pandas as pd
from model import *
import psycopg2.errors as errors
from tool import JWT, SendEmail


chat = APIRouter(tags=['chat'], prefix='/chat')
user = APIRouter(tags=['user'], prefix='/user')

@user.get("/{token}")
def get_user(token: str):
    try:
        email=JWT.decode(token)
        print("이메일 : ",email)
        with connect() as conn:
            df=pd.read_sql('select * from "user" left join lipstick on "user".hex_code =lipstick.hex_code where email=%s',conn,params=[email,])
        print("df : ",df)
        df['token']=token
        return df.to_dict(orient="records")[0]
    except Exception as e:
        return to_response(str(e))
@chat.get("/{color}")
def get_chat(color: str):
    try:
        with connect() as conn:
            df=pd.read_sql('''SELECT chat.chat_id, "user".name, chat.msg
                                FROM "user"
                                INNER JOIN chat ON "user".email = chat.email
                                INNER JOIN lipstick ON "user".hex_code = lipstick.hex_code
                                INNER JOIN color ON lipstick.color_id = color.color_id
                                WHERE color.color_id = %s
                                ORDER BY chat.time;
        ''',conn,params=[color,])
        return to_response(df)
    except Exception as e:
        return to_response(str(e))

@chat.post("")
def post_chat(chat:Chat=Form(...)):
    try:
        with connect() as conn:
            cursor=conn.cursor()
            cursor.execute("insert into chat(email,msg,color_id) values(%s,%s,%s)",vars=[JWT.decode(chat.token),chat.msg,chat.color_id])
            conn.commit()
        return 
    except Exception as e:
        return to_response(str(e))

@user.post("")
def post_user(user:User=Form(...)):
    response={}
    try:
        response["token"]=JWT.encode(user.email)
        with connect() as conn:
            cursor=conn.cursor()
            try:
                var=user.email,hashpw(user.pw),user.name
                cursor.execute('insert into "user"(email,pw,name) values (%s,%s,%s)',var)
                conn.commit()
                
                SendEmail(user.email,'''안녕하세요, Toniverse에 오신 것을 진심으로 환영합니다!

당신만의 퍼스널컬러와 상황에 맞는 AI 기반 가상 메이크업 서비스를 이제 직접 경험하실 수 있습니다.

Toniverse는 최신 AI와 AR 기술을 활용해,
✓ 나에게 가장 잘 어울리는 컬러와 스타일을 손쉽게 추천해주며
✓ 언제 어디서나 다양한 뷰티 시뮬레이션을 즐기고
✓ 유저들과 뷰티 경험을 함께 나눌 수 있는 글로벌 커뮤니티를 제공합니다.

지금 바로 메이크업 시뮬레이션을 시작하고,  
나만의 컬러풀한 변신을 경험해보세요!

문의 및 피드백은 언제든 환영합니다.  
함께 Toniverse를 만들어가요!

Toniverse 개발자 드림
                ''')
            except errors.UniqueViolation:
                response["result"]="이미 존재하는 이메일입니다"
                return response
            except Exception as e:
                response["result"]="개발자 오류 : {e}"
                return response
            response["result"]="Sign up complete"
            return response
    except Exception as e:
        response["result"]=f"개발자 오류 : {e}"
        return response

@user.put("")
def put_user(update:Update):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('UPDATE "user" SET pw=%s, name=%s WHERE email=%s',
                            (hashpw(update.pw), update.name,  JWT.decode(update.token)))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

@user.put("/lipstick")
def put_user_lipstick(lipstick:Lipstick):
    try:
        email=JWT.decode(lipstick.token)
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('update "user" set hex_code=%s where email=%s',(lipstick.hex_code,email))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))


@user.delete("/{token}")
def delete_user(token:str):
    try:
        email=JWT.decode(token)
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('delete  from chat where email=%s; delete  from "user" where email=%s;',
                               (email, email))
                conn.commit()
                result="Deleted" if cursor.rowcount>0 else "Does not exist"
                return to_response(result)
            except Exception as e: 
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

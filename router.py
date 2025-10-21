from fastapi import APIRouter,Form
from tool import *
import pandas as pd
from model import *
import psycopg2.errors as errors
from tool import JWT


chat = APIRouter(tags=['chat'], prefix='/chat')
user = APIRouter(tags=['user'], prefix='/user')

@chat.get("/{color}")
def get_chat(color: str):
    try:
        with connect() as conn:
            df=pd.read_sql('''SELECT chat.chat_id, "user".name, chat.msg
                                FROM "user"
                                INNER JOIN chat ON "user".user_id = chat.user_id
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
            cursor.execute("insert into chat(user_id,msg) values(%s,%s)",vars=[JWT.decode(chat.token),chat.msg])
        return 
    except Exception as e:
        return to_response(str(e))

@user.post("")
def post_user(user:User=Form(...)):
    response={}
    try:
        response["token"]=JWT.encode(user.user_id)
        with connect() as conn:
            cursor=conn.cursor()
            try:
                var=user.user_id,hashpw(user.pw),user.name,hashpw(user.email),user.gender
                cursor.execute('insert into "user"(user_id,pw,name,email,gender) values (%s,%s,%s,%s,%s)',var)
                conn.commit()
            except errors.UniqueViolation:
                response["result"]="이미 존재하는 아이디 혹은 이메일입니다"
                return response
            except errors.CheckViolation:
                response["result"]="성별을 다시 입력해주세요"
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
                cursor.execute('UPDATE "user" SET pw=%s, name=%s, email=%s, gender=%s WHERE user_id=%s',
                            (hashpw(update.pw), update.name, hashpw(update.email), update.gender, JWT.decode(update.token)))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

@user.put("/lipstick")
def put_user_lipstick(lipstick:Lipstick):
    try:
        user_id=JWT.decode(lipstick.token)
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('update "user" set hex_code=%s where user_id=%s',(lipstick.hex_code,user_id))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))


@user.delete("/{token}")
def delete_user():
    try:
        user_id=JWT.decode(token)
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('delete  from chat where user_id=%s; delete  from "user" where user_id=%s;',
                               (user_id, user_id))
                conn.commit()
                result="Deleted" if cursor.rowcount>0 else "Does not exist"
                return to_response(result)
            except Exception as e: 
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

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
            cursor.execute("insert into chat(user_id,msg) values(%s,%s)",vars=[JWT.decode(chat.token)['user_id'],chat.msg])
        return 
    except Exception as e:
        return to_response(str(e))

@user.post("")
def post_user(user:User=Form(...)):
    try:
        with connect() as conn:
            cursor=conn.cursor()
            try:
                var=JWT.decode(user.token)['user_id'],hashpw(user.pw),user.name,user.year,user.gender
                cursor.execute('insert into "user"(user_id,pw,name,year,gender) values (%s,%s,%s,%s,%s)',var)
                conn.commit()
            except errors.UniqueViolation:
                return to_response("Already exists")
            except errors.CheckViolation:
                return to_response("Please enter a valid gender")
            except Exception as e:
                return to_response(f"Developer error : {e}")
            return to_response("Sign up complete")
    except Exception as e:
        return to_response(str(e))

@user.put("")
def put_user(user:User):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('UPDATE "user" SET pw=%s, name=%s, year=%s, gender=%s WHERE user_id=%s',
                            (hashpw(user.pw), user.name, user.year, user.gender, JWT.decode(user.token)['user_id']))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

@user.put("/lipstick")
def put_user_lipstick(lipstick:Lipstick):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('update "user" set hex_code=%s where user_id=%s',(lipstick.hex_code,JWT.decode(lipstick.token)['user_id']))
                conn.commit()
                return to_response("Modified")
            except Exception as e:
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))


@user.delete("/{id}")
def delete_user(id: str):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('delete  from chat where user_id=%s;',(id,))
                cursor.execute('delete  from "user" where user_id=%s;',(id,))
                conn.commit()
                result="Deleted" if cursor.rowcount>0 else "Does not exist"
                return to_response(result)
            except Exception as e: 
                return to_response(f"Error : {e}")
    except Exception as e:
        return to_response(str(e))

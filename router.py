from fastapi import APIRouter,Form
from db_response import *
import pandas as pd
from model import *
import psycopg2.errors as errors
# 라우터 정의 (기능별 분리)
chat = APIRouter(tags=['chat'], prefix='/chat')            # 채팅 기능 관련
user = APIRouter(tags=['user'], prefix='/user')            # 사용자 정보 관련

# ====================[ 채팅 기능 ]====================

# 특정 퍼스널 컬러 그룹의 채팅 내용 불러오기
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

# 채팅 메시지 추가
@chat.post("/")
def post_chat(chat:Chat=Form(...)):
    try:
        with connect() as conn:
            cursor=conn.cursor()
            cursor.execute("insert into chat(user_id,msg) values(%s,%s)",vars=[chat.user_id,chat.msg])
        return 
    except Exception as e:
        return to_response(str(e))

# ====================[ 사용자 기능 ]====================

# 사용자 정보 추가
@user.post("/")
def post_user(user:User=Form(None)):
    try:
        with connect() as conn:
            cursor=conn.cursor()
            try:
                var=user.user_id,hash(user.pw),user.name,user.year,user.gender
                cursor.execute('insert into "user"(user_id,pw,name,year,gender) values (%s,%s,%s,%s,%s)',var)
            except errors.UniqueViolation:
                return to_response("이미 존재하는 아이디 입니다")
            except errors.CheckViolation:
                return to_response("남자 여자 라고만 입력해주세요")
            except Exception as e:
                return to_response(f"개발자가 {e}을 실수했어요")
            return to_response("가입 완료")
    except Exception as e:
        return to_response(str(e))

# 유저 정보 변경
@user.put("/")
def put_user(user:User):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('UPDATE "user" SET pw=%s, name=%s, year=%s, gender=%s WHERE user_id=%s',
                            (user.pw, user.name, user.year, user.gender, user.user_id))
                conn.commit()
                return to_response("수정 완료")
            except Exception as e:
                return to_response(f"에러 : {e}")
    except Exception as e:
        return to_response(str(e))

# 립스틱 정보 변경
@user.put("/lipstick")
def put_user_lipstick(lipstick:Lipstick):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('update "user" set hex_code=%s where user_id=%s',(lipstick.hex_code,lipstick.user_id))
                conn.commit()
                return to_response("수정 완료")
            except Exception as e:
                return to_response(f"에러 : {e}")
    except Exception as e:
        return to_response(str(e))


# 사용자 정보 삭제
@user.delete("/{id}")
def delete_user(id: str):
    try:
        with connect()as conn:
            cursor=conn.cursor()
            try:
                cursor.execute('delete  from chat where user_id=%s;',(id,))
                cursor.execute('delete  from "user" where user_id=%s;',(id,))
                conn.commit()
                result="삭제 완료" if cursor.rowcount>0 else "존재하지 않는 아이디"
                return to_response(result)
            except Exception as e: 
                return to_response(f"에러 : {e}")
    except Exception as e:
        return to_response(str(e))


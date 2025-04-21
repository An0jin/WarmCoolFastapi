from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from model import Chat,User,Login
import pandas as pd
from db_response import *
import psycopg2.errors as errors

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    docs_url=None,  # 주석 해제 시 Swagger 문서 비활성화
    redoc_url=None
)



# 라우터 정의 (기능별 분리)
chat = APIRouter(tags=['chat'], prefix='/chat')            # 채팅 기능 관련
user = APIRouter(tags=['user'], prefix='/user')            # 사용자 정보 관련


# 학습된 YOLOv11-CLS 모델 로드
model = YOLO('best.pt')

# ====================[ 채팅 기능 ]====================

# 특정 퍼스널 컬러 그룹의 채팅 내용 불러오기
@chat.get("/{color}")
def get_chat(color: str):
    with connect() as conn:
        df=pd.read_sql('''
        select chat.chat_id, "user".name , chat.msg from "user"
                        inner join chat ON "user".user_id=chat.user_id where "user".color_id=%s
                    order by chat.time
    ''',conn,params=[color,])
    return to_response(df)

# 채팅 메시지 추가
@chat.post("/")
def post_chat(chat:Chat=Form(...)):
    with connect() as conn:
        cursor=conn.cursor()
        cursor.execute("insert into chat(user_id,msg) values(%s,%s)",(chat.user_id,chat.msg))
    return 

# ====================[ 사용자 기능 ]====================

# 사용자 정보 조회
@user.get("/{id}")
def get_user(id: str):
    print(id)
    with connect() as conn:
        df=pd.read_sql('select * from "user" where "user".user_id=%s',conn,params=[id,])
    return df.to_dict(orient="records")[0]

# 사용자 정보 추가
@user.post("/")
def post_user(user:User=Form(None)):
    with connect() as conn:
        cursor=conn.cursor()
        try:
            var=user.user_id,hash(user.pw),user.name,user.birthday.user.gender
            cursor.execute('insert into "user"(user_id,pw,name,birthday,gender) values (%s,%s,%s,%s,%s)',var)
        except errors.UniqueViolation:
            return to_response("이미 존재하는 아이디 입니다")
        except errors.CheckViolation:
            return to_response("남자 여자 라고만 입력해주세요")
        except Exception as e:
            return to_response(f"개발자가 {e}을 실수했어요")
        return to_response("가입 완료")

# 사용자 정보 수정
@user.put("/")
def put_user(user:User):
    with connect()as conn:
        cursor=conn.cursor()
        try:
            cursor.execute('update "user" set pw=%s, name=%s, birthday=%s,gender=%s where user_id=%s',(user.pw,user.name,user.birthday,user.gender,user.user_id))
            conn.commit()
            to_response("수정 완료")
        except: 
            to_response("에러")


# 사용자 정보 삭제
@user.delete("/{id}")
def delete_user(id: str):
    with connect()as conn:
        cursor=conn.cursor()
        try:
            cursor.execute('delete  from chat where user_id=%s;',(id,))
            cursor.execute('delete  from "user where user_id=%s;',(id,))
            conn.commit()
            result="삭제 완료" if cursor.rowcount>0 else "존재하지 않는 아이디"
            to_response(result)
        except : 
            to_response("에러")


# ====================[ 로그인 기능 ]====================

# 로그인 시스템
@app.post('/login')
async def login(login:Login=Form(...)):
    with connect() as conn:
        df=pd.read_sql('select * from "user" where user_id=%s and pw=%s',(login.user_id,hash(login.pw)))
        df['msg']="로그인 완료"if len(df)==1 else "아이디나 비밀번호를 확인해주세요"
        return df.to_json(orient="records")[0]

# ====================[ 예측 기능 ]====================

# 얼굴 이미지 업로드 → 퍼스널 컬러 예측
@app.post('/predict')
async def predict_image(img: UploadFile,id:str=Form(...)):
    img_byte = await img.read()
    img_pil = Image.open(BytesIO(img_byte)).convert('RGB')
    result = model.predict(img_pil)[0].probs.top1
    with connect() as conn:
        cursor=conn.cursor()
        cursor.execute('update "user" set color_id=%s where user_id=%s',(result,id))
        conn.commit()
    return to_response(model.names[result])

# ====================[ 립스틱 반환 기능 ]====================

# 퍼스널컬러->어울리는 립스틱 해시코드 반환
@app.get('/lipstick/{color}')
async def lipstick(color:str):
    with connect() as conn:
        df=pd.read_sql('select * from lipstick where color_id=%s',conn,(color,))
    return to_response(df['hex_code'].values)

# ====================[ 예외 처리 ]====================

# 404 에러 응답 커스터마이징
@app.exception_handler(404)
def error(request: Request, exc: HTTPException):
    return JSONResponse(content={"result":"잘못된 응답입니다"},status_code=404)

# 라우터 등록
app.include_router(chat)
app.include_router(user)

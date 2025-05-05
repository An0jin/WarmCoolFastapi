from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from fastapi.middleware.cors import CORSMiddleware
from router import *
import json

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    # docs_url=None,  # 주석 해제 시 Swagger 문서 비활성화
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 학습된 YOLOv11-CLS 모델 로드
model = YOLO('best.pt')

# ====================[ 로그인 기능 ]====================

# 로그인 시스템
@app.post('/login')
async def login(login:Login=Form(...)):
    with connect() as conn:
        df=pd.read_sql('select user_id,name,year,gender,"user".hex_code, color.color_id, description from "user" inner join lipstick on "user".hex_code=lipstick.hex_code inner join color on color.color_id=lipstick.color_id where user_id=%s and pw=%s',conn,params=(login.user_id,hash(login.pw)))
        result=df.to_dict(orient="records")[0] if len(df)>0 else dict(zip(df.columns,[None]*len(df.columns)))
        result['msg']="성공"if len(df)==1 else '아이디나 비밀번호를 확인해주세요'
        return result

# ====================[ 예측 기능 ]====================

# 얼굴 이미지 업로드 → 퍼스널 컬러 예측
@app.post('/predict')
async def predict_image(img: UploadFile,id:str=Form(...)):
    img_byte = await img.read()
    img_pil = Image.open(BytesIO(img_byte)).convert('RGB')
    result = model.names[model.predict(img_pil)[0].probs.top1]
    with connect() as conn:
        cursor=conn.cursor()
        print(result)
        df=pd.read_sql('select color.color_id, hex_code, description from lipstick  inner join color on lipstick.color_id=color.color_id where lipstick.color_id=%s',conn,params=(result,))
        response=json.loads(df)[0]
        cursor.execute('update "user" set hex_code=%s where user_id=%s',(response['hex_code'],id))
        conn.commit()
    return response

# ====================[ 립스틱 반환 기능 ]====================

# 퍼스널컬러->어울리는 립스틱 해시코드 반환
@app.get('/lipstick/{color}')
async def lipstick(color:str):
    with connect() as conn:
        df=pd.read_sql('select * from lipstick where color_id=%s',conn,params=[color,])
        print(f"결과 : {to_response(df['hex_code'].values)}")
    return to_response(df['hex_code'].values)

# ====================[ 예외 처리 ]====================

# 404 에러 응답 커스터마이징
@app.exception_handler(404)
def error(request: Request, exc: HTTPException):
    return JSONResponse(content={"result":"잘못된 응답입니다"},status_code=404)

# 라우터 등록
app.include_router(chat)
app.include_router(user)

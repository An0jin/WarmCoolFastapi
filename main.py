from fastapi import FastAPI, UploadFile, HTTPException, Request,Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from fastapi.middleware.cors import CORSMiddleware
from router import *
import json
from openai import OpenAI
import os


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
        df=pd.read_sql('select user_id,name,year,gender, "user".hex_code, color.color_id, description from "user" left join lipstick on "user".hex_code=lipstick.hex_code left join color on color.color_id=lipstick.color_id where user_id=%s and pw=%s',conn,params=(login.user_id,hashpw(login.pw),))
        result=df.to_dict(orient="records")[0] if len(df)>0 else dict(zip(df.columns,[None]*len(df.columns)))
        result['msg']="성공"if  len(df)>0 else '아이디나 비밀번호를 확인해주세요'
        return result


# ====================[ 예측 기능 ]====================

# 얼굴 이미지 업로드 → 퍼스널 컬러 예측
@app.post('/predict')
async def predict_image(img: UploadFile, user_id: str = Form(None)):
    img_byte = await img.read()
    img_pil = Image.open(BytesIO(img_byte)).convert('RGB')
    result = model.names[model.predict(img_pil)[0].probs.top1]
    with connect() as conn:
        cursor = conn.cursor()
        print(result)
        df = pd.read_sql('select color.color_id, hex_code, description from lipstick inner join color on lipstick.color_id=color.color_id where lipstick.color_id=%s', conn, params=(result,))
        # DataFrame을 JSON 문자열로 변환 후 파싱
        df_json = df.to_json(orient="records")
        response = json.loads(df_json)[0]
        # user_id 변수 사용 (id 대신)
        if user_id!=None:
            cursor.execute('update "user" set hex_code=%s where user_id=%s', (response['hex_code'], user_id))
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


# 퍼스널컬러->안어울리는 립스틱 해시코드 반환
@app.get('/lipstick_not/{color}')
async def lipstick_not(color:str):
    with connect() as conn:
        df=pd.read_sql('select * from lipstick where color_id!=%s',conn,params=[color,])
        print(f"결과 : {to_response(df['hex_code'].values)}")
    return to_response(df['hex_code'].values)

# ====================[ AI 챗봇 기능 ]====================
@app.post('/llm')
async def llm(llm:LLM=Form(None)):
    with connect() as conn:
        colors=list(map(lambda x:x[0],pd.read_sql('select hex_code from lipstick where color_id=%s',conn,params=[llm.color_id,]).values))
        client = OpenAI(api_key=os.getenv("openAIKey"))
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # 사용 가능한 모델명
            messages=[
                {"role": "system", "content": f"You are given a situation and you have to pick a lipstick color among {colors}. Please respond with a color code like #ffffff and do not say anything else."},
                {"role": "user", "content": llm.msg}
            ]
        )
        shap=response.choices[0].message.content.find("#")
        color=response.choices[0].message.content[shap:shap+7]
        if llm.user_id!=None:
            cursor=conn.cursor()
            cursor.execute('update "user" set hex_code=%s where user_id=%s',(color,llm.user_id))
            conn.commit()        
    return to_response(color)

# ====================[ 예외 처리 ]====================

# 404 에러 응답 커스터마이징
@app.exception_handler(404)
def error(request: Request, exc: HTTPException):
    return JSONResponse(content={"result":"잘못된 응답입니다"},status_code=404)

# 라우터 등록
app.include_router(chat)
app.include_router(user)

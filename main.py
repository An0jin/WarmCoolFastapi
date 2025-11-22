from fastapi import FastAPI, UploadFile, HTTPException, Request,Form,File
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from fastapi.middleware.cors import CORSMiddleware
from router import *
import json
import re
from ultralytics import YOLO
from tool import LipstickLLM,JWT,connect,to_response,hashpw, SendEmail
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
load_dotenv()

executor = ThreadPoolExecutor(max_workers=(os.cpu_count() or 4))

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    docs_url=None,  # 주석 해제 시 Swagger 문서 비활성화
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
model=YOLO('best.pt')
# ====================[ 테스트용 ]====================

# @app.get('/')
# async def test():
#     return FileResponse("index.html")

# ====================[ 로그인 기능 ]====================

# 로그인 시스템
@app.post('/login')
async def login(login:Login=Form(...)):
    try:
        with connect() as conn:
            df=pd.read_sql('select * from "user" as U left join lipstick as L on U.hex_code =L.hex_code  where U.email=%s and U.pw=%s',conn,params=(login.email,hashpw(login.pw)))
            result=df.to_dict(orient="records")[0] if len(df)==1 else dict(zip(df.columns,[None]*len(df.columns)))
            result['msg']="성공"if  len(df)==1 else '이메일과 암호를 확인해주세요'
            result['token']=JWT.encode(login.email)if  len(df)==1 else None
            return result
    except Exception as e:
        return to_response(str(e))


# ====================[ 예측 기능 ]====================

# 얼굴 이미지 업로드 → 퍼스널 컬러 예측
@app.post('/predict')
async def predict_image(img: UploadFile=File(...), token: str = Form(None)):
    print("예측중")
    img_byte = await img.read()
    loop = asyncio.get_event_loop()
    def predict(img_byte):
        img_pil = Image.open(BytesIO(img_byte)).convert('RGB') 
        results = model.predict(img_pil, iou=0.1, agnostic_nms=True)
        return results[0].boxes.cls
    result=loop.run_in_executor(executor,predict,img_byte)
    if len(result) > 1:
        return {"color_id": "한사람만 테스트할수 있습니다", "hex_code": "","description":""}
    elif len(result) == 0:
        return {"color_id": "얼굴을 찾을 수 없습니다", "hex_code": "","description":""}
    else:
        color_id=model.names[result[0].item()]
    with connect() as conn:
        cursor = conn.cursor()
        df = pd.read_sql('select color.color_id, hex_code, description from lipstick inner join color on lipstick.color_id=color.color_id where lipstick.color_id=%s', conn, params=(color_id,))
        # DataFrame을 JSON 문자열로 변환 후 파싱
        df_json = df.to_json(orient="records")
    response = json.loads(df_json)[0]
    if token!=None:
        email=JWT.decode(token)
        cursor.execute('update "user" set hex_code=%s where email=%s', (response['hex_code'], email))
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

# ====================[ AI 챗봇 기능 ]====================
@app.post('/llm')
async def llm(llm:LLM=Form(None)):
    with connect() as conn:
        load_dotenv()
        email=JWT.decode(llm.token)
        colors=list(map(lambda x:x[0],pd.read_sql('''
        SELECT hex_code FROM lipstick 
WHERE color_id = (
    SELECT T1.color_id 
    FROM "user" AS T0 
    INNER JOIN lipstick AS T1 ON T0.hex_code = T1.hex_code 
    WHERE T0.email = %s
)''',conn,params=[email,]).values))
        lllm=LipstickLLM()
        response = await lllm.invoke(llm.msg,colors)
        patten="#[A-Fa-f\d]{6}"
        color=re.findall(patten,response)[0]
        if llm.token!=None:
            cursor=conn.cursor()
            cursor.execute('update "user" set hex_code=%s where email=%s',(color,email))
            conn.commit()        
    return to_response(color)

# ====================[ 버전 체크 기능]====================
@app.get('/version/{version}')
async def version(version:int):
    with connect() as conn:
        df=pd.read_sql('select * from "version"',conn)
    return to_response(version==df['version'].values[0])

# ====================[  비밀번호 초기화 기능]====================
@app.post('/email')
async def get_Pw(email:Email=Form(...)):
    print(f"email : {email.email}")
    new_pw=os.urandom(32).hex()[:6]
    with connect() as conn:
        df=pd.read_sql('select * from "user" where email=%s',conn,params=[email.email])
        if len(df)==0:
            return to_response("해당 이메일이 존재하지 않습니다")
        cursor=conn.cursor()
        cursor.execute('update "user" set pw=%s where email=%s',(hashpw(new_pw),email.email))
        conn.commit()
    SendEmail(email.email,f"당신의 비밀번호는 {new_pw}으로 초기화 했습니다")
    return to_response("메일을 확인해주세요")

@app.post('/getNum')
async def getNum(email:str=Form(...),num:str=Form(...)):
    SendEmail(email,f"인증번호 : {num}")
    return to_response("메일을 확인해주세요")


# ====================[ 예외 처리 ]====================

# 404 에러 응답 커스터마이징
@app.exception_handler(404)
def error(request: Request, exc: HTTPException):
    return JSONResponse(content={"result":"잘못된 응답입니다"},status_code=404)

# 라우터 등록
app.include_router(chat)
app.include_router(user)

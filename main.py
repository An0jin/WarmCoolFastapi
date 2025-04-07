from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from ultralytics import YOLO

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    # docs_url=None,  # 주석 해제 시 Swagger 문서 비활성화
)

# 라우터 정의 (기능별 분리)
predict = APIRouter(tags=['predict'], prefix='/predict')  # 퍼스널 컬러 예측 관련
chat = APIRouter(tags=['chat'], prefix='/chat')            # 채팅 기능 관련
user = APIRouter(tags=['user'], prefix='/user')            # 사용자 정보 관련

# 학습된 YOLOv8-CLS 모델 로드
model = YOLO('best.pt')

# ====================[ 예측 기능 ]====================

# 얼굴 이미지 업로드 → 퍼스널 컬러 예측
@predict.post('/')
async def predict_image(img: UploadFile):
    img_byte = await img.read()
    img_pil = Image.open(BytesIO(img_byte)).convert('RGB')
    result = model.predict(img_pil)[0].probs.top1
    return {"result":model.names[result]}

# ====================[ 채팅 기능 ]====================

# 특정 퍼스널 컬러 그룹의 채팅 내용 불러오기
@chat.get("/{color}")
def get_chat(color: str):
    return {"result":"채팅 내용을 가져오는 앤드포인트"}

# 채팅 메시지 추가
@chat.post("/")
def post_chat():
    return {"result":"채팅 내용을 추가하는 앤드포인트"}

# ====================[ 사용자 기능 ]====================

# 사용자 정보 조회
@user.get("/{id}")
def get_user(id: int):
    return {"result":"해당 유저 정보를 가져오는 앤드포인트"}

# 사용자 정보 추가
@user.post("/")
def post_user():
    return {"result":"유저 정보를 추가하는 앤드포인트"}

# 사용자 정보 수정
@user.put("/{id}")
def put_user(id: int):
    return {"result":"유저 정보를 수정하는 앤드포인트"}

# 사용자 정보 삭제
@user.delete("/{id}")
def delete_user(id: int):
    return {"result":"유저 정보를 삭제하는 앤드포인트"}

# ====================[ 예외 처리 ]====================

# 404 에러 응답 커스터마이징
@app.exception_handler(404)
def error(request: Request, exc: HTTPException):
    return JSONResponse(content={"result":"잘못된 응답입니다"},status_code=404)

# 라우터 등록
app.include_router(chat)
app.include_router(predict)
app.include_router(user)

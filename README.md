
# ⚡ FastAPI 기반 퍼스널 컬러 분석 서버

## 📌 개요

이 리포지토리는 **YOLOv11-CLS 모델을 FastAPI로 서빙**하여, Unity 애플리케이션과 통신하는 퍼스널 컬러 분석 백엔드 서버입니다. 사용자의 얼굴 이미지를 전달받아 퍼스널 컬러(예: 웜톤, 쿨톤 등)를 추론하고, 그 결과를 반환합니다.

------

## 🏗 시스템 구성 요소 관계 흐름

```
[ photon chat ]
  -같은 퍼스널 컬러인 사람들 끼리 커뮤니티를 할수 있는 공간 구현

        ↑ 퍼스널 컬러 제공

[ Unity (시작점)]
  - 사용자 얼굴 이미지 촬영
  - 분석 결과 기반 AR 메이크업 적용 (ARFoundation)
  - ➕ 결과 기반으로 Photon Chat 연결

이미지 전송   ⇅결과 수신

[ FastAPI 서버 ]
  - YOLOv11-CLS 모델 호출
  - Unity에서 이미지 수신 → 추론 → 결과 응답

이미지 전송   ⇅결과 수신

[ YOLOv11-CLS 모델 (Ultralytics) ](https://docs.ultralytics.com/ko/tasks/classify/)
  - 학습된 weight로 이미지 분류
  - 퍼스널 컬러 결과 반환

        ↑ 데이터 제공

[ Roboflow & github]
  - YOLOv11-CLS 학습용 데이터셋 제공=
```
---

## 🧩 시스템 내 역할

본 FastAPI 서버는 전체 시스템에서 다음과 같은 역할을 수행합니다:

- Unity로부터 얼굴 이미지를 수신
- YOLOv11-CLS 모델을 통해 퍼스널 컬러 분석 수행
- 추론 결과(JSON)를 Unity로 반환

---

## 🚀 실행 방법

1. 의존성 설치:
   ```bash
   pip install fastapi uvicorn ultralytics python-multipart
   ```

2. 서버 실행:
   ```bash
   uvicorn main:app --reload
   ```

3. 테스트:
   - Unity 또는 Postman으로 이미지 전송 (`POST /predict`)
   - 응답 예시:
     ```json
     {
       "result": "봄 웜톤",
     }
     ```

---

## 📡 FastAPI 퍼스널 컬러 분석 API 명세
### predict
#### 📍 POST `/predict/`

- **설명**: 업로드된 이미지를 YOLOv8-CLS 모델로 분석하여 퍼스널 컬러(예: 웜톤, 쿨톤)를 분류합니다.
- **요청 방식**: `multipart/form-data`
- **요청 필드**:
  - `img`: 사용자 얼굴 이미지 파일 (예: JPG, PNG 등)

---

### chat (구현 예정)

#### 📍 GET `/chat/{color}`

- **설명**: DB에 있는 해당 퍼스널 컬러의 채팅 내용을 가져옵니다

#### 📍 POST `/chat/`

- **설명**: DB에 채팅 내용을 업로드 합니다
- **요청 방식**: `multipart/form-data`

---

### user (구현 예정)

#### 📍 GET `/user/{id}`

- **설명**: DB에 있는 해당 아이디의 유저 정보를 가져옵니다

#### 📍 POST `/user/`

- **설명**: DB에 유저를 추가 합니다
- **요청 방식**: `multipart/form-data`

#### 📍 PUT `/user/{id}`

- **설명**: DB에 해당 아이디의 유저 정보를 수정합니다

#### 📍 DELETE `/user/{id}`

- **설명**: DB에 해당 아이디의 유저를 삭제 합니다

---

## 🧠 기술 스택

- **FastAPI** – 경량화된 Python 웹 서버
- **Ultralytics YOLOv8 (CLS)** – 퍼스널 컬러 분류 모델
- **Roboflow** – 학습용 데이터셋 관리
- **Uvicorn** – ASGI 서버 실행

---

## 📬 연락 및 기여

기여는 언제든 환영합니다!  
Issue 또는 PR을 통해 함께 발전시켜 주세요.

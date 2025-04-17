# ⚡ FastAPI 기반 퍼스널 컬러 분석 서버

## 📌 개요

이 리포지토리는 **YOLOv11-CLS 모델을 FastAPI로 서빙**하여, Unity 애플리케이션과 통신하는 퍼스널 컬러 분석 백엔드 서버입니다. 사용자의 얼굴 이미지를 전달받아 퍼스널 컬러(예: 웜톤, 쿨톤 등)를 추론하고, 그 결과를 반환합니다.

---



## 🏗 시스템 구성
프로젝트는 다음 다섯 개의 주요 리포지토리로 구성되어 있습니다:

### 1. [WarmCoolYolo](https://github.com/anyoungjin20040106/WarmCoolYolo)
- YOLOv11-CLS 기반 퍼스널 컬러 분류 모델
- Roboflow를 통한 데이터셋 관리
- 모델 학습 및 평가 파이프라인

### 2. [WarmCoolFastapi](https://github.com/anyoungjin20040106/WarmCoolFastapi)
- FastAPI 기반 백엔드 서버
- YOLOv11-CLS 모델 서빙
- RESTful API 엔드포인트 제공
- Postgresql 데이터베이스 연동

### 3. [WarmCoolUnity](https://github.com/anyoungjin20040106/WarmCoolUnity)
- Unity 기반 AR 애플리케이션
- ARFoundation을 통한 얼굴 인식
- 가상 메이크업 적용
- Photon 기반 실시간 채팅

### 4. [WarmCoolSQL](https://github.com/anyoungjin20040106/WarmCoolSQL)
- 채팅 정보 관리
- 유저 정보 관리
- 퍼스널 컬러 해설

### 5. [WarmCoolDataset](https://github.com/anyoungjin20040106/WarmCoolDataset)
- roboflow를 활용한 데이터 수집
- github를 활용한 데이터 수집
- 데이터 전처리

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


## 🛠 사용 기술

- FastAPI
- psycopg(추가 예정)

---


## 💻 기술 스택
- **AI/ML**: YOLOv11-CLS, Ultralytics
- **백엔드**: FastAPI, Postgresql
- **프론트엔드**: Unity, ARFoundation
- **네트워킹**: Photon Chat
- **데이터**: Roboflow

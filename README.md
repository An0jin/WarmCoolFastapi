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
- 데이터 라벨링

## 📡 FastAPI 퍼스널 컬러 분석 API 명세

### chat

#### 📍 GET `/chat/{color}`

- **설명**: DB에 있는 해당 퍼스널 컬러의 채팅 내용을 가져옵니다
- **요청 방식**: `query parameter`
- **요청 필드**
  - `color` : 퍼스널 컬러

#### 📍 POST `/chat/`

- **설명**: DB에 채팅 내용을 업로드 합니다
- **요청 방식**: `application/x-www-form-urlencoded`
- **요청 필드**
  - `user_id` : 유저의 아이디
  - `msg` : 메세지

---

### user

#### 📍 GET `/user/{id}`

- **설명**: DB에 있는 해당 아이디의 유저 정보를 가져옵니다
- **요청 방식**: `query parameter`
- **요청 필드**
  - `id` : 유저의 아이디


#### 📍 POST `/user/`

- **설명**: DB에 유저를 추가 합니다
- **요청 방식**: `application/x-www-form-urlencoded`
- **요청 필드**
  - `user_id` : 유저의 아이디
  - `pw` : 비밀번호
  - `name` : 유저명
  - `birthday` : 생년월일
  - `gender` : 성별

#### 📍 PUT `/user/{id}`

- **설명**: DB에 해당 아이디의 유저 정보를 수정합니다
- **요청 방식**: `application/json`
- **요청 필드**
  - `user_id` : 유저의 아이디
  - `pw` : 비밀번호
  - `name` : 유저명
  - `birthday` : 생년월일
  - `gender` : 성별


#### 📍 DELETE `/user/{id}`

- **설명**: DB에 해당 아이디의 유저를 삭제 합니다
- **요청 방식**: `query parameter`
- **요청 필드**
  - `id` : 유저의 아이디

---

### 그 외

#### 📍 POST `/predict/`

- **설명**: 업로드된 이미지를 YOLOv8-CLS 모델로 분석하여 퍼스널 컬러(예: 웜톤, 쿨톤)를 분류하고 "user".color_id를 수정합니다.
- **요청 방식**: `multipart/form-data`
- **요청 필드**
  - `img`: 사용자 얼굴 이미지 파일 (예: JPG, PNG 등)
  - `id` : 유저의 아이디

#### 📍 POST `/login/`

- **설명**: 유저의 아이디와 비밀번호를 받아 로그인 요청을 처리합니다.
- **요청 방식**: `multipart/form-data`
- **요청 필드**
  - `user_id` : 유저의 아이디
  - `pw`: 비밀번호

#### 📍 GET `/lipstick/{color}`

- **설명**: 해당 피부톤에 어울리는 립스틱 색상들을 반환합니다.
- **요청 방식**: `query parameter`
- **요청 필드**
  - `color` : 퍼스널 컬러

---

## 🛠 사용 기술

- ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
- ![docker](https://img.shields.io/badge/-docker-2496ED?style=flat&logo=docker&logoColor=white)
- ![amazonec2](https://img.shields.io/badge/-AWS%20EC2-FF9900?style=flat&logo=amazonec2&logoColor=white)

---

## 💻 기술 스택

- **AI/ML**: ![Ultralytics(YOLOv11-CLS)](https://img.shields.io/badge/YOLOv11--CLS-111F68?style=flat&logo=Ultralytics&logoColor=white)
- **백엔드**: ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi&logoColor=white), ![docker](https://img.shields.io/badge/-docker-2496ED?style=flat&logo=docker&logoColor=white), ![amazonwebservices](https://img.shields.io/badge/-AWS%20AppRunner-232F3E?style=flat&logo=amazonwebservices&logoColor=white), ![amazonwebservices](https://img.shields.io/badge/-AWS%20Elastic%20Container%20Registry-232F3E?style=flat&logo=amazonwebservices&logoColor=white)
- **DB** : ![Postgresql](https://img.shields.io/badge/-postgresql-4169E1?style=flat&logo=postgresql&logoColor=white), ![amazonrds](https://img.shields.io/badge/-amazonrds-527FFF?style=flat&logo=amazonrds&logoColor=white)
- **프론트엔드**: ![Unity(ARFoundation)](https://img.shields.io/badge/-ARFoundation-000000?style=flat&logo=unity&logoColor=white)
- **네트워킹**: ![Photon Chat](https://img.shields.io/badge/-Photon%20Chat-004480?style=flat&logo=photon&logoColor=white)
- **데이터 수집**: ![Roboflow](https://img.shields.io/badge/-roboflow-6706CE?style=flat&logo=roboflow&logoColor=white),![github](https://img.shields.io/badge/-github-000000?style=flat&logo=github&logoColor=white)
- **디자인**: ![Photoshop](https://img.shields.io/badge/-Photoshop-31A8FF?style=flat&logo=adobe-photoshop&logoColor=white)
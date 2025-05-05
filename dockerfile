# 베이스 이미지로 Python 3.11 사용
FROM python:3.11.9

WORKDIR /code

# OpenCV 및 기타 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt 

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

# 명령어 설정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
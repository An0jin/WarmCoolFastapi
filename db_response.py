import psycopg2
import os
import pandas as pd
import hashlib

def connect():
    return psycopg2.connect(host=os.getenv("MakeUpHost"),
                            port=int(os.getenv("MakeUpPort")),
                            user=os.getenv("MakeUpUser"),
                            password=os.getenv("MakeUpPW"),
                            dbname=os.getenv("MakeUpDBname"))
def to_response(x):
    if isinstance(x, pd.DataFrame):
        return {"result": x.to_dict(orient="records")}
    elif hasattr(x, 'tolist'):  # NumPy 배열 처리
        return {"result": x.tolist()}
    else:
        return {"result": x}

def hash(pw):
    c=ord(pw[-1])
    for i in range(c%10):
        func=hashlib.blake2b if bool(i%2) else hashlib.sha256
        pw=func(pw.encode()).hexdigest()
    return pw
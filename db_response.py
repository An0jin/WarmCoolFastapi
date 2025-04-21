import psycopg2
import os
import pandas as pd
import hashlib

def connect():
    return psycopg2.connect(host=os.getenv("MakeUpHost"),
                            port=int(os.getenv("MakeUpPort")),
                            user=os.getenv("MakeUpUser"),
                            password=os.getenv("MakeUpPassword"),
                            dbname="makeup")
def to_response(x):
    return {"result":x.to_json(orient="records",index=False)if isinstance(x,pd.DataFrame) else x} 

def hash(pw):
    c=ord(pw[-1])
    for i in range(c%10):
        func=hashlib.blake2b if bool(i%2) else hashlib.sha256
        pw=func(pw.encode()).hexdigest()
    return pw
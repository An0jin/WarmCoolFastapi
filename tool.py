import hashlib
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()
from jose import JWTError
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent

def connect():
    """데이터베이스에 접근하는 함수"""
    return psycopg2.connect(host=os.getenv("host"),
                            port=int(os.getenv("port")),
                            user=os.getenv("user"),
                            password=os.getenv("password"),
                            dbname=os.getenv("dbname"))


def to_response(x):
    """응답을 JSON 형식으로 변환하는 함수"""
    if isinstance(x, pd.DataFrame):
        return {"result": x.to_dict(orient="records")}
    elif hasattr(x, 'tolist'):  # NumPy 배열 처리
        return {"result": x.tolist()}
    else:
        return {"result": x}


def hashpw(pw):
    """패스워드를 해싱하는 함수"""
    c = ord(pw[-1])
    for i in range(c % 5):
        func = hashlib.blake2b if bool(i % 2) else hashlib.sha256
        pw = func(pw.encode()).hexdigest()
    return pw

class JWT:
    @staticmethod
    def encode(user_id):
        return jwt.encode({'user_id':user_id}, os.getenv("jwtSecret"), algorithm='HS256')
    @staticmethod
    def decode(token):
        try:
            return jwt.decode(token, os.getenv("jwtSecret"), algorithms=['HS256'])['user_id']
        except:
            return None
class LipstickLLM:
    def __init__(self):
        groq = ChatGroq(
            model="gemma2-9b-it", # 또는 gemma-7b-it과 같이 더 안정적인 모델 고려
            api_key=os.getenv("groq")
        )   
        tools = [
    DuckDuckGoSearchRun(name="web_search")
]
        prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Beauty AI specializing in recommending the best lipstick based on the user's situation. Please only respond with lipstick colors from the list and follow the format #000000. You must provide accurate and up-to-date information.
For answering questions, you may use the following tools ({tool_names}):

You should infer and act as follows:
Thought: (Determine what action to take based on the question. Decide whether to use a tool or provide a final answer.)
Action: (The name of the action to be performed. Must be one of the available tools: {tool_names})
Action Input: (The input format for the action. Must match the format of the tool's input.)
Observation: (The result of the action)
... (Repeat Thought/Action/Action Input/Observation as needed)
Thought: (Determine when it's time to provide a final answer.)
Final Answer: (The final answer)

Available tools:
{tools}

{agent_scratchpad}
"""),
    ("human", "{input}"),
])

        # 4. ReAct 에이전트 생성
        agent = create_react_agent(groq, tools,prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)
def invoke(self,text):
    result = self.agent_executor.invoke({"input": text})
    return result['output']

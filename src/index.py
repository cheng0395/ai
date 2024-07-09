import time

import requests
import streamlit as st
from db import verify_login, get_user_name, insert_chat_record
from db import get_chat_history



def get_answer(api_key, user_input, session_id):
    url = "http://localhost:8001/get_response"
    payload = {
        "api_key": api_key,
        "user_input": user_input,
        "session_id": session_id
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return "Error: " + response.text

def get_history(user_id):
    url = f"http://localhost:8001/get_chat_history/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return "Error: " + response.text


with st.sidebar:
    st.title("登录")
    user_id = st.text_input("用户id")
    user_password = st.text_input("用户密码", type="password")
    if verify_login(user_id, user_password):
        user_name = get_user_name(user_id)
        key = st.text_input(f"你好，{user_name}！请输入你的大模型密钥", type="password")
    elif user_id and user_password:
        st.write("用户名或密码错误")
    st.divider()
    st.title("查询聊天记录")
    input_id=st.text_input("请输入想查询的用户id")
    if st.button("提交"):
        history = get_history(input_id)
        st.write(history)


def stream_data(result_text):
    for word in result_text.split(" "):
        yield word
        time.sleep(0.02)


st.title("🌏AI问答页面")
# 定义⼀个聊天记录到会话管理中
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "你好,我是您的ai助⼿，请输⼊你的问题!"}]

# print(st.session_state["messages"])
# 如果聊天记录会话中只有⼀个开场⽩，那我们需要将开场⽩⽤流式模拟的⽅式渲染出来
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("请输⼊你的问题")
if user_input:
    st.session_state["messages"].append({"role": "human", "content": user_input})
    # 获取⽤户输⼊并调⽤模型对象，并处理其历史消息
    with st.chat_message("human"):
        st.write_stream(stream_data(" ".join(user_input)))

if user_input:
    # 进行模型调用
    with st.spinner("AI正在思考中，请等待....."):
        response = get_answer(key, user_input, user_id)
        # 展示模型输入
        st.session_state["messages"].append({"role": "ai", "content": response})
        with st.chat_message("ai"):
            st.write_stream(stream_data(" ".join(response)))
        # 存储到数据库
        insert_chat_record(user_id, user_name, user_input, response)

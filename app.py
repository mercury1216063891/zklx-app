import streamlit as st
from PIL import Image
import base64
import requests
import json
from voice_toolkit import voice_toolkit


icon_path = "images/院徽.ico"

ICON = Image.open(icon_path)
with open(icon_path, "rb") as img_file:
    ICON_base64 = base64.b64encode(img_file.read()).decode()

st.set_page_config(
    page_title="智课灵犀-对话",
    layout="centered",
    page_icon=ICON,
)

with st.sidebar:
    icon_text = f"""
        <div class="icon-text-container" style="text-align: center;">
            <img src='data:image/png;base64,{ICON_base64}' alt='icon' style='width: 70px; height: 70px; margin: 0 auto; display: block;'>
            <span style='font-size: 24px;'>湘潭大学课程助手--智课灵犀</span>
        </div>
        """
    st.markdown(
        icon_text,
        unsafe_allow_html=True,
    )

st.sidebar.title("模型")
option1 = st.sidebar.selectbox("课程", ["数据结构", "软件工程与项目管理"])

st.sidebar.title("输入")
option2 = st.sidebar.selectbox("方式", ["键盘", "语音"])


# 添加滑动条
st.sidebar.title("参数")
with st.sidebar.expander("文本生成"):
    if "max_new_tokens" not in st.session_state:
        st.session_state["max_new_tokens"] = 500
        st.session_state["top_p"] = 0.9
        st.session_state["temperature"] = 0.1
        st.session_state["repetition_penalty"] = 1.0
    parameter_1 = st.slider(
        "max_new_tokens",
        min_value=50,
        max_value=1000,
        value=st.session_state.max_new_tokens,
        step=50,
    )
    parameter_2 = st.slider(
        "top_p", min_value=0.5, max_value=0.95, value=st.session_state.top_p, step=0.01
    )
    parameter_3 = st.slider(
        "temperature",
        min_value=0.1,
        max_value=5.0,
        value=st.session_state.temperature,
        step=0.1,
    )
    parameter_4 = st.slider(
        "repetition_penalty",
        min_value=0.5,
        max_value=5.0,
        value=st.session_state.repetition_penalty,
        step=0.1,
    )

    st.session_state["max_new_tokens"] = parameter_1
    st.session_state["top_p"] = parameter_2
    st.session_state["temperature"] = parameter_3
    st.session_state["repetition_penalty"] = parameter_4

st.title("🪶 智课灵犀")
st.caption("🌈 一款由湘潭大学计算机学院开发的课程助手")

# 状态
if "chat_type" not in st.session_state or st.session_state["chat_type"] != "chat":
    st.session_state["chat_type"] = "chat"

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

if "user_input_area" not in st.session_state:
    st.session_state.user_input_area = ""

if "user_voice_value" not in st.session_state:
    st.session_state.user_voice_value = ""

if "voice_flag" not in st.session_state:
    st.session_state["voice_flag"] = ""

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "message": "你好，我是湘潭大学课程知识答疑小助手“智课灵犀”",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["message"])


def send_message():
    payload = {
        "chat_type": st.session_state.chat_type,
        "messages": st.session_state.messages,
        "max_new_tokens": st.session_state.max_new_tokens,
        "top_p": st.session_state.top_p,
        "temperature": st.session_state.temperature,
        "repetition_penalty": st.session_state.repetition_penalty,
    }
    # print(type(payload), payload)
    url_map = {
        "数据结构": "http://localhost:5000/api-dev/qa/get_answer",
        "软件工程与项目管理": "http://localhost:5000/api-dev/qa/get_answer2",
    }
    url = url_map.get(option1)
    response = requests.post(url, json=payload)
    # print(response, type(response))
    return response.text


if option2 == "键盘":
    if prompt := st.chat_input(placeholder="输入..."):
        st.session_state.messages.append({"role": "user", "message": prompt})
        st.chat_message("user").write(prompt)
        answer = send_message()
        st.session_state.messages.append({"role": "assistant", "message": answer})
        st.chat_message("assistant").write(answer)
        print(st.session_state)

elif option2 == "语音":
    # 文本输入表单
    with st.form("input_form", clear_on_submit=True):
        prompt = st.text_area(
            "**输入：**",
            key="user_input_area",
            value=st.session_state.user_voice_value,
            help="在此输入文本或通过语音输入。",
        )
        submitted = st.form_submit_button("确认提交")

    # 处理提交
    if submitted:
        st.session_state.messages.append({"role": "user", "message": prompt})
        st.chat_message("user").write(prompt)
        answer = send_message()
        st.session_state.messages.append({"role": "assistant", "message": answer})
        st.chat_message("assistant").write(answer)

        st.session_state.user_voice_value = ""
        st.rerun()
    # 语音输入
    vocie_result = voice_toolkit()
    # vocie_result会保存最后一次结果
    if (
        vocie_result and vocie_result["voice_result"]["flag"] == "interim"
    ) or st.session_state["voice_flag"] == "interim":
        st.session_state["voice_flag"] = "interim"
        st.session_state["user_voice_value"] = vocie_result["voice_result"]["value"]
        if vocie_result["voice_result"]["flag"] == "final":
            st.session_state["voice_flag"] = "final"
            st.rerun()

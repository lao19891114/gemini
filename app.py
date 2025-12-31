import streamlit as st
import google.generativeai as genai
import os

# 页面基础设置
st.set_page_config(page_title="Gemini 私人空间", page_icon="🌙")
st.title("Gemini 3 Pro - 沉浸式写作 (CN直连版)")

# 从环境变量获取 Key (适配 Zeabur)
api_key = os.getenv("GOOGLE_API_KEY")

# 如果本地测试没有环境变量，尝试从 Streamlit Secrets 获取（兼容 Streamlit Cloud）
if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

if not api_key:
    st.error("请配置 API Key！(在 Zeabur 的 Variables 中添加 GOOGLE_API_KEY)")
    st.stop()

# 配置 API
genai.configure(api_key=api_key)

# 【核心】暴力解锁安全设置 (Block None)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# 初始化模型函数
def get_model(model_name):
    generation_config = {
        "temperature": 1.0, # 稍微调高，增加创造性
        "max_output_tokens": 8192,
    }
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

# 聊天界面逻辑
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏：选择模型
with st.sidebar:
    st.header("模型选择")
    selected_model = st.selectbox(
        "选择你的写手:",
        ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"],
        index=0
    )
    st.info("💡 提示：Flash 速度最快且阻力最小；Pro 文笔更好但可能被拒。")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理输入
if prompt := st.chat_input("输入剧情指令..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 生成回复
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.markdown("正在构思中...")
        
        try:
            # 尝试加载选中的模型
            model = get_model(selected_model)
            
            # 构建历史记录
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages 
                if m["role"] != "system"
            ]
            
            # 发送请求
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt)
            
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
        except Exception as e:
            status_placeholder.error(f"生成失败: {e}\n\n建议：尝试在侧边栏切换回 Flash 模型，那个抗拒更少。")

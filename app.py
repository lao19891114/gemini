import streamlit as st
import google.generativeai as genai
import os

# 页面配置
st.set_page_config(page_title="Gemini 沉浸式空间", page_icon="🌌", layout="wide")

# 标题
st.title("🌌 Gemini 3 - 沉浸式解压终端")

# 1. 获取 API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

if not api_key:
    st.error("❌ 未检测到 API Key，请在 Zeabur 环境变量中配置 GOOGLE_API_KEY")
    st.stop()

# 2. 配置 API Key
genai.configure(api_key=api_key)

# 3. 侧边栏：核心控制台
with st.sidebar:
    st.header("🎮 控制台")
    
    # --- 模型选择器 (关键更新) ---
    selected_model = st.selectbox(
        "选择你的 AI 伴侣:",
        [
            "gemini-3-flash-preview",  # 【首选】最新一代 Flash，速度快，智商高，抗拒低
            "gemini-2.5-flash",        # 【稳妥】经典款，写文非常顺手
            "gemini-3-pro-preview",    # 【深度】最新一代 Pro，文笔最强，但可能爱说教
            "gemini-2.5-pro",          # 【怀旧】上一代 Pro
        ],
        index=0, # 默认选中第一个 (3 Flash)
        help="推荐使用 Flash 系列，速度快且更听话。Pro 系列适合写复杂的长篇大论。"
    )
    
    # --- 参数调节 ---
    temperature = st.slider("创造力 (Temperature)", 0.0, 2.0, 1.2, help="越高越疯，越低越严谨。写文建议 1.0 以上。")
    
    if st.button("🗑️ 清空记忆 (重开)"):
        st.session_state.messages = []
        st.rerun()

# 4. 暴力解锁安全设置 (这是写解压文的关键)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# 5. 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. 处理用户输入
if prompt := st.chat_input("输入剧情指令... (例如：继续，详细描写...)"):
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 生成回复
    with st.chat_message("assistant"):
        status_box = st.empty()
        status_box.markdown(f"⚡ {selected_model} 正在构思...")

        try:
            # 动态加载用户选中的模型
            model = genai.GenerativeModel(
                model_name=selected_model,
                generation_config={
                    "temperature": temperature, 
                    "max_output_tokens": 8192
                },
                safety_settings=safety_settings
            )

            # 构建历史上下文
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages
                if m["role"] != "system"
            ]

            # 发送请求
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt)
            
            # 显示结果
            status_box.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})

        except Exception as e:
            status_box.error(f"⚠️ 生成失败: {e}")
            st.info("💡 建议：如果遇到 404 错误，说明该模型在此地区不可用，请在左侧尝试切换其他模型（如 2.5 Flash）。")

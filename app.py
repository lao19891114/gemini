import os
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, api_key: str):
        # 初始化客户端，默认使用最新 API 版本
        self.client = genai.Client(api_key=api_key)
        # 2026 推荐模型：Pro 用于复杂推理，Flash 用于快速响应
        self.pro_model = "gemini-3.0-pro" 
        self.flash_model = "gemini-3.0-flash"

    def list_all_models(self):
        """列出所有你当前权限可以使用的模型名称"""
        print("可用模型列表:")
        for m in self.client.models.list():
            print(f"- {m.name} ({m.display_name})")

    def chat_with_history(self, user_message: str, history=None):
        """支持上下文记忆的对话"""
        chat = self.client.chats.create(model=self.flash_model, history=history)
        response = chat.send_message(user_message)
        return response.text, chat.history

    def generate_with_search(self, prompt: str):
        """集成 Google Search 联网增强功能（Gemini 3 核心功能）"""
        response = self.client.models.generate_content(
            model=self.pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
            )
        )
        return response.text

    def multimodal_analyze(self, prompt: str, image_path: str):
        """图片/视频分析（多模态）"""
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        response = self.client.models.generate_content(
            model=self.flash_model,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            ]
        )
        return response.text

    def stream_generate(self, prompt: str):
        """流式输出，像 ChatGPT 一样逐字弹出"""
        for chunk in self.client.models.generate_content_stream(
            model=self.pro_model,
            contents=prompt
        ):
            print(chunk.text, end="", flush=True)

# --- 使用示例 ---
if __name__ == "__main__":
    # 请替换为你的真实 API KEY
    MY_KEY = "YOUR_GEMINI_API_KEY"
    gemini = GeminiClient(MY_KEY)

    print("--- 1. 测试联网搜索 ---")
    ans = gemini.generate_with_search("2026年CES电子展有哪些重磅AI产品？")
    print(ans)

    print("\n--- 2. 测试流式对话 ---")
    gemini.stream_generate("请写一个关于量子计算机的长篇科幻故事开头。")

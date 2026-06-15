"""LLM 客户端 — 通用 OpenAI 兼容接口

支持任何兼容 OpenAI Chat Completions API 的服务：
- 智谱 GLM (https://open.bigmodel.cn/api/paas/v4)
- 阿里云百炼 (https://dashscope.aliyuncs.com/compatible-mode/v1)
- DeepSeek (https://api.deepseek.com/v1)
- OpenAI (https://api.openai.com/v1)
- 本地部署的 Ollama / vLLM 等

通过 base_url + api_key + model_name 三元组配置，切换供应商零代码改动。
"""
import json

import httpx

from app.config import settings

# 默认超时（秒）：LLM 生成可能较慢
DEFAULT_TIMEOUT = 120


class LLMClient:
    """OpenAI 兼容的 LLM 客户端"""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
    ):
        # 去掉末尾斜杠，统一拼接
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model_name

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> str:
        """发送 Chat Completions 请求，返回助手回复文本。"""
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        # OpenAI 标准响应格式
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"LLM 返回空结果: {json.dumps(data, ensure_ascii=False)}")

        return choices[0]["message"]["content"]

    def review_documents(
        self,
        documents: list[dict],
        review_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """对多个文档执行审查。

        Args:
            documents: [{"file_name": "xxx.pdf", "content": "# Markdown..."}]
            review_prompt: 用户的审查要求（自由文本）

        Returns:
            LLM 的审查结果文本
        """
        # 构建系统提示
        system_msg = (
            "你是一个专业的文档审查助手。用户会给你一份或多份文档的内容，"
            "以及具体的审查要求。请仔细阅读文档，按照要求进行审查，"
            "并给出结构化的审查结果。\n\n"
            "输出格式要求：\n"
            "1. 先给出总体评价（一段话）\n"
            "2. 然后按文件逐个列出发现的问题\n"
            "3. 每个问题说明：在哪个文件、什么位置、什么问题、建议如何修改\n"
            "4. 如果没有问题，明确说明「未发现问题」\n"
            "5. 使用 Markdown 格式输出"
        )

        # 构建用户消息：把所有文档内容拼接起来
        doc_sections = []
        for i, doc in enumerate(documents, 1):
            file_name = doc.get("file_name", f"文档{i}")
            content = doc.get("content", "")
            doc_sections.append(
                f"---\n## 📄 文档 {i}: {file_name}\n\n{content}\n---"
            )

        user_msg = (
            f"## 审查要求\n\n{review_prompt}\n\n"
            f"## 待审查文档\n\n" + "\n\n".join(doc_sections)
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        return self.chat(messages, temperature=temperature)

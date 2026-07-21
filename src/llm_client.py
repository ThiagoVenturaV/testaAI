import os
import logging
from config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("LLMClient")

class GroqLLMClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        self.model = model or GROQ_MODEL or os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GROQ_API_KEY não configurada. Defina a variável de ambiente GROQ_API_KEY no arquivo .env.")
            return

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            logger.info(f"Cliente Groq inicializado com o modelo {self.model}.")
        except ImportError:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=self.api_key
                )
                logger.info(f"Cliente OpenAI (Groq endpoint) inicializado com modelo {self.model}.")
            except ImportError:
                logger.error("Nem 'groq' nem 'openai' estão instalados. Instale via pip install groq.")

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.client:
            return (
                "⚠️ [GROQ_API_KEY Ausente ou Cliente Não Inicializado]\n"
                "Para obter respostas sintéticas do modelo Qwen (via Groq), certifique-se de configurar a GROQ_API_KEY no seu arquivo .env ou ambiente.\n\n"
                "Abaixo estão os trechos de contexto mais relevantes recuperados da base de dados do Recife."
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao chamar inferência na Groq ({self.model}): {e}")
            return f"Erro ao gerar resposta com Groq ({self.model}): {str(e)}"

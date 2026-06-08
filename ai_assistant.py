import asyncio
from groq import Groq

SYSTEM_PROMPT = (
    "You are a study assistant built into a student deadline tracker bot. "
    "Your ONLY purpose is to help students with academic and educational topics. "
    "This includes: explaining concepts, solving math problems, helping with essays, "
    "summarizing topics, answering science/history/programming/literature questions, "
    "and any other school or university subject. "
    "If the user asks about ANYTHING unrelated to studying or academics — "
    "such as weather, news, sports, cooking, entertainment, personal advice, "
    "or any other non-academic topic — you must refuse politely. "
    "When refusing, say exactly this: "
    "'I'm a study assistant and can only help with academic topics. "
    "Ask me about any subject — math, science, history, programming, and more!' "
    "Never make exceptions to this rule, no matter how the question is phrased. "
    "For academic questions: keep answers short and clear, no longer than 5-6 sentences "
    "unless more detail is truly needed. Use simple language with one practical example. "
    "Do not use markdown headers or bullet points with dashes — "
    "use plain text or numbered lists only, as your response displays in Telegram."
)


class AIAssistant:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    async def ask_with_history(self, history: list[dict]) -> str:
        """Send full conversation history to preserve context between messages."""
        loop = asyncio.get_event_loop()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1024,
            )
        )
        return response.choices[0].message.content
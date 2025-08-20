from openai import OpenAI
from app.core.config import settings
from typing import List
import time
from tenacity import retry, stop_after_attempt, wait_exponential

client = OpenAI(api_key=settings.openai_api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환"""
    embeddings = []
    batch_size = 10  # 배치 사이즈를 줄임
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=batch
        )
        for item in response.data:
            embeddings.append(item.embedding)
        time.sleep(1)  # 대기 시간을 늘림
    
    return embeddings

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def generate_answer(question: str, context: str) -> str:
    """검색된 컨텍스트를 기반으로 답변 생성"""
    prompt = f"""다음 슬랙 대화 내용을 참고하여 질문에 답변해주세요.
    
컨텍스트:
{context}

질문: {question}

답변:"""
    
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": "당신은 팀의 과거 슬랙 대화 내용을 바탕으로 기술적 질문에 답변하는 도우미입니다. 간결하고 정확하게 답변해주세요."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content
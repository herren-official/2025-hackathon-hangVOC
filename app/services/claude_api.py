from anthropic import Anthropic
from app.core.config import settings
from typing import List
import time
from tenacity import retry, stop_after_attempt, wait_exponential

client = Anthropic(api_key=settings.claude_api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환
    
    Note: Claude는 임베딩 API를 제공하지 않으므로, 
    Voyage AI 또는 Cohere 같은 대체 임베딩 서비스를 사용하거나
    로컬 임베딩 모델(sentence-transformers)을 사용해야 합니다.
    """
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer(settings.embedding_model)
    embeddings = []
    batch_size = 10
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch, convert_to_numpy=True)
        embeddings.extend(batch_embeddings.tolist())
        time.sleep(0.1)
    
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
    
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=500,
        temperature=0.7,
        system="당신은 팀의 과거 슬랙 대화 내용을 바탕으로 기술적 질문에 답변하는 도우미입니다. 간결하고 정확하게 답변해주세요.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text
"""LLM 서비스 통합 모듈 - OpenAI와 Claude를 모두 지원"""
from typing import List
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import time

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환
    
    Claude를 사용하는 경우 sentence-transformers를 사용하고,
    OpenAI를 사용하는 경우 OpenAI Embeddings API를 사용합니다.
    """
    if settings.api_provider == "claude" or not settings.openai_api_key:
        # Claude 사용 또는 OpenAI 키가 없는 경우 - sentence-transformers 사용
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
    else:
        # OpenAI 사용
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        embeddings = []
        batch_size = 10
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = client.embeddings.create(
                model=settings.openai_embedding_model,
                input=batch
            )
            for item in response.data:
                embeddings.append(item.embedding)
            time.sleep(1)
        
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
    
    if settings.api_provider == "claude" and settings.claude_api_key:
        # Claude 사용
        from anthropic import Anthropic
        
        client = Anthropic(api_key=settings.claude_api_key)
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
    elif settings.openai_api_key:
        # OpenAI 사용
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
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
    else:
        raise ValueError("API 키가 설정되지 않았습니다. CLAUDE_API_KEY 또는 OPENAI_API_KEY를 설정해주세요.")
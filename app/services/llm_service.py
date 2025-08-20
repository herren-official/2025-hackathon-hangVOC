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

def generate_answer(question: str, context: str) -> str:
    """검색된 컨텍스트를 기반으로 답변 생성
    
    LLM 없이 가장 관련성 높은 대화 내용을 직접 반환합니다.
    """
    # LLM API가 설정되어 있으면 사용
    if settings.api_provider == "claude" and settings.claude_api_key:
        # Claude 사용
        from anthropic import Anthropic
        
        try:
            client = Anthropic(api_key=settings.claude_api_key)
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
        except Exception as e:
            # API 에러 시 기본 방식으로 폴백
            pass
    
    elif settings.openai_api_key:
        # OpenAI 사용
        from openai import OpenAI
        
        try:
            client = OpenAI(api_key=settings.openai_api_key)
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
        except Exception as e:
            # API 에러 시 기본 방식으로 폴백
            pass
    
    # LLM 없이 직접 관련 대화 내용 반환
    # 컨텍스트에서 가장 관련성 있는 부분 추출
    lines = context.split('\n')
    relevant_lines = []
    
    # 질문 키워드 추출
    question_words = set(question.lower().split())
    
    # 각 줄의 관련성 점수 계산
    scored_lines = []
    for line in lines:
        if line.strip():
            # 질문 키워드와 일치하는 단어 수 계산
            line_words = set(line.lower().split())
            score = len(question_words & line_words)
            scored_lines.append((score, line))
    
    # 점수 높은 순으로 정렬
    scored_lines.sort(reverse=True)
    
    # 상위 5개 줄 선택
    for _, line in scored_lines[:5]:
        relevant_lines.append(line)
    
    if relevant_lines:
        answer = "🔍 관련 대화 내용:\n\n"
        answer += "\n".join(relevant_lines)
        answer += "\n\n💡 위 대화 내용이 질문과 가장 관련성이 높습니다."
        return answer
    else:
        return "관련된 대화 내용을 찾을 수 없습니다."
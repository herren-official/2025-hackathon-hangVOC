from typing import List, Dict
from app.core.database import get_collection
from app.services.llm_service import get_embeddings, generate_answer
from app.models.message import SearchQuery, SearchResult

def search_messages(query: SearchQuery) -> SearchResult:
    """질문에 대한 답변 검색 및 생성"""
    
    # 질문 임베딩
    query_embedding = get_embeddings([query.question])[0]
    
    # ChromaDB에서 유사한 메시지 검색
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=query.top_k or 10
    )
    
    # 검색 결과가 없는 경우
    if not results['documents'][0]:
        return SearchResult(
            answer="관련된 대화 내용을 찾을 수 없습니다.",
            sources=[],
            query=query.question
        )
    
    # 컨텍스트 생성
    context_parts = []
    sources = []
    
    for i, doc in enumerate(results['documents'][0]):
        context_parts.append(f"[대화 {i+1}]\n{doc}")
        sources.append({
            "text": doc[:200] + "..." if len(doc) > 200 else doc,
            "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
            "distance": results['distances'][0][i] if results['distances'] else 0
        })
    
    context = "\n\n".join(context_parts[:5])  # 상위 5개만 사용
    
    # 답변 생성
    answer = generate_answer(query.question, context)
    
    return SearchResult(
        answer=answer,
        sources=sources[:5],  # 상위 5개 소스만 반환
        query=query.question
    )
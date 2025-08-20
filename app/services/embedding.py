from typing import List, Dict
from app.core.database import get_collection
from app.services.llm_service import get_embeddings
from app.services.slack_data import parse_slack_export, chunk_messages
from app.core.config import settings
import uuid

def index_slack_data(file_path: str, progress_callback=None, clear_existing=True):
    """슬랙 데이터를 파싱하고 임베딩하여 ChromaDB에 저장"""
    
    # 슬랙 데이터 파싱
    if progress_callback:
        progress_callback("슬랙 데이터 파싱 중...")
    messages = parse_slack_export(file_path)
    
    # 메시지 청킹
    if progress_callback:
        progress_callback(f"{len(messages)}개 메시지를 청크로 분할 중...")
    chunks = chunk_messages(messages, settings.max_tokens_per_chunk)
    
    # 텍스트 추출
    texts = [chunk["text"] for chunk in chunks]
    
    # 임베딩 생성
    if progress_callback:
        progress_callback(f"{len(chunks)}개 청크의 임베딩 생성 중...")
    embeddings = get_embeddings(texts)
    
    # ChromaDB에 저장
    if progress_callback:
        progress_callback("ChromaDB에 저장 중...")
    collection = get_collection()
    
    # 기존 데이터 삭제 (clear_existing이 True일 때만)
    if clear_existing:
        try:
            collection.delete(where={})
        except:
            pass
    
    # 새 데이터 추가
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    
    if progress_callback:
        progress_callback(f"인덱싱 완료! {len(chunks)}개 청크 저장됨")
    
    return len(chunks)

def index_multiple_files(file_paths: List[str], progress_callback=None):
    """여러 슬랙 export 파일을 파싱하고 임베딩하여 ChromaDB에 저장"""
    
    all_messages = []
    
    # 모든 파일에서 메시지 파싱
    for i, file_path in enumerate(file_paths):
        if progress_callback:
            progress_callback(f"파일 {i+1}/{len(file_paths)} 파싱 중: {file_path}")
        
        try:
            messages = parse_slack_export(file_path)
            all_messages.extend(messages)
        except Exception as e:
            print(f"파일 파싱 실패 {file_path}: {str(e)}")
            continue
    
    if not all_messages:
        return 0
    
    # 메시지 청킹
    if progress_callback:
        progress_callback(f"총 {len(all_messages)}개 메시지를 청크로 분할 중...")
    chunks = chunk_messages(all_messages, settings.max_tokens_per_chunk)
    
    # 텍스트 추출
    texts = [chunk["text"] for chunk in chunks]
    
    # 임베딩 생성
    if progress_callback:
        progress_callback(f"{len(chunks)}개 청크의 임베딩 생성 중...")
    embeddings = get_embeddings(texts)
    
    # ChromaDB에 저장
    if progress_callback:
        progress_callback("ChromaDB에 저장 중...")
    collection = get_collection()
    
    # 기존 데이터는 유지하고 새로운 데이터 추가 (append 방식)
    # 만약 기존 데이터를 삭제하고 싶다면 첫 번째 파일 처리 시에만 삭제
    
    # 새 데이터 추가
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    # 파일명 정보를 메타데이터에 추가
    for i, metadata in enumerate(metadatas):
        metadata["source_files_count"] = len(file_paths)
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    
    if progress_callback:
        progress_callback(f"인덱싱 완료! {len(file_paths)}개 파일에서 {len(chunks)}개 청크 저장됨")
    
    return len(chunks)
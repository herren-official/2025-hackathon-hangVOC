#!/usr/bin/env python3
"""
Mock 데이터를 ChromaDB에 직접 저장하는 스크립트
OpenAI API 없이 테스트용 랜덤 임베딩을 생성합니다
"""
import json
import uuid
import random
import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()

# ChromaDB 설정
persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "slack_messages")

# 데이터 로드
with open("data/sample_slack_data.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(
    path=persist_directory,
    settings=Settings(anonymized_telemetry=False)
)

# 컬렉션 생성 또는 가져오기
try:
    collection = client.get_collection(name=collection_name)
    # 기존 데이터 삭제
    collection.delete(where={})
    print(f"기존 컬렉션 '{collection_name}' 초기화")
except:
    collection = client.create_collection(name=collection_name)
    print(f"새 컬렉션 '{collection_name}' 생성")

# 메시지를 문서로 변환
documents = []
metadatas = []
ids = []
embeddings = []

for msg in messages:
    if msg.get("type") == "message" and msg.get("text"):
        # 문서 텍스트
        doc_text = msg["text"]
        documents.append(doc_text)
        
        # 메타데이터
        metadata = {
            "user": msg.get("user", "unknown"),
            "channel": msg.get("channel", "general"),
            "timestamp": msg.get("ts", "0")
        }
        metadatas.append(metadata)
        
        # ID 생성
        ids.append(str(uuid.uuid4()))
        
        # Mock 임베딩 생성 (1536 차원의 랜덤 벡터)
        # 실제로는 OpenAI API를 사용하지만 테스트용으로 랜덤 벡터 사용
        mock_embedding = [random.random() for _ in range(1536)]
        embeddings.append(mock_embedding)

# 데이터 저장
if documents:
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print(f"\n✅ {len(documents)}개의 메시지를 ChromaDB에 저장했습니다!")
    
    # 저장된 데이터 확인
    count = collection.count()
    print(f"총 저장된 문서 수: {count}")
    
    # 샘플 조회
    results = collection.get(limit=3, include=["metadatas", "documents"])
    print("\n저장된 샘플 데이터:")
    for i, (doc_id, doc, meta) in enumerate(zip(
        results['ids'], 
        results['documents'], 
        results['metadatas']
    ), 1):
        print(f"\n[{i}] 채널: {meta['channel']}, 사용자: {meta['user']}")
        print(f"    내용: {doc[:50]}...")
else:
    print("저장할 메시지가 없습니다.")

print("\n💡 참고: 이 데이터는 테스트용 Mock 임베딩을 사용합니다.")
print("실제 검색 기능을 사용하려면 유효한 OpenAI API 키가 필요합니다.")
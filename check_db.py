#!/usr/bin/env python3
import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ChromaDB 설정
persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "slack_messages")

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(
    path=persist_directory,
    settings=Settings(anonymized_telemetry=False)
)

# 컬렉션 목록 확인
collections = client.list_collections()
print(f"현재 컬렉션 목록: {[col.name for col in collections]}")

# 컬렉션이 있으면 데이터 확인
if collections:
    try:
        collection = client.get_collection(name=collection_name)
        
        # 컬렉션 정보
        count = collection.count()
        print(f"\n'{collection_name}' 컬렉션 정보:")
        print(f"- 저장된 문서 수: {count}")
        
        if count > 0:
            # 샘플 데이터 조회 (최대 5개)
            results = collection.get(
                limit=min(5, count),
                include=["metadatas", "documents"]
            )
            
            print(f"\n샘플 데이터 (최대 5개):")
            print("-" * 50)
            
            for i, (doc_id, doc, metadata) in enumerate(zip(
                results['ids'], 
                results['documents'], 
                results['metadatas']
            ), 1):
                print(f"\n[{i}] ID: {doc_id}")
                print(f"    채널: {metadata.get('channel', 'N/A')}")
                print(f"    사용자: {metadata.get('user', 'N/A')}")
                print(f"    타임스탬프: {metadata.get('timestamp', 'N/A')}")
                print(f"    내용: {doc[:100]}..." if len(doc) > 100 else f"    내용: {doc}")
            
            # 채널별 통계
            all_metadata = collection.get(include=["metadatas"])['metadatas']
            channels = {}
            for meta in all_metadata:
                channel = meta.get('channel', 'unknown')
                channels[channel] = channels.get(channel, 0) + 1
            
            print(f"\n채널별 메시지 수:")
            for channel, count in sorted(channels.items()):
                print(f"  - {channel}: {count}개")
                
    except Exception as e:
        print(f"컬렉션 '{collection_name}'을 찾을 수 없습니다: {e}")
else:
    print(f"\n데이터베이스에 컬렉션이 없습니다.")
    print(f"먼저 'python scripts/data_import.py' 명령으로 데이터를 임포트하세요.")
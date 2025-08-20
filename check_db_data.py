#!/usr/bin/env python3
"""ChromaDB에 저장된 데이터 조회 스크립트"""

from app.core.database import get_collection
import json
from datetime import datetime

def check_db_data():
    """DB에 저장된 모든 데이터 조회"""
    
    collection = get_collection()
    
    # 1. 전체 개수
    total_count = collection.count()
    print(f"=" * 60)
    print(f"📊 ChromaDB 데이터 현황")
    print(f"=" * 60)
    print(f"총 저장된 청크 수: {total_count}개\n")
    
    if total_count == 0:
        print("❌ 저장된 데이터가 없습니다.")
        return
    
    # 2. 모든 데이터 가져오기
    results = collection.get()
    
    # 3. 메타데이터 분석
    print(f"📝 저장된 데이터 상세:")
    print(f"-" * 60)
    
    channels_set = set()
    users_set = set()
    sync_times = []
    
    for i, (doc_id, doc, metadata) in enumerate(zip(
        results['ids'], 
        results['documents'], 
        results['metadatas']
    ), 1):
        print(f"\n[청크 {i}]")
        print(f"  ID: {doc_id[:8]}...")
        
        # 텍스트 미리보기 (첫 100자)
        preview = doc[:100].replace('\n', ' ')
        print(f"  텍스트: {preview}...")
        
        # 메타데이터
        print(f"  메타데이터:")
        print(f"    - 메시지 수: {metadata.get('message_count', 'N/A')}")
        # 새 형식과 구 형식 모두 지원
        if 'timestamp' in metadata:
            print(f"    - 타임스탬프: {metadata.get('timestamp', 'N/A')}")
            print(f"    - 사용자: {metadata.get('user', 'N/A')}")
        else:
            print(f"    - 시작 시간: {metadata.get('first_ts', 'N/A')}")
            print(f"    - 종료 시간: {metadata.get('last_ts', 'N/A')}")
            print(f"    - 참여 사용자: {metadata.get('users', 'N/A')}")
        
        # Slack API로 가져온 데이터인 경우
        if 'sync_time' in metadata:
            sync_time = metadata['sync_time']
            print(f"    - 동기화 시간: {sync_time}")
            sync_times.append(sync_time)
        
        # 소스 정보
        source = metadata.get('source', 'file_upload')
        print(f"    - 소스: {source}")
        
        # 통계 수집
        if 'users' in metadata:
            for user in metadata['users'].split(', '):
                if user:
                    users_set.add(user)
    
    # 4. 전체 통계
    print(f"\n{'=' * 60}")
    print(f"📈 전체 통계")
    print(f"{'=' * 60}")
    print(f"총 청크 수: {total_count}개")
    print(f"고유 사용자 수: {len(users_set)}명")
    
    if users_set:
        print(f"사용자 목록: {', '.join(sorted(users_set)[:10])}")
        if len(users_set) > 10:
            print(f"  ... 외 {len(users_set) - 10}명")
    
    if sync_times:
        latest_sync = max(sync_times)
        print(f"최근 동기화: {latest_sync}")
    
    # 5. 샘플 검색 테스트
    print(f"\n{'=' * 60}")
    print(f"🔍 샘플 검색 테스트")
    print(f"{'=' * 60}")
    
    # 임베딩으로 검색 (테스트 쿼리)
    from app.services.llm_service import get_embeddings
    test_query = "테스트"
    query_embedding = get_embeddings([test_query])[0]
    
    search_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    if search_results['documents'][0]:
        print(f"'{test_query}' 검색 결과 (상위 3개):")
        for i, (doc, distance) in enumerate(zip(
            search_results['documents'][0], 
            search_results['distances'][0]
        ), 1):
            preview = doc[:100].replace('\n', ' ')
            print(f"\n  {i}. 유사도: {1 - distance:.2%}")
            print(f"     내용: {preview}...")

def export_to_json():
    """DB 데이터를 JSON으로 내보내기"""
    collection = get_collection()
    results = collection.get()
    
    data = []
    for doc_id, doc, metadata in zip(
        results['ids'], 
        results['documents'], 
        results['metadatas']
    ):
        data.append({
            'id': doc_id,
            'text': doc,
            'metadata': metadata
        })
    
    filename = f"db_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 데이터를 {filename}에 저장했습니다.")
    return filename

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--export':
        export_to_json()
    else:
        check_db_data()
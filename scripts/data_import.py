#!/usr/bin/env python
"""
슬랙 데이터 임포트 스크립트
커맨드라인에서 직접 슬랙 export 파일을 인덱싱할 때 사용
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding import index_slack_data
import argparse

def main():
    parser = argparse.ArgumentParser(description='슬랙 데이터 인덱싱')
    parser.add_argument('file_path', help='슬랙 export JSON 파일 경로')
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"파일을 찾을 수 없습니다: {args.file_path}")
        sys.exit(1)
    
    print(f"파일 인덱싱 시작: {args.file_path}")
    
    def progress_callback(message):
        print(f"[진행] {message}")
    
    try:
        chunk_count = index_slack_data(args.file_path, progress_callback)
        print(f"\n✅ 인덱싱 완료! 총 {chunk_count}개 청크가 생성되었습니다.")
    except Exception as e:
        print(f"\n❌ 인덱싱 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
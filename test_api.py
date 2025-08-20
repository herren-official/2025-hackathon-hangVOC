#!/usr/bin/env python3
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    # 간단한 임베딩 테스트
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="테스트 문장입니다"
    )
    print("✅ 임베딩 생성 성공!")
    print(f"임베딩 차원: {len(response.data[0].embedding)}")
    
except Exception as e:
    print(f"❌ 에러 발생: {e}")
    print(f"에러 타입: {type(e).__name__}")
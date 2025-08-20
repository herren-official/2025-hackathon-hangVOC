# Slack Q&A Search API 사용 가이드

## API 엔드포인트

### Slack API 연동 (새로운 기능! 🚀)

#### 1. Slack 채널 목록 조회
**GET** `/api/v1/slack/channels`

워크스페이스의 모든 채널 목록을 가져옵니다.

```bash
curl -X GET "http://localhost:8000/api/v1/slack/channels"
```

#### 2. Slack 메시지 동기화
**POST** `/api/v1/slack/sync`

최근 Slack 메시지를 자동으로 가져와서 인덱싱합니다.

```bash
# 최근 24시간 메시지 동기화
curl -X POST "http://localhost:8000/api/v1/slack/sync?hours_back=24"

# 특정 채널만 동기화
curl -X POST "http://localhost:8000/api/v1/slack/sync?hours_back=48&channels=general&channels=random"
```

#### 3. Slack 실시간 검색
**POST** `/api/v1/slack/search`

Slack API를 직접 사용하여 실시간 검색합니다.

```bash
curl -X POST "http://localhost:8000/api/v1/slack/search?query=프로젝트&count=10"
```

### 파일 업로드 방식

#### 1. 단일 파일 업로드
**POST** `/api/v1/index`

JSON 파일 하나를 업로드하여 인덱싱합니다.

```bash
curl -X POST "http://localhost:8000/api/v1/index" \
  -F "file=@path/to/slack_data.json"
```

### 2. 다중 파일 업로드
**POST** `/api/v1/index-multiple`

여러 JSON 파일을 동시에 업로드하여 인덱싱합니다.

```bash
curl -X POST "http://localhost:8000/api/v1/index-multiple" \
  -F "files=@file1.json" \
  -F "files=@file2.json" \
  -F "files=@file3.json"
```

### 3. 폴더 업로드 (ZIP)
**POST** `/api/v1/index-folder`

JSON 파일들이 포함된 ZIP 파일을 업로드하여 모든 파일을 인덱싱합니다.

```bash
# ZIP 파일 생성
zip slack_data.zip *.json

# 업로드
curl -X POST "http://localhost:8000/api/v1/index-folder" \
  -F "folder=@slack_data.zip"
```

### 4. 검색
**POST** `/api/v1/search`

인덱싱된 데이터에서 질문에 대한 답변을 검색합니다.

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"question": "프로젝트 마감일은 언제인가요?"}'
```

응답 예시:
```json
{
  "answer": "프로젝트 마감일은 다음 달 15일입니다.",
  "sources": [
    {
      "text": "관련 대화 내용...",
      "metadata": {
        "first_ts": "1703001600.000001",
        "last_ts": "1703010100.000020",
        "message_count": 20,
        "users": "U001, U002, U003"
      },
      "distance": 0.7039
    }
  ],
  "query": "프로젝트 마감일은 언제인가요?"
}
```

## 주요 기능

### 다중 파일 처리
- **단일 파일**: 기존 데이터를 대체하며 새로 인덱싱
- **다중 파일**: 여러 파일의 데이터를 병합하여 인덱싱
- **ZIP 폴더**: ZIP 내 모든 JSON 파일을 자동으로 찾아 인덱싱

### 임베딩 모델
- **기본**: sentence-transformers (로컬, 무료)
- **선택적**: OpenAI 또는 Claude API 사용 가능

### 데이터 저장
- ChromaDB를 사용한 벡터 데이터베이스
- 메타데이터 포함 (사용자, 타임스탬프, 메시지 수 등)

## 환경 설정

`.env` 파일에서 API 제공자와 모델을 설정할 수 있습니다:

```bash
# API Provider ('claude' 또는 'openai')
API_PROVIDER=claude

# Claude API (선택적)
CLAUDE_API_KEY=your_api_key_here

# OpenAI API (선택적)
OPENAI_API_KEY=your_api_key_here

# 임베딩 모델
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 사용 예시

### 전체 워크플로우

1. **데이터 준비**: Slack export JSON 파일들 준비
2. **데이터 인덱싱**: 
   - 단일 파일: `/api/v1/index`
   - 여러 파일: `/api/v1/index-multiple`
   - ZIP 폴더: `/api/v1/index-folder`
3. **검색**: `/api/v1/search`로 질문하여 답변 받기

### Python 클라이언트 예시

```python
import requests

# 다중 파일 업로드
files = [
    ('files', open('data1.json', 'rb')),
    ('files', open('data2.json', 'rb')),
    ('files', open('data3.json', 'rb'))
]
response = requests.post('http://localhost:8000/api/v1/index-multiple', files=files)
print(response.json())

# 검색
query = {"question": "프로젝트 진행 상황은 어떤가요?"}
response = requests.post('http://localhost:8000/api/v1/search', json=query)
print(response.json()['answer'])
```
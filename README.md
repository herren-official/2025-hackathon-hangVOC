# 🔍 Slack Q&A Instant Search System

2025 행정안전부 해커톤 - 슬랙 대화 내용 기반 지능형 Q&A 검색 시스템

사내 슬랙 대화를 임베딩·검색·요약하여 개발자/PM이 몇 초 만에 과거 해결책을 찾도록 돕는 브라우저 기반 웹 애플리케이션입니다.

## 📋 주요 기능

- **슬랙 데이터 임포트**: Slack export JSON 파일 업로드 및 자동 파싱
- **다중 파일 지원**: 
  - 단일 JSON 파일 업로드
  - 여러 JSON 파일 동시 업로드
  - ZIP 폴더 전체 업로드
- **지능형 검색**: 벡터 임베딩을 활용한 의미 기반 검색
- **즉시 답변**: 자연어 질문에 대한 요약 답변 생성
- **다양한 LLM 지원**: OpenAI, Claude, 또는 로컬 임베딩 모델 선택 가능
- **근거 제시**: 답변의 근거가 되는 원본 슬랙 메시지 표시
- **빠른 응답**: 5초 이내 검색 결과 제공

## 🚀 빠른 시작

### 1. 사전 요구사항

- Python 3.8 이상
- API 키 (선택적):
  - OpenAI API 키 또는
  - Claude API 키
- Slack workspace export 파일 (JSON 형식)

### 2. 설치

```bash
# 저장소 클론
git clone https://github.com/herren-official/2025-hackathon-hangVOC.git
cd 2025-hackathon-hangVOC

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어 API 설정
# API_PROVIDER=claude  # 'claude' 또는 'openai'
# CLAUDE_API_KEY=your_claude_api_key  # Claude 사용시
# OPENAI_API_KEY=your_openai_api_key  # OpenAI 사용시
```

**참고**: API 키가 없어도 로컬 sentence-transformers를 사용하여 임베딩 가능합니다.

### 4. 실행

#### 백엔드 API 서버 실행
```bash
# FastAPI 서버 시작
python -m app.main
```
API 문서: http://localhost:8000/docs

#### 프론트엔드 UI 실행 (선택적)
```bash
# 새 터미널에서 Streamlit 앱 시작
streamlit run streamlit_app/main.py
```
웹 UI: http://localhost:8501

## 📁 프로젝트 구조

```
2025-hackathon-hangVOC/
├── app/                      # FastAPI 백엔드
│   ├── api/                  # API 엔드포인트
│   ├── core/                 # 설정 및 데이터베이스
│   ├── services/             # 비즈니스 로직
│   ├── models/               # 데이터 모델
│   └── main.py               # FastAPI 앱 진입점
├── streamlit_app/            # Streamlit 프론트엔드
│   ├── main.py               # Streamlit 앱 메인
│   └── utils.py              # 유틸리티 함수
├── scripts/                  # 유틸리티 스크립트
├── data/                     # 샘플 데이터
├── requirements.txt          # Python 의존성
├── .env.example              # 환경 변수 템플릿
├── API_USAGE.md              # API 상세 문서
└── README.md                 # 프로젝트 문서
```

## 🔧 사용 방법

### 1. 슬랙 데이터 준비

1. Slack workspace에서 데이터 export
   - Workspace 설정 → Import/Export Data → Export → Start Export
2. Export 완료 후 JSON 파일 다운로드

### 2. 데이터 인덱싱

#### 방법 1: API 사용

```bash
# 단일 파일 업로드
curl -X POST "http://localhost:8000/api/v1/index" \
  -F "file=@slack_data.json"

# 다중 파일 업로드
curl -X POST "http://localhost:8000/api/v1/index-multiple" \
  -F "files=@file1.json" \
  -F "files=@file2.json" \
  -F "files=@file3.json"

# ZIP 폴더 업로드
zip slack_data.zip *.json
curl -X POST "http://localhost:8000/api/v1/index-folder" \
  -F "folder=@slack_data.zip"
```

#### 방법 2: Streamlit UI 사용

1. Streamlit UI (http://localhost:8501) 접속
2. 사이드바에서 "📤 슬랙 데이터 업로드" 섹션 찾기
3. JSON 파일 선택 후 "🚀 인덱싱 시작" 클릭

### 3. 검색 사용

```bash
# API로 검색
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"question": "프로젝트 마감일은 언제인가요?"}'
```

또는 Streamlit UI에서:
1. 메인 화면의 검색창에 질문 입력
2. "🔍 검색" 버튼 클릭
3. AI가 생성한 답변 확인

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **Vector DB**: ChromaDB
- **Embedding**: 
  - sentence-transformers (로컬, 무료)
  - OpenAI Embeddings (선택적)
- **LLM**: 
  - OpenAI GPT (gpt-4o-mini)
  - Claude (claude-3-haiku)
- **Data Processing**: Pandas, NumPy

## ⚙️ 환경 변수 설정

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `API_PROVIDER` | LLM 제공자 ('claude' 또는 'openai') | claude |
| `CLAUDE_API_KEY` | Claude API 키 | (선택적) |
| `OPENAI_API_KEY` | OpenAI API 키 | (선택적) |
| `EMBEDDING_MODEL` | 임베딩 모델 | sentence-transformers/all-MiniLM-L6-v2 |
| `MAX_TOKENS_PER_CHUNK` | 청크당 최대 토큰 | 1000 |
| `SEARCH_TOP_K` | 검색 결과 개수 | 10 |

## 📊 성능 목표

- **응답 시간**: ≤ 5초
- **정확도**: 3회 이내 검색으로 원하는 답변 찾기 ≥ 80%
- **사용률**: 주간 활성 사용자 ≥ 60%

## 🔍 API 엔드포인트

자세한 API 문서는 [API_USAGE.md](API_USAGE.md)를 참조하세요.

### 주요 엔드포인트

- `POST /api/v1/search` - 질문에 대한 답변 검색
- `POST /api/v1/index` - 단일 파일 업로드
- `POST /api/v1/index-multiple` - 다중 파일 업로드
- `POST /api/v1/index-folder` - ZIP 폴더 업로드

## 🐛 문제 해결

### API 키 없이 사용하기
- `.env`에서 `API_PROVIDER=claude`로 설정
- CLAUDE_API_KEY를 비워두면 자동으로 sentence-transformers 사용

### ChromaDB 오류
```bash
# ChromaDB 초기화
rm -rf chroma_db/
```

### 메모리 부족
- `MAX_TOKENS_PER_CHUNK` 값을 줄여서 청크 크기 감소

## 📝 라이센스

MIT License

## 🤝 기여

이슈 및 PR을 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 팀

2025 행정안전부 해커톤 참가팀

## 📧 문의

프로젝트 관련 문의사항은 이슈를 통해 남겨주세요.
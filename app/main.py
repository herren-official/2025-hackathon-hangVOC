from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.core.config import settings
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Slack Q&A Search API",
    description="슬랙 대화 내용 검색 및 요약 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Slack Q&A Search API", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행되는 이벤트"""
    logger.info("🚀 Slack Q&A Search API 시작")
    
    # Slack 자동 동기화 스케줄러 시작
    if settings.slack_auto_sync_enabled and settings.slack_bot_token:
        try:
            from app.services.scheduler import scheduler
            scheduler.start()
            logger.info(f"✅ Slack 자동 동기화 활성화 (간격: {settings.slack_sync_interval_minutes}분)")
        except Exception as e:
            logger.error(f"❌ Slack 자동 동기화 시작 실패: {e}")
    else:
        logger.info("ℹ️ Slack 자동 동기화 비활성화 상태")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행되는 이벤트"""
    logger.info("👋 Slack Q&A Search API 종료")
    
    # 스케줄러 중지
    try:
        from app.services.scheduler import scheduler
        scheduler.stop()
    except:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
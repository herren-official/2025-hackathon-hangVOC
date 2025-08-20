"""자동 Slack 동기화 스케줄러"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from app.services.slack_realtime import SlackRealtime
from app.core.config import settings
import threading
import time

logger = logging.getLogger(__name__)

class SlackSyncScheduler:
    def __init__(self):
        self.is_running = False
        self.sync_thread = None
        self.last_sync_time = None
        self.sync_interval = settings.slack_sync_interval_minutes * 60  # 분을 초로 변환
        self.sync_hours_back = settings.slack_sync_hours_back
        
    def start(self):
        """백그라운드 스케줄러 시작"""
        if self.is_running:
            logger.info("스케줄러가 이미 실행 중입니다.")
            return
            
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.sync_thread.start()
        logger.info(f"Slack 자동 동기화 시작 (간격: {settings.slack_sync_interval_minutes}분)")
        
    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Slack 자동 동기화 중지됨")
        
    def _run_scheduler(self):
        """백그라운드에서 실행되는 스케줄러 루프"""
        # 시작 시 즉시 한 번 동기화
        self._sync_messages()
        
        while self.is_running:
            try:
                # 설정된 간격만큼 대기
                time.sleep(self.sync_interval)
                
                if self.is_running:
                    self._sync_messages()
                    
            except Exception as e:
                logger.error(f"스케줄러 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기
                
    def _sync_messages(self):
        """Slack 메시지 동기화 실행"""
        try:
            logger.info("🔄 Slack 메시지 자동 동기화 시작...")
            
            # Slack API 클라이언트 생성
            slack = SlackRealtime()
            
            # 연결 테스트
            connection = slack.test_connection()
            if connection["status"] == "error":
                logger.error(f"Slack 연결 실패: {connection['error']}")
                return
                
            # 메시지 동기화
            result = slack.sync_recent_messages(
                hours_back=self.sync_hours_back,
                channels=None  # 모든 공개 채널
            )
            
            self.last_sync_time = datetime.now()
            
            logger.info(f"✅ 자동 동기화 완료: "
                       f"{result['channels_synced']}개 채널, "
                       f"{result['messages_collected']}개 메시지, "
                       f"{result['chunks_created']}개 청크 생성")
            
            if result['errors']:
                logger.warning(f"동기화 중 오류: {result['errors']}")
                
        except Exception as e:
            logger.error(f"자동 동기화 실패: {e}")
            
    def get_status(self):
        """스케줄러 상태 반환"""
        return {
            "is_running": self.is_running,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "sync_interval_minutes": settings.slack_sync_interval_minutes,
            "sync_hours_back": self.sync_hours_back,
            "next_sync_time": (
                datetime.fromtimestamp(
                    self.last_sync_time.timestamp() + self.sync_interval
                ).isoformat()
                if self.last_sync_time else None
            )
        }

# 전역 스케줄러 인스턴스
scheduler = SlackSyncScheduler()
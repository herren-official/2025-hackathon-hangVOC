"""Slack API를 통한 실시간 메시지 동기화"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
import certifi
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from app.models.message import SlackMessage
from app.services.embedding import index_slack_data
from app.services.slack_data import chunk_messages
from app.core.database import get_collection
from app.services.llm_service import get_embeddings
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class SlackRealtime:
    def __init__(self, token: str = None):
        """Slack API 클라이언트 초기화"""
        self.token = token or os.getenv("SLACK_BOT_TOKEN") or settings.slack_bot_token
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN이 설정되지 않았습니다.")
        
        # SSL 컨텍스트 생성
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(token=self.token, ssl=ssl_context)
        self.user_cache = {}  # 사용자 정보 캐시
        
    def test_connection(self) -> Dict:
        """Slack API 연결 테스트"""
        try:
            response = self.client.auth_test()
            return {
                "status": "success",
                "team": response["team"],
                "user": response["user"],
                "bot_id": response.get("bot_id"),
                "is_enterprise": response.get("is_enterprise_install", False)
            }
        except SlackApiError as e:
            logger.error(f"Slack 연결 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_channels(self) -> List[Dict]:
        """워크스페이스의 모든 채널 목록 가져오기"""
        channels = []
        try:
            # 공개 채널만 가져오기 (private_channel 제거)
            for page in self.client.conversations_list(
                types="public_channel",
                limit=100
            ):
                channels.extend(page["channels"])
                
            return [{
                "id": ch["id"],
                "name": ch["name"],
                "is_private": ch.get("is_private", False),
                "num_members": ch.get("num_members", 0)
            } for ch in channels]
            
        except SlackApiError as e:
            logger.error(f"채널 목록 가져오기 실패: {e}")
            return []
    
    def get_user_info(self, user_id: str) -> str:
        """사용자 정보 가져오기 (캐시 사용)"""
        if user_id in self.user_cache:
            return self.user_cache[user_id]
            
        try:
            response = self.client.users_info(user=user_id)
            real_name = response["user"].get("real_name", user_id)
            self.user_cache[user_id] = real_name
            return real_name
        except:
            self.user_cache[user_id] = user_id
            return user_id
    
    def get_channel_messages(
        self, 
        channel_id: str, 
        hours_back: int = 24,
        limit: int = 1000
    ) -> List[SlackMessage]:
        """특정 채널의 메시지 가져오기"""
        messages = []
        
        # 시작 시간 설정
        oldest = datetime.now() - timedelta(hours=hours_back)
        oldest_ts = str(oldest.timestamp())
        
        try:
            # 먼저 봇이 채널에 참여했는지 확인
            try:
                self.client.conversations_join(channel=channel_id)
            except SlackApiError as e:
                if "already_in_channel" not in str(e):
                    logger.warning(f"채널 참여 실패 {channel_id}: {e}")
                    
            # 메시지 가져오기
            response = self.client.conversations_history(
                channel=channel_id,
                oldest=oldest_ts,
                limit=limit
            )
            
            for msg in response.get("messages", []):
                # 봇 메시지나 시스템 메시지 제외
                if msg.get("subtype") in ["bot_message", "channel_join", "channel_leave"]:
                    continue
                
                if not msg.get("text"):
                    continue
                    
                user_id = msg.get("user", "unknown")
                user_name = self.get_user_info(user_id) if user_id != "unknown" else "Unknown"
                
                messages.append(SlackMessage(
                    user=user_name,
                    text=msg.get("text", ""),
                    ts=msg.get("ts", ""),
                    channel=channel_id,
                    thread_ts=msg.get("thread_ts")
                ))
                
        except SlackApiError as e:
            logger.error(f"메시지 가져오기 실패 (채널: {channel_id}): {e}")
            
        return messages
    
    def sync_recent_messages(
        self, 
        hours_back: int = 24,
        channels: Optional[List[str]] = None,
        progress_callback=None
    ) -> Dict:
        """최근 메시지를 DB에 동기화
        
        Args:
            hours_back: 몇 시간 전까지의 메시지를 가져올지 (기본: 24시간)
            channels: 특정 채널만 동기화 (None이면 모든 공개 채널)
            progress_callback: 진행상황 콜백
        """
        all_messages = []
        sync_result = {
            "channels_synced": 0,
            "messages_collected": 0,
            "chunks_created": 0,
            "errors": []
        }
        
        # 채널 목록 가져오기
        if channels:
            channel_list = [{"id": ch, "name": ch} for ch in channels]
        else:
            channel_list = self.get_channels()
            
        if progress_callback:
            progress_callback(f"총 {len(channel_list)}개 채널 동기화 시작...")
        
        # 각 채널의 메시지 가져오기
        for idx, channel in enumerate(channel_list):
            channel_id = channel["id"]
            channel_name = channel.get("name", channel_id)
            
            if progress_callback:
                progress_callback(f"[{idx+1}/{len(channel_list)}] #{channel_name} 채널 동기화 중...")
            
            try:
                messages = self.get_channel_messages(
                    channel_id=channel_id,
                    hours_back=hours_back
                )
                
                # 채널 이름을 메시지에 추가
                for msg in messages:
                    msg.channel = channel_name
                    
                all_messages.extend(messages)
                sync_result["channels_synced"] += 1
                
                if messages:
                    logger.info(f"채널 #{channel_name}: {len(messages)}개 메시지 수집")
                    
            except Exception as e:
                error_msg = f"채널 #{channel_name} 동기화 실패: {str(e)}"
                sync_result["errors"].append(error_msg)
                logger.error(error_msg)
        
        sync_result["messages_collected"] = len(all_messages)
        
        # 메시지가 있으면 DB에 저장
        if all_messages:
            if progress_callback:
                progress_callback(f"총 {len(all_messages)}개 메시지 인덱싱 중...")
            
            # 메시지 청킹
            chunks = chunk_messages(all_messages, settings.max_tokens_per_chunk)
            texts = [chunk["text"] for chunk in chunks]
            
            # 임베딩 생성
            if progress_callback:
                progress_callback(f"{len(chunks)}개 청크 임베딩 생성 중...")
            embeddings = get_embeddings(texts)
            
            # ChromaDB에 저장 (중복 제거)
            collection = get_collection()
            
            # 기존 Slack API 데이터 삭제 (동일 시간대 중복 방지)
            try:
                existing_data = collection.get(
                    where={"source": "slack_api"}
                )
                if existing_data and existing_data['ids']:
                    # 동일한 hours_back 범위의 기존 데이터만 삭제
                    ids_to_delete = []
                    for idx, metadata in enumerate(existing_data['metadatas']):
                        if metadata.get('hours_back') == hours_back:
                            ids_to_delete.append(existing_data['ids'][idx])
                    
                    if ids_to_delete:
                        collection.delete(ids=ids_to_delete)
                        logger.info(f"기존 데이터 {len(ids_to_delete)}개 삭제 (hours_back={hours_back})")
            except Exception as e:
                logger.warning(f"기존 데이터 삭제 중 오류: {e}")
            
            # 새 데이터 추가
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # 실시간 동기화 정보 추가
            for metadata in metadatas:
                metadata["sync_time"] = datetime.now().isoformat()
                metadata["source"] = "slack_api"
                metadata["hours_back"] = hours_back
            
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            sync_result["chunks_created"] = len(chunks)
            
            if progress_callback:
                progress_callback(f"✅ 동기화 완료! {len(chunks)}개 청크 생성됨")
        else:
            if progress_callback:
                progress_callback("동기화할 새 메시지가 없습니다.")
        
        return sync_result
    
    def search_in_slack(self, query: str, count: int = 20) -> List[Dict]:
        """Slack 검색 API를 직접 사용 (실시간 검색)"""
        try:
            response = self.client.search_messages(
                query=query,
                sort="timestamp",
                sort_dir="desc",
                count=count
            )
            
            results = []
            for match in response["messages"]["matches"]:
                results.append({
                    "text": match.get("text", ""),
                    "user": self.get_user_info(match.get("user", "")),
                    "channel": match.get("channel", {}).get("name", ""),
                    "timestamp": match.get("ts", ""),
                    "permalink": match.get("permalink", "")
                })
                
            return results
            
        except SlackApiError as e:
            logger.error(f"Slack 검색 실패: {e}")
            return []
import json
from typing import List, Dict
from app.models.message import SlackMessage
import re

def parse_slack_export(file_path: str) -> List[SlackMessage]:
    """슬랙 export JSON 파일 파싱"""
    messages = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 슬랙 export 형식에 따라 파싱
    if isinstance(data, list):
        # 단일 채널 메시지 리스트
        for msg in data:
            if 'text' in msg and msg['text']:
                messages.append(SlackMessage(
                    user=msg.get('user'),
                    text=clean_text(msg['text']),
                    ts=msg.get('ts', ''),
                    thread_ts=msg.get('thread_ts')
                ))
    elif isinstance(data, dict):
        # 여러 채널이 포함된 export
        for channel_name, channel_messages in data.items():
            if isinstance(channel_messages, list):
                for msg in channel_messages:
                    if 'text' in msg and msg['text']:
                        messages.append(SlackMessage(
                            user=msg.get('user'),
                            text=clean_text(msg['text']),
                            ts=msg.get('ts', ''),
                            channel=channel_name,
                            thread_ts=msg.get('thread_ts')
                        ))
    
    return messages

def clean_text(text: str) -> str:
    """슬랙 메시지 텍스트 정제"""
    # 사용자 멘션 처리
    text = re.sub(r'<@[A-Z0-9]+>', '@user', text)
    # 채널 멘션 처리
    text = re.sub(r'<#[A-Z0-9]+\|([^>]+)>', r'#\1', text)
    # URL 처리
    text = re.sub(r'<(http[^|>]+)\|([^>]+)>', r'\2', text)
    text = re.sub(r'<(http[^>]+)>', r'\1', text)
    
    return text.strip()

def chunk_messages(messages: List[SlackMessage], max_tokens: int = 1000) -> List[Dict]:
    """메시지를 개별 청크로 변환 - 1메시지 = 1청크"""
    chunks = []
    
    for msg in messages:
        # 각 메시지를 독립적인 청크로 생성
        chunk_text = f"{msg.user}: {msg.text}" if msg.user else msg.text
        
        metadata = {
            "message_count": 1,  # 항상 1
            "timestamp": msg.ts,
            "user": msg.user if msg.user else "Unknown",
            "channel": msg.channel if msg.channel else "Unknown"
        }
        
        # thread_ts는 있을 때만 추가
        if msg.thread_ts:
            metadata["thread_ts"] = msg.thread_ts
        
        chunks.append({
            "text": chunk_text,
            "metadata": metadata
        })
    
    return chunks
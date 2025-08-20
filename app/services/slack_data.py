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
    """메시지를 청크로 분할"""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for msg in messages:
        msg_tokens = len(msg.text.split())
        
        if current_tokens + msg_tokens > max_tokens and current_chunk:
            chunk_text = "\n".join([m.text for m in current_chunk])
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "message_count": len(current_chunk),
                    "first_ts": current_chunk[0].ts,
                    "last_ts": current_chunk[-1].ts,
                    "users": ", ".join(list(set([m.user for m in current_chunk if m.user])))
                }
            })
            current_chunk = []
            current_tokens = 0
        
        current_chunk.append(msg)
        current_tokens += msg_tokens
    
    if current_chunk:
        chunk_text = "\n".join([m.text for m in current_chunk])
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "message_count": len(current_chunk),
                "first_ts": current_chunk[0].ts,
                "last_ts": current_chunk[-1].ts,
                "users": ", ".join(list(set([m.user for m in current_chunk if m.user])))
            }
        })
    
    return chunks
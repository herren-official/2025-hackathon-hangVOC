from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from app.models.message import SearchQuery, SearchResult
from app.services.search import search_messages
from app.services.embedding import index_slack_data, index_multiple_files
import tempfile
import os
import zipfile
import json
from pathlib import Path

router = APIRouter()

@router.post("/search", response_model=SearchResult)
async def search(query: SearchQuery):
    """슬랙 메시지 검색 및 답변 생성"""
    try:
        result = search_messages(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index")
async def index_data(file: UploadFile = File(...)):
    """슬랙 export 파일 업로드 및 인덱싱"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 인덱싱 수행
        chunk_count = index_slack_data(tmp_file_path)
        
        # 임시 파일 삭제
        os.unlink(tmp_file_path)
        
        return {
            "status": "success",
            "message": f"Successfully indexed {chunk_count} chunks from {file.filename}",
            "chunk_count": chunk_count,
            "filename": file.filename
        }
    except Exception as e:
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index-multiple")
async def index_multiple_data(files: List[UploadFile] = File(...)):
    """여러 슬랙 export 파일 업로드 및 인덱싱"""
    results = []
    total_chunks = 0
    temp_files = []
    
    try:
        # 모든 파일을 임시 저장
        for file in files:
            if not file.filename.endswith('.json'):
                continue
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)
        
        # 여러 파일 인덱싱
        if temp_files:
            chunk_count = index_multiple_files(temp_files)
            total_chunks = chunk_count
            
            for i, file in enumerate(files):
                if file.filename.endswith('.json'):
                    results.append({
                        "filename": file.filename,
                        "status": "success"
                    })
        
        # 임시 파일 삭제
        for tmp_path in temp_files:
            os.unlink(tmp_path)
        
        return {
            "status": "success",
            "message": f"Successfully indexed {total_chunks} chunks from {len(results)} files",
            "total_chunks": total_chunks,
            "files": results
        }
    except Exception as e:
        # 에러 시 임시 파일 정리
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index-folder")
async def index_folder_data(folder: UploadFile = File(...)):
    """ZIP 폴더 업로드 및 인덱싱 (폴더 내 모든 JSON 파일 처리)"""
    temp_dir = None
    temp_zip = None
    
    try:
        # ZIP 파일인지 확인
        if not folder.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Please upload a ZIP file containing JSON files")
        
        # ZIP 파일을 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            content = await folder.read()
            tmp_zip.write(content)
            temp_zip = tmp_zip.name
        
        # 임시 디렉토리 생성 및 ZIP 압축 해제
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # JSON 파일 찾기
        json_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.json') and not file.startswith('.'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            raise HTTPException(status_code=400, detail="No JSON files found in the uploaded ZIP")
        
        # 인덱싱
        chunk_count = index_multiple_files(json_files)
        
        # 임시 파일 정리
        import shutil
        shutil.rmtree(temp_dir)
        os.unlink(temp_zip)
        
        return {
            "status": "success",
            "message": f"Successfully indexed {chunk_count} chunks from {len(json_files)} JSON files",
            "total_chunks": chunk_count,
            "file_count": len(json_files),
            "processed_files": [os.path.basename(f) for f in json_files]
        }
    except Exception as e:
        # 에러 시 임시 파일 정리
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
        if temp_zip and os.path.exists(temp_zip):
            os.unlink(temp_zip)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
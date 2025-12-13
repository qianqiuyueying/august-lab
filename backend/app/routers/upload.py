from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
from typing import List
import shutil

from .auth import get_current_user

router = APIRouter()

# 允许的图片格式
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    """检查文件格式是否允许"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """上传图片文件（需要认证）"""
    
    # 检查文件格式
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。允许的格式: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE // (1024*1024)}MB）"
        )
    
    # 生成唯一文件名
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 确保上传目录存在
    upload_dir = "uploads/images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # 返回文件访问URL
        file_url = f"/uploads/images/{unique_filename}"
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "文件上传成功",
                "filename": unique_filename,
                "url": file_url,
                "size": len(file_content)
            }
        )
        
    except Exception as e:
        # 如果保存失败，删除可能已创建的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件保存失败"
        )

@router.delete("/image/{filename}")
async def delete_image(
    filename: str,
    current_user: str = Depends(get_current_user)
):
    """删除图片文件（需要认证）"""
    
    file_path = os.path.join("uploads/images", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    try:
        os.remove(file_path)
        return JSONResponse(
            content={"message": "文件删除成功"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件删除失败"
        )
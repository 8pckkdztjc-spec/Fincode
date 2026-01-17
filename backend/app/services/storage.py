"""
文件存储服务
处理文件上传、存储和管理
使用 UUID + MD5 统一命名防止冲突
"""

import uuid
import hashlib
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from app.core.config import settings


class FileStorage:
    """文件存储服务"""
    
    def __init__(self, upload_dir: Optional[Path] = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_file_id(self, original_filename: str) -> tuple[str, Path]:
        """
        生成唯一文件 ID 和存储路径
        
        使用 UUID + 原文件名 MD5 前8位 + 扩展名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            (file_id, storage_path) 元组
        """
        file_id = str(uuid.uuid4())
        name_hash = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        ext = Path(original_filename).suffix.lower()
        
        storage_filename = f"{file_id}_{name_hash}{ext}"
        storage_path = self.upload_dir / storage_filename
        
        return file_id, storage_path
    
    async def save_upload(self, file: UploadFile) -> tuple[str, Path]:
        """
        保存上传的文件
        
        Args:
            file: FastAPI UploadFile 对象
            
        Returns:
            (file_id, storage_path) 元组
        """
        if not file.filename:
            raise ValueError("文件名不能为空")
        
        file_id, storage_path = self.generate_file_id(file.filename)
        
        # 异步写入文件
        content = await file.read()
        async with aiofiles.open(storage_path, 'wb') as f:
            await f.write(content)
        
        return file_id, storage_path
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        根据文件 ID 查找文件路径
        
        Args:
            file_id: 文件 ID
            
        Returns:
            文件路径，不存在则返回 None
        """
        # 搜索匹配的文件
        for file_path in self.upload_dir.glob(f"{file_id}_*"):
            if file_path.is_file():
                return file_path
        return None
    
    async def delete_file(self, file_id: str) -> bool:
        """
        删除文件
        
        Args:
            file_id: 文件 ID
            
        Returns:
            是否删除成功
        """
        file_path = self.get_file_path(file_id)
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def validate_extension(self, filename: str) -> bool:
        """验证文件扩展名是否允许"""
        ext = Path(filename).suffix.lower()
        return ext in settings.ALLOWED_EXTENSIONS
    
    def validate_size(self, size: int) -> bool:
        """验证文件大小是否在允许范围内"""
        return size <= settings.MAX_FILE_SIZE


# 全局实例
file_storage = FileStorage()

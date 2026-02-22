"""统一响应模型

响应格式: {"code": "0", "message": "success", "data": {...}}
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

from app.core.exceptions import ErrorCode

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应模型"""
    code: str = ErrorCode.SUCCESS
    message: str = "success"
    data: Optional[T] = None

    class Config:
        from_attributes = True

    @staticmethod
    def success(data: T = None, message: str = "success") -> "ApiResponse[T]":
        return ApiResponse(code=ErrorCode.SUCCESS, message=message, data=data)

    @staticmethod
    def error(code: ErrorCode, message: str = None) -> "ApiResponse":
        return ApiResponse(code=code, message=message or code.name, data=None)

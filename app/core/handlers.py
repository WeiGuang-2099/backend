"""FastAPI 全局异常处理器"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import BizException, ErrorCode
from app.schemas.response import ApiResponse


async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    """处理业务异常"""
    return JSONResponse(
        status_code=200,
        content=ApiResponse.error(exc.code, exc.message).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理参数验证异常"""
    errors = exc.errors()
    error_msg = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in errors])
    return JSONResponse(
        status_code=200,
        content=ApiResponse.error(ErrorCode.PARAM_FORMAT_ERROR, error_msg).model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常"""
    return JSONResponse(
        status_code=200,
        content=ApiResponse.error(ErrorCode.INTERNAL_ERROR, "Internal server error").model_dump()
    )


def register_exception_handlers(app):
    """注册异常处理器"""
    app.add_exception_handler(BizException, biz_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # 生产环境启用: app.add_exception_handler(Exception, generic_exception_handler)

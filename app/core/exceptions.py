"""自定义业务异常和错误码

错误码规范:
- 0: 成功
- 1xxxx: 通用错误
- 2xxxx: 认证授权错误
- 3xxxx: 资源错误
- 4xxxx: 业务逻辑错误
- 5xxxx: 系统错误
"""
from enum import Enum


class ErrorCode(str, Enum):
    """业务错误码"""
    SUCCESS = "0"

    # 通用错误 1xxxx
    PARAM_ERROR = "10001"
    PARAM_MISSING = "10002"
    PARAM_FORMAT_ERROR = "10003"

    # 认证授权错误 2xxxx
    UNAUTHORIZED = "20001"
    TOKEN_EXPIRED = "20002"
    TOKEN_INVALID = "20003"
    PERMISSION_DENIED = "20004"

    # 资源错误 3xxxx
    RESOURCE_NOT_FOUND = "30001"
    AGENT_NOT_FOUND = "30002"
    USER_NOT_FOUND = "30003"

    # 业务逻辑错误 4xxxx
    AGENT_CREATE_FAILED = "40001"
    AGENT_UPDATE_FAILED = "40002"
    AGENT_DELETE_FAILED = "40003"
    OPERATION_FAILED = "40004"

    # 系统错误 5xxxx
    INTERNAL_ERROR = "50001"
    DATABASE_ERROR = "50002"


class BizException(Exception):
    """业务异常基类"""

    def __init__(self, code: ErrorCode, message: str = None):
        self.code = code
        self.message = message or code.name
        super().__init__(self.message)


class NotFoundException(BizException):
    """资源未找到"""

    def __init__(self, message: str = "Resource not found", code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND):
        super().__init__(code, message)


class PermissionDeniedException(BizException):
    """权限不足"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(ErrorCode.PERMISSION_DENIED, message)


class ParamErrorException(BizException):
    """参数错误"""

    def __init__(self, message: str = "Parameter error", code: ErrorCode = ErrorCode.PARAM_ERROR):
        super().__init__(code, message)

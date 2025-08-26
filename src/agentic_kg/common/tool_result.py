
from typing import Any, Callable, Literal, TypedDict, Union, TypeGuard


class ResultSuccess(TypedDict):
    status: Literal["success"]
    result: Any


class ResultError(TypedDict):
    status: Literal["error"]
    error_message: str


ToolResult = Union[ResultSuccess, ResultError]

def tool_success(key: str, result: Any) -> ToolResult:
    """Create a successful result containing the given value.

    Args:
        key: the key to store the result under
        result: The successful result value

    Returns:
        ToolResult: success dict with the result under the given key
    """
    return {"status": "success", key: result}

def tool_error(message: str) -> ToolResult:
    """Create an error result with the given message.

    Args:
        message: The error message
        error_type: Optional exception type to use (defaults to ValueError)

    Returns:
        ToolResult: error dict
    """
    return {
        "status": "error",
        "error_message": str(message) if message is not None else "Unknown error",
    }


def is_success(result: ToolResult) -> TypeGuard[ResultSuccess]:
    return result["status"] == "success"


def is_error(result: ToolResult) -> TypeGuard[ResultError]:
    return result["status"] == "error"


def map_result(result: ToolResult, f: Callable[[Any], Any]) -> ToolResult:
    return tool_success(f(result["result"])) if is_success(result) else result


def map_error(result: ToolResult, f: Callable[[str], Any]) -> ToolResult:
    return {"status": "error", "error_message": f(result["error_message"])} if is_error(result) else result


def get_or_else(result: ToolResult, default: Any) -> Any:
    return result["result"] if is_success(result) else default


def get_or_raise(result: ToolResult) -> Any:
    if is_success(result):
        return result["result"]
    elif is_error(result):
        raise Exception(result["error_message"])

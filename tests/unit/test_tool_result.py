#!/usr/bin/env python3
"""
Comprehensive tests for the tool_result module.
"""
from agentic_kg.common.tool_result import (
    ToolResult,
    ResultSuccess,
    ResultError,
    tool_success,
    tool_error,
    is_success,
    is_error,
    map_result,
    map_error,
    get_or_else,
    get_or_raise
)


def test_tool_success():
    """Test that tool_success creates a proper success result."""
    # Test with various data types
    result_str = tool_success("hello")
    assert result_str["status"] == "success"
    assert result_str["result"] == "hello"
    
    result_int = tool_success(42)
    assert result_int["status"] == "success"
    assert result_int["result"] == 42
    
    result_dict = tool_success({"key": "value"})
    assert result_dict["status"] == "success"
    assert result_dict["result"] == {"key": "value"}
    
    result_none = tool_success(None)
    assert result_none["status"] == "success"
    assert result_none["result"] is None
    
    print("✓ tool_success creates proper success results for various data types")


def test_tool_error():
    """Test that tool_error creates a proper error result."""
    # Test with string message
    result_str = tool_error("Something went wrong")
    assert result_str["status"] == "error"
    assert result_str["error_message"] == "Something went wrong"
    
    # Test with None message (should convert to string)
    result_none = tool_error(None)
    assert result_none["status"] == "error"
    assert result_none["error_message"] == "Unknown error"
    
    # Test with empty string
    result_empty = tool_error("")
    assert result_empty["status"] == "error"
    assert result_empty["error_message"] == ""
    
    # Test with non-string that can be converted
    result_int = tool_error(404)
    assert result_int["status"] == "error"
    assert result_int["error_message"] == "404"
    
    print("✓ tool_error creates proper error results and handles edge cases")


def test_is_success():
    """Test that is_success correctly identifies success results."""
    success_result = tool_success("data")
    error_result = tool_error("error")
    
    assert is_success(success_result) is True
    assert is_success(error_result) is False
    
    # Test with manually created results
    manual_success = {"status": "success", "result": "test"}
    manual_error = {"status": "error", "error_message": "test"}
    
    assert is_success(manual_success) is True
    assert is_success(manual_error) is False
    
    print("✓ is_success correctly identifies success results")


def test_is_error():
    """Test that is_error correctly identifies error results."""
    success_result = tool_success("data")
    error_result = tool_error("error")
    
    assert is_error(success_result) is False
    assert is_error(error_result) is True
    
    # Test with manually created results
    manual_success = {"status": "success", "result": "test"}
    manual_error = {"status": "error", "error_message": "test"}
    
    assert is_error(manual_success) is False
    assert is_error(manual_error) is True
    
    print("✓ is_error correctly identifies error results")


def test_map_result():
    """Test that map_result applies function to success results only."""
    # Test with success result
    success_result = tool_success(10)
    mapped_success = map_result(success_result, lambda x: x * 2)
    
    assert is_success(mapped_success)
    assert mapped_success["result"] == 20
    
    # Test with error result (should pass through unchanged)
    error_result = tool_error("failed")
    mapped_error = map_result(error_result, lambda x: x * 2)
    
    assert is_error(mapped_error)
    assert mapped_error["error_message"] == "failed"
    assert mapped_error is error_result  # Should be the same object
    
    # Test with more complex transformation
    success_list = tool_success([1, 2, 3])
    mapped_list = map_result(success_list, lambda x: [i * 2 for i in x])
    
    assert is_success(mapped_list)
    assert mapped_list["result"] == [2, 4, 6]
    
    print("✓ map_result correctly applies function to success results only")


def test_map_error():
    """Test that map_error applies function to error results only."""
    # Test with error result
    error_result = tool_error("original error")
    mapped_error = map_error(error_result, lambda msg: f"Wrapped: {msg}")
    
    assert is_error(mapped_error)
    assert mapped_error["error_message"] == "Wrapped: original error"
    
    # Test with success result (should pass through unchanged)
    success_result = tool_success("data")
    mapped_success = map_error(success_result, lambda msg: f"Wrapped: {msg}")
    
    assert is_success(mapped_success)
    assert mapped_success["result"] == "data"
    assert mapped_success is success_result  # Should be the same object
    
    # Test with transformation that changes error message format
    error_result2 = tool_error("404")
    mapped_error2 = map_error(error_result2, lambda msg: f"HTTP Error {msg}: Not Found")
    
    assert is_error(mapped_error2)
    assert mapped_error2["error_message"] == "HTTP Error 404: Not Found"
    
    print("✓ map_error correctly applies function to error results only")


def test_get_or_else():
    """Test that get_or_else returns result on success, default on error."""
    # Test with success result
    success_result = tool_success("success_value")
    value = get_or_else(success_result, "default_value")
    assert value == "success_value"
    
    # Test with error result
    error_result = tool_error("something failed")
    value = get_or_else(error_result, "default_value")
    assert value == "default_value"
    
    # Test with None as default
    value_none = get_or_else(error_result, None)
    assert value_none is None
    
    # Test with complex default value
    complex_default = {"fallback": True, "data": [1, 2, 3]}
    value_complex = get_or_else(error_result, complex_default)
    assert value_complex == complex_default
    
    print("✓ get_or_else returns correct values for success and error cases")


def test_get_or_raise():
    """Test that get_or_raise returns result on success, raises on error."""
    # Test with success result
    success_result = tool_success("success_value")
    value = get_or_raise(success_result)
    assert value == "success_value"
    
    # Test with success result containing None
    success_none = tool_success(None)
    value_none = get_or_raise(success_none)
    assert value_none is None
    
    # Test with success result containing complex data
    complex_data = {"nested": {"value": 42}}
    success_complex = tool_success(complex_data)
    value_complex = get_or_raise(success_complex)
    assert value_complex == complex_data
    
    # Test with error result (should raise)
    error_result = tool_error("something failed")
    try:
        get_or_raise(error_result)
        assert False, "Expected exception to be raised"
    except Exception as e:
        assert str(e) == "something failed"
    
    # Test with different error message
    error_result2 = tool_error("custom error message")
    try:
        get_or_raise(error_result2)
        assert False, "Expected exception to be raised"
    except Exception as e:
        assert str(e) == "custom error message"
    
    print("✓ get_or_raise returns values on success and raises on error")


def test_chaining_operations():
    """Test chaining multiple operations together."""
    # Success chain
    result = tool_success(5)
    result = map_result(result, lambda x: x * 2)  # 10
    result = map_result(result, lambda x: x + 3)  # 13
    final_value = get_or_else(result, 0)
    assert final_value == 13
    
    # Error chain (should short-circuit)
    result = tool_error("initial error")
    result = map_result(result, lambda x: x * 2)  # Should not apply
    result = map_result(result, lambda x: x + 3)  # Should not apply
    final_value = get_or_else(result, 0)
    assert final_value == 0
    assert is_error(result)
    assert result["error_message"] == "initial error"
    
    # Mixed chain with error transformation
    result = tool_error("404")
    result = map_error(result, lambda msg: f"HTTP {msg}")
    result = map_result(result, lambda x: x * 2)  # Should not apply
    final_value = get_or_else(result, "fallback")
    assert final_value == "fallback"
    assert result["error_message"] == "HTTP 404"
    
    print("✓ Operations chain correctly with proper short-circuiting")


def test_type_guards():
    """Test that type guards work correctly for type checking."""
    success_result = tool_success("test")
    error_result = tool_error("test error")
    
    # Test that type guards narrow types correctly
    if is_success(success_result):
        # In a real type checker, success_result would be typed as ResultSuccess here
        assert "result" in success_result
        assert success_result["result"] == "test"
    
    if is_error(error_result):
        # In a real type checker, error_result would be typed as ResultError here
        assert "error_message" in error_result
        assert error_result["error_message"] == "test error"
    
    print("✓ Type guards work correctly for type narrowing")


def test_edge_cases():
    """Test various edge cases and boundary conditions."""
    # Test with empty string success
    empty_success = tool_success("")
    assert is_success(empty_success)
    assert empty_success["result"] == ""
    
    # Test with zero
    zero_success = tool_success(0)
    assert is_success(zero_success)
    assert zero_success["result"] == 0
    
    # Test with False
    false_success = tool_success(False)
    assert is_success(false_success)
    assert false_success["result"] is False
    
    # Test map_result with function that returns None
    none_mapped = map_result(tool_success("input"), lambda x: None)
    assert is_success(none_mapped)
    assert none_mapped["result"] is None
    
    # Test map_error with function that returns empty string
    empty_mapped = map_error(tool_error("error"), lambda x: "")
    assert is_error(empty_mapped)
    assert empty_mapped["error_message"] == ""
    
    print("✓ Edge cases handled correctly")


if __name__ == "__main__":
    print("Testing tool_result module...")
    print("=" * 50)
    
    test_tool_success()
    test_tool_error()
    test_is_success()
    test_is_error()
    test_map_result()
    test_map_error()
    test_get_or_else()
    test_get_or_raise()
    test_chaining_operations()
    test_type_guards()
    test_edge_cases()
    
    print("=" * 50)
    print("🎉 All tool_result tests passed!")
    print("\nThe tool_result module is working correctly:")
    print("- Success and error result creation")
    print("- Type guards for success/error detection")
    print("- Functional operations (map_result, map_error)")
    print("- Value extraction (get_or_else, get_or_raise)")
    print("- Proper chaining and short-circuiting behavior")
    print("- Edge cases and boundary conditions")

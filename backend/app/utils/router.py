import inspect
from functools import wraps
from typing import Callable

from fastapi import APIRouter, HTTPException

from app.config.logger import log


class SafeAPIRouter(APIRouter):
    """Custom APIRouter to raise 500 with an appropriate error message when an unexpected error occurs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_message = "Something went wrong. Kindly retry later"

    def _wrap_with_exception_handler(self, func: Callable) -> Callable:
        """Wrap a route handler with automatic exception handling"""
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except HTTPException:
                    # Re-raise HTTPExceptions as they are intentional
                    raise
                except:
                    log.exception("The unexpected occurred")
                    raise self.http_500_exc_internal_server_error()

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except HTTPException:
                    # Re-raise HTTPExceptions as they are intentional
                    raise
                except:
                    log.exception("The unexpected occurred")
                    raise self.http_500_exc_internal_server_error()

            return sync_wrapper

    def http_500_exc_internal_server_error(self):
        """Override this method to customize your 500 error response"""
        raise HTTPException(status_code=500, detail=self.error_message)

    def post(self, path: str, **kwargs):
        """Override post method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).post(path, **kwargs)(wrapped_func)

        return decorator

    def get(self, path: str, **kwargs):
        """Override get method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).get(path, **kwargs)(wrapped_func)

        return decorator

    def put(self, path: str, **kwargs):
        """Override put method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).put(path, **kwargs)(wrapped_func)

        return decorator

    def patch(self, path: str, **kwargs):
        """Override patch method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).patch(path, **kwargs)(wrapped_func)

        return decorator

    def delete(self, path: str, **kwargs):
        """Override delete method to add exception handling"""

        def decorator(func: Callable) -> Callable:
            wrapped_func = self._wrap_with_exception_handler(func)
            return super(SafeAPIRouter, self).delete(path, **kwargs)(wrapped_func)

        return decorator

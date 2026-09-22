"""
NepaliCode Async Library
Python asyncio-like async/await support
"""

import asyncio
from typing import Callable, Any, List, Optional
from functools import wraps


def run(coro):
    """Run async coroutine"""
    return asyncio.run(coro)


def sleep(seconds: float):
    """Async sleep"""
    return asyncio.sleep(seconds)


def gather(*coros):
    """Run multiple coroutines concurrently"""
    return asyncio.gather(*coros)


def create_task(coro):
    """Create async task"""
    return asyncio.create_task(coro)


def wrap(func: Callable) -> Callable:
    """Wrap synchronous function to run in thread pool"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper


class AsyncContext:
    """Async context manager for common operations"""
    
    @staticmethod
    async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
        """Run function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    @staticmethod
    async def run_in_process(func: Callable, *args, **kwargs) -> Any:
        """Run function in process pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)


# For interpreter context
_module_dict = {
    'run': run,
    'sleep': sleep,
    'gather': gather,
    'create_task': create_task,
    'wrap': wrap,
    'AsyncContext': AsyncContext,
}
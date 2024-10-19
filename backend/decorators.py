import functools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_route_call(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Route called: {func.__name__}")
        return await func(*args, **kwargs)
    return wrapper
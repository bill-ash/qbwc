import logging
from datetime import datetime, timezone
from functools import wraps

import xml.sax.saxutils as saxutils

logger = logging.getLogger(__name__)

def parse_time_stamp(x):
    """Convert stringstamps to datestamps"""
    try:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        logger.error("Error parsing time stamp")
        return datetime.now(timezone.utc)

def string_escape_decorator(func):
    """
    Escape special characters included in strings that could be passed to QuickBooks 
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for var in vars(self): 
            if isinstance(getattr(self, var), str):
                setattr(self, var, saxutils.escape(getattr(self, var)))
        return func(self, *args, **kwargs)
    return wrapper

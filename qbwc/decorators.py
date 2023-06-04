from functools import wraps
import xml.sax.saxutils as saxutils


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

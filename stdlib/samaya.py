"""
NepaliLang Standard Library - Samaya (Time)
Provides time and date functions.
"""

import time

def now():
    """Get current time."""
    return time.time()

def today():
    """Get today's date."""
    import datetime
    return datetime.date.today()

def sleep(seconds):
    """Sleep for given seconds."""
    time.sleep(seconds)

def format(timestamp, format_string):
    """Format timestamp."""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime(format_string)
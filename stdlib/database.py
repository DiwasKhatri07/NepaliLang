"""
NepaliCode Database Library
Simple SQLite API for database operations
"""

import sqlite3
from typing import List, Any, Optional, Union, Tuple
from contextlib import contextmanager


class Database:
    """SQLite database connection"""
    
    def __init__(self, filename: str = ":memory:"):
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
    
    def execute(self, sql: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """Execute SQL statement"""
        if params:
            return self.connection.execute(sql, params)
        return self.connection.execute(sql)
    
    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries"""
        cursor = self.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetchone(self, sql: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def commit(self) -> None:
        """Commit transaction"""
        self.connection.commit()
    
    def rollback(self) -> None:
        """Rollback transaction"""
        self.connection.rollback()
    
    def close(self) -> None:
        """Close database connection"""
        self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise


def connect(filename: str = ":memory:") -> Database:
    """Create database connection"""
    return Database(filename)


# For interpreter context
_module_dict = {
    'connect': connect,
    'Database': Database,
    'execute': lambda *args, **kwargs: None,  # Placeholder
    'query': lambda *args, **kwargs: None,  # Placeholder
    'fetchone': lambda *args, **kwargs: None,  # Placeholder
    'commit': lambda: None,  # Placeholder
    'close': lambda: None,  # Placeholder
}
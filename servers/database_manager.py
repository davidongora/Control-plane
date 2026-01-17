"""Database query execution manager with security controls."""
import re
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
import pymysql
import sqlite3
from contextlib import contextmanager


def validate_identifier(identifier: str) -> bool:
    """Validate SQL identifier (table name, column name) to prevent injection."""
    # Allow only alphanumeric characters, underscores, and start with letter/underscore
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, identifier))


class DatabaseQueryManager:
    """Manager for executing database queries with security controls."""
    
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE',
        'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'CALL', 'SHUTDOWN'
    ]
    
    MAX_QUERY_TIME = 30  # seconds
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    def __init__(self, db_type: str, host: str, port: int, database: str, 
                 username: str, password: str):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
    
    @contextmanager
    def get_connection(self):
        """Get database connection based on type."""
        conn = None
        try:
            if self.db_type == 'postgresql':
                conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    connect_timeout=10
                )
            elif self.db_type == 'mysql':
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    connect_timeout=10,
                    charset='utf8mb4'
                )
            elif self.db_type == 'sqlite':
                conn = sqlite3.connect(self.database, timeout=10)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            yield conn
        finally:
            if conn:
                conn.close()
    
    def is_query_safe(self, query: str, allow_write: bool = False) -> Tuple[bool, str]:
        """Check if query is safe to execute."""
        query_upper = query.upper().strip()
        
        # Remove comments
        query_no_comments = re.sub(r'--.*$', '', query_upper, flags=re.MULTILINE)
        query_no_comments = re.sub(r'/\*.*?\*/', '', query_no_comments, flags=re.DOTALL)
        
        # Check for dangerous operations
        if not allow_write:
            for keyword in self.DANGEROUS_KEYWORDS:
                if re.search(r'\b' + keyword + r'\b', query_no_comments):
                    return False, f"Query contains prohibited keyword: {keyword}"
        
        # Check for multiple statements (SQL injection protection)
        if ';' in query.strip().rstrip(';'):
            return False, "Multiple statements not allowed"
        
        return True, "Query is safe"
    
    def execute_query(self, query: str, allow_write: bool = False, 
                     page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        """Execute a database query with pagination."""
        # Validate query safety
        is_safe, message = self.is_query_safe(query, allow_write)
        if not is_safe:
            return {
                'success': False,
                'error': message,
                'columns': [],
                'rows': [],
                'total_rows': 0,
                'page': page,
                'page_size': page_size
            }
        
        # Limit page size
        page_size = min(page_size, self.MAX_PAGE_SIZE)
        offset = (page - 1) * page_size
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Set query timeout
                if self.db_type == 'postgresql':
                    cursor.execute(f"SET statement_timeout = {self.MAX_QUERY_TIME * 1000}")
                elif self.db_type == 'mysql':
                    cursor.execute(f"SET SESSION max_execution_time = {self.MAX_QUERY_TIME * 1000}")
                
                # For SELECT queries, add pagination
                query_upper = query.upper().strip()
                if query_upper.startswith('SELECT'):
                    # Count total rows (for SELECT queries)
                    count_query = f"SELECT COUNT(*) FROM ({query}) AS count_table"
                    try:
                        cursor.execute(count_query)
                        total_rows = cursor.fetchone()[0]
                    except:
                        # If count fails, execute original query without count
                        total_rows = -1
                    
                    # Add pagination to query
                    paginated_query = f"{query} LIMIT {page_size} OFFSET {offset}"
                    cursor.execute(paginated_query)
                else:
                    # For non-SELECT queries (if allowed)
                    cursor.execute(query)
                    total_rows = cursor.rowcount
                
                # Fetch results
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    # Convert rows to list of dicts
                    rows_data = []
                    for row in rows:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            value = row[i]
                            # Convert special types to strings
                            if value is not None and not isinstance(value, (str, int, float, bool)):
                                value = str(value)
                            row_dict[col] = value
                        rows_data.append(row_dict)
                else:
                    columns = []
                    rows_data = []
                
                # Commit for write operations
                if allow_write and not query_upper.startswith('SELECT'):
                    conn.commit()
                
                return {
                    'success': True,
                    'columns': columns,
                    'rows': rows_data,
                    'total_rows': total_rows if total_rows >= 0 else len(rows_data),
                    'page': page,
                    'page_size': page_size,
                    'affected_rows': cursor.rowcount if not query_upper.startswith('SELECT') else 0
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'columns': [],
                'rows': [],
                'total_rows': 0,
                'page': page,
                'page_size': page_size
            }
    
    def list_tables(self) -> Dict[str, Any]:
        """List all tables in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        ORDER BY table_name
                    """)
                elif self.db_type == 'mysql':
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        ORDER BY table_name
                    """, (self.database,))
                elif self.db_type == 'sqlite':
                    cursor.execute("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table' 
                        ORDER BY name
                    """)
                
                tables = [row[0] for row in cursor.fetchall()]
                return {
                    'success': True,
                    'tables': tables
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tables': []
            }
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        # Validate table name to prevent SQL injection
        if not validate_identifier(table_name):
            return {
                'success': False,
                'error': 'Invalid table name. Table names must start with a letter or underscore and contain only alphanumeric characters and underscores.',
                'columns': []
            }
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """, (table_name,))
                elif self.db_type == 'mysql':
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = %s
                        ORDER BY ordinal_position
                    """, (table_name, self.database))
                elif self.db_type == 'sqlite':
                    # For SQLite, use parameterized query with validated identifier
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    # SQLite returns: cid, name, type, notnull, dflt_value, pk
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            'column_name': row[1],
                            'data_type': row[2],
                            'is_nullable': 'YES' if row[3] == 0 else 'NO',
                            'column_default': row[4]
                        })
                    return {
                        'success': True,
                        'columns': columns
                    }
                
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        'column_name': row[0],
                        'data_type': row[1],
                        'is_nullable': row[2],
                        'column_default': row[3]
                    })
                
                return {
                    'success': True,
                    'columns': columns
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'columns': []
            }
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

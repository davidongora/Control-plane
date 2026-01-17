# Database Client Feature

## Overview
The Database Client feature provides a web-based SQL client interface for executing queries against databases on managed servers.

## Backend Implementation

### Model: DatabaseClient
Located in `servers/models.py`, the DatabaseClient model stores database connection information:
- **server**: ForeignKey to Server model
- **name**: Connection display name
- **db_type**: Database type (postgresql, mysql, sqlite)
- **database_name**: Name of the database
- **host**: Database host (defaults to server IP)
- **port**: Database port (defaults based on db_type)
- **username**: Database username
- **password_encrypted**: Encrypted password using Django SECRET_KEY

### API Endpoints
All endpoints are prefixed with `/api/database-clients/`

1. **GET /api/database-clients/** - List all database connections
   - Query param: `server_id` (optional) - Filter by server

2. **POST /api/database-clients/** - Create a new database connection
   - Body: `{ server, name, db_type, database_name, host, port, username, password }`

3. **GET /api/database-clients/{id}/** - Get a specific connection

4. **PUT /api/database-clients/{id}/** - Update a connection

5. **DELETE /api/database-clients/{id}/** - Delete a connection

6. **POST /api/database-clients/{id}/test_connection/** - Test connection
   - Returns: `{ success, message }`

7. **GET /api/database-clients/{id}/tables/** - List all tables
   - Returns: `{ success, tables: [...] }`

8. **GET /api/database-clients/{id}/table_schema/?table_name={name}** - Get table schema
   - Returns: `{ success, columns: [{column_name, data_type, is_nullable, column_default}] }`

9. **POST /api/database-clients/{id}/query/** - Execute a query
   - Body: `{ query, allow_write, page, page_size }`
   - Returns: `{ success, columns, rows, total_rows, page, page_size, error }`

10. **GET /api/database-clients/{id}/records/?table_name={name}&page={n}&page_size={n}** - Get table records
    - Returns paginated records from a table

### Security Features

#### Query Validation (`database_manager.py`)
- **SQL Injection Protection**: Prevents multiple statements, validates query structure
- **Read-only by Default**: Only SELECT queries allowed unless `allow_write=true`
- **Dangerous Keywords Blocked**: DROP, DELETE, TRUNCATE, ALTER, CREATE, etc. (when write disabled)
- **Query Timeout**: Maximum 30 seconds execution time
- **Pagination**: Default 100 rows, maximum 1000 rows per page

#### Password Encryption
- Passwords encrypted using `cryptography.fernet.Fernet`
- Encryption key derived from Django SECRET_KEY via SHA-256
- Stored in `password_encrypted` field, never returned in API responses

## Frontend Implementation

### Component: DatabaseClientComponent
Located in `control-plane-frontend/src/app/components/database-client/`

### Features

1. **Connection Management**
   - Add new database connections
   - View all connections
   - Test connections
   - Delete connections

2. **Query Editor**
   - Monospace textarea for SQL queries
   - Execute button
   - Option to allow write operations (INSERT/UPDATE/DELETE)

3. **Table Browser**
   - List all tables in selected database
   - Click table to generate SELECT query

4. **Query Results**
   - Tabular display of results
   - Pagination controls
   - Column headers from query
   - NULL value handling
   - Row count display

5. **Error Handling**
   - Display query errors
   - Connection failure messages
   - Input validation

### Navigation
- Added to main navbar as "Database Client"
- Route: `/database-client`
- Protected by auth guard

## Usage

### Setting Up a Database Connection

1. Navigate to "Database Client" in the navbar
2. Click "+ Add Database Connection"
3. Fill in the form:
   - Select a server
   - Choose database type (PostgreSQL, MySQL, or SQLite)
   - Enter database name, username, and password
   - Optionally specify host and port (defaults provided)
4. Click "Add Connection"

### Executing Queries

1. Select a database connection from the list
2. (Optional) Click "Show Tables" to browse available tables
3. Enter your SQL query in the editor
4. Click "Execute Query"
5. View results in the table below
6. Use pagination controls for large result sets

### Security Notes

- Only SELECT queries are allowed by default
- Check "Allow Write Operations" to enable INSERT/UPDATE/DELETE
- Queries are validated server-side to prevent SQL injection
- Query execution is time-limited to 30 seconds
- Passwords are encrypted at rest

## Database Support

### PostgreSQL
- Default port: 5432
- Requires `psycopg2-binary` package
- Full support for all query types

### MySQL
- Default port: 3306
- Requires `PyMySQL` package
- Full support for all query types

### SQLite
- No port required
- Uses Python's built-in `sqlite3` module
- File path should be in `database_name` field

## Dependencies

### Backend
- `psycopg2-binary>=2.9.9` (PostgreSQL)
- `PyMySQL>=1.1.0` (MySQL)
- `cryptography>=41.0.0` (Password encryption)
- `sqlite3` (built-in, SQLite)

### Frontend
- Angular forms module
- Existing API service

## Database Migration

Run migrations to create the DatabaseClient table:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Future Enhancements

Potential improvements:
1. Query history and saved queries
2. Export results to CSV/JSON
3. Visual query builder
4. Database schema viewer with relationships
5. Query performance metrics
6. Multi-query execution with transaction support
7. Syntax highlighting in query editor
8. Auto-completion for table/column names

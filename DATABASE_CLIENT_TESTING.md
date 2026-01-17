# Database Client Implementation - Testing Guide

## Overview
This guide provides instructions for testing the Database Client feature after environment setup.

## Prerequisites

### 1. Backend Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run migrations to create DatabaseClient table
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd control-plane-frontend

# Install dependencies (if not already done)
npm install

# Start the Angular development server
npm start
```

### 3. Database Setup (for testing)
You'll need at least one test database to connect to. Options:

**PostgreSQL:**
```bash
# Create a test database
sudo -u postgres createdb testdb
sudo -u postgres psql -c "CREATE USER testuser WITH PASSWORD 'testpass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;"
```

**MySQL:**
```bash
# Create a test database
mysql -u root -p
CREATE DATABASE testdb;
CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpass';
GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'localhost';
FLUSH PRIVILEGES;
```

**SQLite:**
```bash
# Create a test database file
sqlite3 /tmp/testdb.sqlite "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);"
```

## Testing Steps

### 1. Test Backend API Endpoints

#### Create a Database Client
```bash
curl -X POST http://localhost:8000/api/database-clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "server": 1,
    "name": "Test PostgreSQL",
    "db_type": "postgresql",
    "database_name": "testdb",
    "username": "testuser",
    "password": "testpass"
  }'
```

#### List Database Clients
```bash
curl http://localhost:8000/api/database-clients/
```

#### Test Connection
```bash
curl -X POST http://localhost:8000/api/database-clients/1/test_connection/
```

#### List Tables
```bash
curl http://localhost:8000/api/database-clients/1/tables/
```

#### Execute Query
```bash
curl -X POST http://localhost:8000/api/database-clients/1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT 1 as test_column",
    "allow_write": false,
    "page": 1,
    "page_size": 100
  }'
```

### 2. Test Frontend Interface

1. **Navigate to Database Client**
   - Open http://localhost:4200/database-client
   - Verify the page loads without errors

2. **Add a Database Connection**
   - Click "+ Add Database Connection"
   - Fill in the form with test database credentials
   - Click "Add Connection"
   - Verify success message appears
   - Verify connection appears in the list

3. **Test Connection**
   - Click "Test" button on a connection
   - Verify connection test result (success or failure with error message)

4. **Select Connection and Browse Tables**
   - Click "Select" on a connection
   - Click "Show Tables" button
   - Verify tables are listed (if any exist)
   - Click on a table name
   - Verify query editor populates with "SELECT * FROM table_name"

5. **Execute Queries**
   - Enter a simple query: `SELECT 1 as test_column, 'test' as test_text`
   - Click "Execute Query"
   - Verify results appear in table
   - Verify column headers match query

6. **Test Pagination**
   - Execute a query that returns more than 100 rows
   - Verify pagination controls appear
   - Click "Next" and "Previous" buttons
   - Verify page numbers update correctly

7. **Test Query Validation**
   - Try executing: `DROP TABLE test;`
   - Verify error message about prohibited keyword
   - Try executing: `SELECT * FROM test; DELETE FROM test;`
   - Verify error message about multiple statements

8. **Test Write Operations**
   - Check "Allow Write Operations" checkbox
   - Execute: `CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);`
   - Verify success (if database supports it)
   - Execute: `INSERT INTO test_table (name) VALUES ('test');`
   - Verify affected rows count

9. **Delete Connection**
   - Click "Delete" on a connection
   - Confirm deletion
   - Verify connection is removed from list

### 3. Security Testing

#### SQL Injection Prevention
```bash
# Test 1: Multiple statements
curl -X POST http://localhost:8000/api/database-clients/1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1; DROP TABLE test;"}'
# Expected: Error about multiple statements

# Test 2: Dangerous keywords (without allow_write)
curl -X POST http://localhost:8000/api/database-clients/1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "DROP TABLE test;"}'
# Expected: Error about prohibited keyword

# Test 3: Invalid table name
curl http://localhost:8000/api/database-clients/1/records/?table_name="test%27%20OR%201=1--"
# Expected: Error about invalid table name
```

#### Password Encryption
```bash
# Check that password is encrypted in database
python manage.py shell
>>> from servers.models import DatabaseClient
>>> db = DatabaseClient.objects.first()
>>> print(db.password_encrypted)  # Should be encrypted gibberish
>>> print(db.get_password())  # Should be decrypted password
```

### 4. Error Handling Testing

1. **Invalid Credentials**
   - Create connection with wrong password
   - Try to execute query
   - Verify proper error message

2. **Invalid Query Syntax**
   - Execute: `SELCT * FROM test;` (typo in SELECT)
   - Verify SQL syntax error is displayed

3. **Non-existent Table**
   - Execute: `SELECT * FROM nonexistent_table;`
   - Verify error about table not existing

4. **Query Timeout**
   - Execute a long-running query (if possible)
   - Verify timeout error after 30 seconds

5. **Invalid Pagination**
   - Try page=-1, page=0, page_size=-1, page_size=10000
   - Verify values are corrected to valid ranges

## Known Issues and Limitations

1. **Authentication**: Demo version has authentication disabled for ease of testing. For production, update `permission_classes` in views.

2. **SQLite**: File path goes in `database_name` field. The `host` and `port` fields are not used.

3. **Connection Pooling**: Not implemented. Each query creates a new connection.

4. **Query History**: Not saved. Each query is independent.

5. **Large Result Sets**: First page fetch requires fetching all results for counting. May be slow for very large datasets.

## Production Checklist

Before deploying to production:

- [ ] Enable authentication (`permission_classes = [IsAuthenticated]`)
- [ ] Use HTTPS for all connections
- [ ] Set strong SECRET_KEY in Django settings
- [ ] Use PostgreSQL instead of SQLite for Control Plane database
- [ ] Enable Django's security middleware
- [ ] Set up rate limiting for API endpoints
- [ ] Configure CORS properly for production frontend URL
- [ ] Set appropriate query timeout values
- [ ] Add audit logging for database operations
- [ ] Regularly rotate database credentials
- [ ] Monitor for suspicious query patterns

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
Solution: Activate virtual environment: `source venv/bin/activate`

### "OperationalError: no such table: servers_databaseclient"
Solution: Run migrations: `python manage.py migrate`

### "Connection refused" errors
Solution: Check database is running and credentials are correct

### Frontend shows "Cannot GET /database-client"
Solution: Make sure Angular dev server is running: `npm start`

### Query execution hangs
Solution: Query might be taking too long. Check database logs and consider adding indexes.

## Performance Tips

1. **Add Indexes**: For tables frequently queried, add appropriate indexes
2. **Limit Result Sets**: Use WHERE clauses to reduce data fetched
3. **Use Pagination**: Don't fetch thousands of rows at once
4. **Connection Reuse**: Consider adding connection pooling for high-traffic scenarios
5. **Query Optimization**: Use EXPLAIN to analyze query performance

## Support

For issues or questions:
- Review DATABASE_CLIENT.md for feature documentation
- Check Django error logs: console output or log files
- Check browser console for frontend errors
- Verify database server logs for connection issues

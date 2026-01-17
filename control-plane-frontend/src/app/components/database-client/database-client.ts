import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api, DatabaseClient, QueryResult, Server } from '../../services/api';

@Component({
  selector: 'app-database-client',
  imports: [CommonModule, FormsModule],
  templateUrl: './database-client.html',
  styleUrl: './database-client.css',
})
export class DatabaseClientComponent implements OnInit {
  servers: Server[] = [];
  databaseClients: DatabaseClient[] = [];
  selectedClient: DatabaseClient | null = null;
  
  // Query execution
  query: string = '';
  allowWrite: boolean = false;
  queryResult: QueryResult | null = null;
  executing: boolean = false;
  
  // Table browser
  tables: string[] = [];
  selectedTable: string | null = null;
  loadingTables: boolean = false;
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 100;
  
  // UI state
  showAddForm: boolean = false;
  showTableBrowser: boolean = false;
  loading: boolean = true;
  errorMessage: string = '';
  successMessage: string = '';
  
  // New database client form
  newClient: Partial<DatabaseClient> = {
    server: 0,
    name: '',
    db_type: 'postgresql',
    database_name: '',
    host: '',
    port: undefined,
    username: '',
    password: ''
  };

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadServers();
    this.loadDatabaseClients();
  }

  loadServers() {
    this.api.getServers().subscribe({
      next: (response) => {
        this.servers = response.results || response;
      },
      error: (err) => {
        console.error('Error loading servers:', err);
      }
    });
  }

  loadDatabaseClients() {
    this.loading = true;
    this.api.getDatabaseClients().subscribe({
      next: (response) => {
        this.databaseClients = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading database clients:', err);
        this.errorMessage = 'Failed to load database clients';
        this.loading = false;
      }
    });
  }

  selectClient(client: DatabaseClient) {
    this.selectedClient = client;
    this.queryResult = null;
    this.query = '';
    this.errorMessage = '';
    this.successMessage = '';
    this.loadTables();
  }

  loadTables() {
    if (!this.selectedClient?.id) return;
    
    this.loadingTables = true;
    this.api.getDatabaseTables(this.selectedClient.id).subscribe({
      next: (response) => {
        this.tables = response.tables || [];
        this.loadingTables = false;
      },
      error: (err) => {
        console.error('Error loading tables:', err);
        this.errorMessage = 'Failed to load tables';
        this.loadingTables = false;
      }
    });
  }

  selectTable(tableName: string) {
    this.selectedTable = tableName;
    this.query = `SELECT * FROM ${tableName}`;
  }

  executeQuery() {
    if (!this.selectedClient?.id || !this.query.trim()) {
      this.errorMessage = 'Please select a database and enter a query';
      return;
    }

    this.executing = true;
    this.errorMessage = '';
    this.queryResult = null;

    this.api.executeDatabaseQuery(
      this.selectedClient.id,
      this.query,
      this.allowWrite,
      this.currentPage,
      this.pageSize
    ).subscribe({
      next: (result) => {
        this.queryResult = result;
        if (!result.success) {
          this.errorMessage = result.error || 'Query execution failed';
        } else {
          this.successMessage = `Query executed successfully. ${result.total_rows} rows returned.`;
          setTimeout(() => this.successMessage = '', 3000);
        }
        this.executing = false;
      },
      error: (err) => {
        console.error('Error executing query:', err);
        this.errorMessage = err.error?.error || 'Failed to execute query';
        this.executing = false;
      }
    });
  }

  loadPage(page: number) {
    if (!this.selectedClient?.id || !this.query.trim()) return;
    
    this.currentPage = page;
    this.executeQuery();
  }

  nextPage() {
    if (this.queryResult && this.currentPage * this.pageSize < this.queryResult.total_rows) {
      this.loadPage(this.currentPage + 1);
    }
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.loadPage(this.currentPage - 1);
    }
  }

  getTotalPages(): number {
    if (!this.queryResult || this.queryResult.total_rows === 0) return 0;
    return Math.ceil(this.queryResult.total_rows / this.pageSize);
  }

  toggleTableBrowser() {
    this.showTableBrowser = !this.showTableBrowser;
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (this.showAddForm) {
      this.resetNewClientForm();
    }
  }

  resetNewClientForm() {
    this.newClient = {
      server: this.servers.length > 0 ? this.servers[0].id : 0,
      name: '',
      db_type: 'postgresql',
      database_name: '',
      host: '',
      port: undefined,
      username: '',
      password: ''
    };
    this.errorMessage = '';
    this.successMessage = '';
  }

  addDatabaseClient() {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.newClient.server || !this.newClient.name || !this.newClient.database_name || !this.newClient.username) {
      this.errorMessage = 'Please fill in all required fields';
      return;
    }

    this.api.createDatabaseClient(this.newClient as DatabaseClient).subscribe({
      next: (client) => {
        this.successMessage = 'Database client added successfully!';
        this.loadDatabaseClients();
        setTimeout(() => {
          this.showAddForm = false;
          this.successMessage = '';
        }, 2000);
      },
      error: (err) => {
        console.error('Error creating database client:', err);
        this.errorMessage = err.error?.detail || 'Failed to create database client';
      }
    });
  }

  testConnection(client: DatabaseClient) {
    if (!client.id) return;

    this.api.testDatabaseConnection(client.id).subscribe({
      next: (response) => {
        alert(response.message);
      },
      error: (err) => {
        alert('Connection test failed: ' + (err.error?.message || 'Unknown error'));
      }
    });
  }

  deleteDatabaseClient(client: DatabaseClient) {
    if (!client.id || !confirm(`Are you sure you want to delete ${client.name}?`)) return;

    this.api.deleteDatabaseClient(client.id).subscribe({
      next: () => {
        this.databaseClients = this.databaseClients.filter(c => c.id !== client.id);
        if (this.selectedClient?.id === client.id) {
          this.selectedClient = null;
          this.queryResult = null;
        }
      },
      error: (err) => {
        console.error('Error deleting database client:', err);
        alert('Failed to delete database client');
      }
    });
  }

  clearResults() {
    this.queryResult = null;
    this.errorMessage = '';
    this.successMessage = '';
  }
}

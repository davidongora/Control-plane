import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api, Server } from '../../services/api';

@Component({
  selector: 'app-servers',
  imports: [CommonModule, FormsModule],
  templateUrl: './servers.html',
  styleUrl: './servers.css',
})
export class Servers implements OnInit {
  servers: Server[] = [];
  loading = true;
  showAddForm = false;
  newServer: Server = this.getEmptyServer();

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadServers();
  }

  loadServers() {
    this.loading = true;
    this.api.getServers().subscribe({
      next: (response) => {
        this.servers = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading servers:', err);
        this.loading = false;
      }
    });
  }

  getEmptyServer(): Server {
    return {
      name: '',
      hostname: '',
      ip_address: '',
      port: 22,
      username: '',
      description: '',
      is_active: true
    };
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (this.showAddForm) {
      this.newServer = this.getEmptyServer();
    }
  }

  addServer() {
    this.api.createServer(this.newServer).subscribe({
      next: (server) => {
        this.servers.push(server);
        this.showAddForm = false;
        this.newServer = this.getEmptyServer();
      },
      error: (err) => {
        console.error('Error creating server:', err);
        alert('Failed to create server');
      }
    });
  }

  testConnection(server: Server) {
    if (!server.id) return;
    
    this.api.testConnection(server.id).subscribe({
      next: (response) => {
        alert(response.message);
      },
      error: (err) => {
        alert('Connection test failed');
        console.error('Error testing connection:', err);
      }
    });
  }

  deleteServer(server: Server) {
    if (!server.id || !confirm(`Are you sure you want to delete ${server.name}?`)) return;
    
    this.api.deleteServer(server.id).subscribe({
      next: () => {
        this.servers = this.servers.filter(s => s.id !== server.id);
      },
      error: (err) => {
        console.error('Error deleting server:', err);
        alert('Failed to delete server');
      }
    });
  }
}

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Api, Server, Service } from '../../services/api';
import { WebSocketService, WebSocketMessage } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit, OnDestroy {
  servers: Server[] = [];
  services: Service[] = [];
  loading = true;
  error: string | null = null;
  wsConnected = false;
  private wsSubscription?: Subscription;
  private wsStatusSubscription?: Subscription;

  constructor(
    private api: Api,
    private wsService: WebSocketService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
    this.connectWebSocket();
  }

  ngOnDestroy() {
    this.disconnectWebSocket();
  }

  get activeServersCount(): number {
    return this.servers.filter(s => s.is_active).length;
  }

  get runningServicesCount(): number {
    return this.services.filter(s => s.status === 'running').length;
  }

  loadDashboardData() {
    this.loading = true;
    this.error = null;

    this.api.getServers().subscribe({
      next: (response) => {
        this.servers = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load servers';
        this.loading = false;
        console.error('Error loading servers:', err);
      }
    });

    this.api.getServices().subscribe({
      next: (response) => {
        this.services = response.results || response;
      },
      error: (err) => {
        console.error('Error loading services:', err);
      }
    });
  }

  connectWebSocket() {
    // Connect to server status updates
    this.wsSubscription = this.wsService.connect('ws/servers/').subscribe({
      next: (message: WebSocketMessage) => {
        if (message.type === 'server_status' && message.data) {
          this.handleServerStatusUpdate(message.data);
        } else if (message.type === 'error') {
          console.error('WebSocket error:', message.message || message.error);
        }
      },
      error: (err) => {
        console.error('WebSocket subscription error:', err);
      }
    });

    // Monitor connection status
    this.wsStatusSubscription = this.wsService.getConnectionStatus('ws/servers/').subscribe({
      next: (connected) => {
        this.wsConnected = connected;
        if (!connected) {
          console.log('WebSocket disconnected, falling back to polling');
          this.startPolling();
        } else {
          console.log('WebSocket connected');
          this.stopPolling();
        }
      }
    });
  }

  disconnectWebSocket() {
    if (this.wsSubscription) {
      this.wsSubscription.unsubscribe();
    }
    if (this.wsStatusSubscription) {
      this.wsStatusSubscription.unsubscribe();
    }
    this.wsService.disconnect('ws/servers/');
    this.stopPolling();
  }

  handleServerStatusUpdate(serverData: any[]) {
    // Update server list with latest data
    serverData.forEach(updatedServer => {
      const index = this.servers.findIndex(s => s.id === updatedServer.id);
      if (index !== -1) {
        this.servers[index] = { ...this.servers[index], ...updatedServer };
      }
    });
  }

  // Fallback polling mechanism
  private pollingInterval?: any;

  startPolling() {
    if (this.pollingInterval) return;
    
    this.pollingInterval = setInterval(() => {
      this.loadDashboardData();
    }, 30000); // Poll every 30 seconds
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }
}

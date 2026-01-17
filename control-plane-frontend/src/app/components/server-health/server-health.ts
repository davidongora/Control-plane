import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Api, HealthMetrics, Server } from '../../services/api';
import { WebSocketService, WebSocketMessage } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-server-health',
  imports: [CommonModule],
  templateUrl: './server-health.html',
  styleUrl: './server-health.css',
})
export class ServerHealth implements OnInit, OnDestroy {
  serverId!: number;
  server?: Server;
  currentMetrics?: HealthMetrics;
  historicalMetrics: any[] = [];
  loading = true;
  wsConnected = false;
  private wsSubscription?: Subscription;
  private wsStatusSubscription?: Subscription;
  private pollingInterval?: any;

  constructor(
    private api: Api,
    private route: ActivatedRoute,
    private wsService: WebSocketService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.serverId = +params['id'];
      this.loadServerInfo();
      this.loadCurrentMetrics();
      this.loadHistoricalMetrics();
      this.connectWebSocket();
    });
  }

  ngOnDestroy() {
    this.disconnectWebSocket();
    this.stopPolling();
  }

  loadServerInfo() {
    this.api.getServer(this.serverId).subscribe({
      next: (server) => {
        this.server = server;
      },
      error: (err) => {
        console.error('Error loading server:', err);
      }
    });
  }

  loadCurrentMetrics() {
    this.api.getServerHealth(this.serverId).subscribe({
      next: (metrics) => {
        this.currentMetrics = metrics;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading metrics:', err);
        this.loading = false;
      }
    });
  }

  loadHistoricalMetrics() {
    this.api.getHealthMetrics(this.serverId).subscribe({
      next: (response) => {
        this.historicalMetrics = (response.results || response).slice(0, 10);
      },
      error: (err) => {
        console.error('Error loading historical metrics:', err);
      }
    });
  }

  connectWebSocket() {
    const endpoint = `ws/health/${this.serverId}/`;
    
    this.wsSubscription = this.wsService.connect(endpoint).subscribe({
      next: (message: WebSocketMessage) => {
        if (message.type === 'health_update' && message.data) {
          this.handleHealthUpdate(message.data);
        } else if (message.type === 'error') {
          console.error('WebSocket error:', message.message || message.error);
        }
      },
      error: (err) => {
        console.error('WebSocket subscription error:', err);
      }
    });

    this.wsStatusSubscription = this.wsService.getConnectionStatus(endpoint).subscribe({
      next: (connected) => {
        this.wsConnected = connected;
        if (!connected) {
          console.log('WebSocket disconnected, falling back to polling');
          this.startPolling();
        } else {
          console.log('WebSocket connected for health monitoring');
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
    this.wsService.disconnect(`ws/health/${this.serverId}/`);
  }

  handleHealthUpdate(data: any) {
    if (data.connected) {
      this.currentMetrics = {
        cpu_usage: data.cpu_usage,
        memory_usage: data.memory_usage,
        disk_usage: data.disk_usage,
        network_in: data.network_in,
        network_out: data.network_out,
      };
      this.loading = false;
    } else {
      console.error('Server not connected:', data.error);
    }
  }

  startPolling() {
    if (this.pollingInterval) return;
    
    this.pollingInterval = setInterval(() => {
      this.loadCurrentMetrics();
    }, 30000); // Poll every 30 seconds
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }

  getHealthClass(value: number, type: 'cpu' | 'memory' | 'disk'): string {
    if (value > 90) return 'health-critical';
    if (value > 75) return 'health-warning';
    return 'health-good';
  }
}

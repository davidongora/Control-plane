import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, Service } from '../../services/api';
import { WebSocketService, WebSocketMessage } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-services',
  imports: [CommonModule],
  templateUrl: './services.html',
  styleUrl: './services.css',
})
export class Services implements OnInit, OnDestroy {
  services: Service[] = [];
  loading = true;
  wsConnections: Map<number, Subscription> = new Map();
  wsStatusConnections: Map<number, Subscription> = new Map();
  serverConnectionStatus: Map<number, boolean> = new Map();

  constructor(
    private api: Api,
    private wsService: WebSocketService
  ) {}

  ngOnInit() {
    this.loadServices();
  }

  ngOnDestroy() {
    this.disconnectAllWebSockets();
  }

  loadServices() {
    this.loading = true;
    this.api.getServices().subscribe({
      next: (response) => {
        this.services = response.results || response;
        this.loading = false;
        
        // Connect to WebSocket for each unique server
        this.connectToServiceUpdates();
      },
      error: (err) => {
        console.error('Error loading services:', err);
        this.loading = false;
      }
    });
  }

  connectToServiceUpdates() {
    // Get unique server IDs
    const serverIds = [...new Set(this.services.map(s => s.server))];
    
    serverIds.forEach(serverId => {
      if (!this.wsConnections.has(serverId)) {
        const endpoint = `ws/services/${serverId}/`;
        
        const subscription = this.wsService.connect(endpoint).subscribe({
          next: (message: WebSocketMessage) => {
            if (message.type === 'service_status' && message.data) {
              this.handleServiceStatusUpdate(serverId, message.data);
            } else if (message.type === 'error') {
              console.error(`WebSocket error for server ${serverId}:`, message.message || message.error);
            }
          },
          error: (err) => {
            console.error(`WebSocket subscription error for server ${serverId}:`, err);
          }
        });
        
        this.wsConnections.set(serverId, subscription);
        
        // Monitor connection status
        const statusSubscription = this.wsService.getConnectionStatus(endpoint).subscribe({
          next: (connected) => {
            this.serverConnectionStatus.set(serverId, connected);
          }
        });
        
        this.wsStatusConnections.set(serverId, statusSubscription);
      }
    });
  }

  disconnectAllWebSockets() {
    this.wsConnections.forEach((subscription, serverId) => {
      subscription.unsubscribe();
      this.wsService.disconnect(`ws/services/${serverId}/`);
    });
    this.wsConnections.clear();
    
    this.wsStatusConnections.forEach(subscription => {
      subscription.unsubscribe();
    });
    this.wsStatusConnections.clear();
  }

  handleServiceStatusUpdate(serverId: number, serviceData: any[]) {
    // Update services for this server
    serviceData.forEach(updatedService => {
      const index = this.services.findIndex(s => s.id === updatedService.id);
      if (index !== -1) {
        this.services[index] = { 
          ...this.services[index], 
          ...updatedService,
          server: serverId
        };
      }
    });
  }

  isServerConnected(serverId: number): boolean {
    return this.serverConnectionStatus.get(serverId) || false;
  }

  startService(service: Service) {
    if (!service.id) return;
    
    this.api.startService(service.id).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadServices();
      },
      error: (err) => {
        console.error('Error starting service:', err);
        alert('Failed to start service');
      }
    });
  }

  stopService(service: Service) {
    if (!service.id) return;
    
    this.api.stopService(service.id).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadServices();
      },
      error: (err) => {
        console.error('Error stopping service:', err);
        alert('Failed to stop service');
      }
    });
  }

  restartService(service: Service) {
    if (!service.id) return;
    
    this.api.restartService(service.id).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadServices();
      },
      error: (err) => {
        console.error('Error restarting service:', err);
        alert('Failed to restart service');
      }
    });
  }
}

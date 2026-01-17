import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Api, HealthMetrics, Server } from '../../services/api';

@Component({
  selector: 'app-server-health',
  imports: [CommonModule],
  templateUrl: './server-health.html',
  styleUrl: './server-health.css',
})
export class ServerHealth implements OnInit {
  serverId!: number;
  server?: Server;
  currentMetrics?: HealthMetrics;
  historicalMetrics: any[] = [];
  loading = true;
  refreshInterval: any;

  constructor(
    private api: Api,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.serverId = +params['id'];
      this.loadServerInfo();
      this.loadCurrentMetrics();
      this.loadHistoricalMetrics();
      
      // Refresh metrics every 30 seconds
      this.refreshInterval = setInterval(() => {
        this.loadCurrentMetrics();
      }, 30000);
    });
  }

  ngOnDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
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

  getHealthClass(value: number, type: 'cpu' | 'memory' | 'disk'): string {
    if (value > 90) return 'health-critical';
    if (value > 75) return 'health-warning';
    return 'health-good';
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Api, Server, Service } from '../../services/api';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  servers: Server[] = [];
  services: Service[] = [];
  loading = true;
  error: string | null = null;

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadDashboardData();
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
}

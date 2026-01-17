import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, Service } from '../../services/api';

@Component({
  selector: 'app-services',
  imports: [CommonModule],
  templateUrl: './services.html',
  styleUrl: './services.css',
})
export class Services implements OnInit {
  services: Service[] = [];
  loading = true;

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadServices();
  }

  loadServices() {
    this.loading = true;
    this.api.getServices().subscribe({
      next: (response) => {
        this.services = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading services:', err);
        this.loading = false;
      }
    });
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

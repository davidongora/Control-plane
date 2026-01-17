import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, NginxSite } from '../../services/api';

@Component({
  selector: 'app-nginx-sites',
  imports: [CommonModule],
  templateUrl: './nginx-sites.html',
  styleUrl: './nginx-sites.css',
})
export class NginxSites implements OnInit {
  sites: NginxSite[] = [];
  loading = true;

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadSites();
  }

  loadSites() {
    this.loading = true;
    this.api.getNginxSites().subscribe({
      next: (response) => {
        this.sites = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading nginx sites:', err);
        this.loading = false;
      }
    });
  }

  enableSite(site: NginxSite) {
    if (!site.id) return;
    
    this.api.enableNginxSite(site.id).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadSites();
      },
      error: (err) => {
        console.error('Error enabling site:', err);
        alert('Failed to enable site');
      }
    });
  }

  disableSite(site: NginxSite) {
    if (!site.id) return;
    
    this.api.disableNginxSite(site.id).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadSites();
      },
      error: (err) => {
        console.error('Error disabling site:', err);
        alert('Failed to disable site');
      }
    });
  }

  viewConfig(site: NginxSite) {
    if (!site.id) return;
    
    this.api.getNginxSiteConfig(site.id).subscribe({
      next: (response) => {
        alert('Config:\n\n' + response.config);
      },
      error: (err) => {
        console.error('Error viewing config:', err);
        alert('Failed to get configuration');
      }
    });
  }
}

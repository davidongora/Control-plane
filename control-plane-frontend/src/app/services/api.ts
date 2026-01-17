import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Server {
  id?: number;
  name: string;
  hostname: string;
  ip_address: string;
  port: number;
  username: string;
  description?: string;
  is_active: boolean;
  services_count?: number;
  projects_count?: number;
  created_at?: string;
}

export interface Service {
  id?: number;
  server: number;
  server_name?: string;
  name: string;
  service_type: string;
  status: string;
  port?: number;
  pid?: number;
  cpu_usage?: number;
  memory_usage?: number;
  config_path?: string;
}

export interface NginxSite {
  id?: number;
  server: number;
  server_name?: string;
  site_name: string;
  domain: string;
  config_path: string;
  is_enabled: boolean;
  has_ssl: boolean;
  ssl_cert_path?: string;
  ssl_key_path?: string;
  upstream_port?: number;
}

export interface Project {
  id?: number;
  server: number;
  server_name?: string;
  name: string;
  path: string;
  project_type: string;
  branch?: string;
  repository_url?: string;
  is_active: boolean;
  last_deployed?: string;
}

export interface HealthMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_in?: number;
  network_out?: number;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root',
})
export class Api {
  private baseUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  // Server endpoints
  getServers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/servers/`);
  }

  getServer(id: number): Observable<Server> {
    return this.http.get<Server>(`${this.baseUrl}/servers/${id}/`);
  }

  createServer(server: Server): Observable<Server> {
    return this.http.post<Server>(`${this.baseUrl}/servers/`, server);
  }

  updateServer(id: number, server: Server): Observable<Server> {
    return this.http.put<Server>(`${this.baseUrl}/servers/${id}/`, server);
  }

  deleteServer(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/servers/${id}/`);
  }

  testConnection(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/servers/${id}/test_connection/`, {});
  }

  getServerHealth(id: number): Observable<HealthMetrics> {
    return this.http.get<HealthMetrics>(`${this.baseUrl}/servers/${id}/health/`);
  }

  getServerServicesStatus(id: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/servers/${id}/services_status/`);
  }

  // Service endpoints
  getServices(): Observable<any> {
    return this.http.get(`${this.baseUrl}/services/`);
  }

  getService(id: number): Observable<Service> {
    return this.http.get<Service>(`${this.baseUrl}/services/${id}/`);
  }

  createService(service: Service): Observable<Service> {
    return this.http.post<Service>(`${this.baseUrl}/services/`, service);
  }

  updateService(id: number, service: Service): Observable<Service> {
    return this.http.put<Service>(`${this.baseUrl}/services/${id}/`, service);
  }

  deleteService(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/services/${id}/`);
  }

  startService(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/services/${id}/start/`, {});
  }

  stopService(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/services/${id}/stop/`, {});
  }

  restartService(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/services/${id}/restart/`, {});
  }

  // Nginx site endpoints
  getNginxSites(): Observable<any> {
    return this.http.get(`${this.baseUrl}/nginx-sites/`);
  }

  getNginxSite(id: number): Observable<NginxSite> {
    return this.http.get<NginxSite>(`${this.baseUrl}/nginx-sites/${id}/`);
  }

  createNginxSite(site: NginxSite): Observable<NginxSite> {
    return this.http.post<NginxSite>(`${this.baseUrl}/nginx-sites/`, site);
  }

  updateNginxSite(id: number, site: NginxSite): Observable<NginxSite> {
    return this.http.put<NginxSite>(`${this.baseUrl}/nginx-sites/${id}/`, site);
  }

  deleteNginxSite(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/nginx-sites/${id}/`);
  }

  enableNginxSite(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/nginx-sites/${id}/enable/`, {});
  }

  disableNginxSite(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/nginx-sites/${id}/disable/`, {});
  }

  getNginxSiteConfig(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/nginx-sites/${id}/config/`);
  }

  // Project endpoints
  getProjects(): Observable<any> {
    return this.http.get(`${this.baseUrl}/projects/`);
  }

  getProject(id: number): Observable<Project> {
    return this.http.get<Project>(`${this.baseUrl}/projects/${id}/`);
  }

  createProject(project: Project): Observable<Project> {
    return this.http.post<Project>(`${this.baseUrl}/projects/`, project);
  }

  updateProject(id: number, project: Project): Observable<Project> {
    return this.http.put<Project>(`${this.baseUrl}/projects/${id}/`, project);
  }

  deleteProject(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/projects/${id}/`);
  }

  // Health metrics endpoints
  getHealthMetrics(serverId?: number): Observable<any> {
    const url = serverId 
      ? `${this.baseUrl}/health-metrics/?server_id=${serverId}`
      : `${this.baseUrl}/health-metrics/`;
    return this.http.get(url);
  }
}

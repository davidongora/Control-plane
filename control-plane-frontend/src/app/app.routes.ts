import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { Servers } from './components/servers/servers';
import { Services } from './components/services/services';
import { NginxSites } from './components/nginx-sites/nginx-sites';
import { Projects } from './components/projects/projects';
import { ServerHealth } from './components/server-health/server-health';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: Dashboard },
  { path: 'servers', component: Servers },
  { path: 'services', component: Services },
  { path: 'nginx-sites', component: NginxSites },
  { path: 'projects', component: Projects },
  { path: 'server-health/:id', component: ServerHealth },
];

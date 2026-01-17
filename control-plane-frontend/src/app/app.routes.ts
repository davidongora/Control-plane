import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { Servers } from './components/servers/servers';
import { Services } from './components/services/services';
import { NginxSites } from './components/nginx-sites/nginx-sites';
import { Projects } from './components/projects/projects';
import { ServerHealth } from './components/server-health/server-health';
import { Login } from './components/login/login';
import { DatabaseClientComponent } from './components/database-client/database-client';
import { UserManagementComponent } from './components/user-management/user-management';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: Dashboard, canActivate: [authGuard] },
  { path: 'servers', component: Servers, canActivate: [authGuard] },
  { path: 'services', component: Services, canActivate: [authGuard] },
  { path: 'nginx-sites', component: NginxSites, canActivate: [authGuard] },
  { path: 'projects', component: Projects, canActivate: [authGuard] },
  { path: 'server-health/:id', component: ServerHealth, canActivate: [authGuard] },
  { path: 'database-client', component: DatabaseClientComponent, canActivate: [authGuard] },
  { path: 'user-management', component: UserManagementComponent, canActivate: [authGuard] },
];

import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { ApiService } from './services/api.service';
import { Router } from '@angular/router';

const authGuard = () => {
  const api: ApiService = inject(ApiService);
  const router: Router = inject(Router);
  if (api.isAuthenticated()) {
    return true;
  }
  return router.parseUrl('/login');
};

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'projects/:id',
    loadComponent: () => import('./pages/project-detail.component').then(m => m.ProjectDetailComponent),
    canActivate: [authGuard]
  }
];
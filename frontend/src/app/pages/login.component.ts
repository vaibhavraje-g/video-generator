import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-slate-950 transition-colors duration-300">
      <div class="w-full max-w-md space-y-8">
        <div class="text-center">
          <div class="mx-auto w-12 h-12 rounded-xl bg-amber-600 flex items-center justify-center text-white font-bold text-2xl mb-4 shadow-lg shadow-amber-600/20">V</div>
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">Sign in to your account</h2>
          <p class="mt-2 text-sm text-gray-600 dark:text-slate-400">
            Or
            <a routerLink="/register" class="font-medium text-amber-600 hover:text-amber-500 dark:text-amber-500 dark:hover:text-amber-400">
              create a new account
            </a>
          </p>
        </div>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="mt-8 space-y-6">
          <div class="space-y-4 rounded-md shadow-sm">
            <div>
              <label for="email" class="sr-only">Email address</label>
              <input id="email" type="email" formControlName="email" class="relative block w-full rounded-lg border-0 bg-white dark:bg-slate-900 py-3 px-3 text-gray-900 dark:text-white ring-1 ring-inset ring-gray-300 dark:ring-slate-800 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-amber-500 sm:text-sm sm:leading-6 transition-colors" placeholder="Email address">
            </div>
            <div>
              <label for="password" class="sr-only">Password</label>
              <input id="password" type="password" formControlName="password" class="relative block w-full rounded-lg border-0 bg-white dark:bg-slate-900 py-3 px-3 text-gray-900 dark:text-white ring-1 ring-inset ring-gray-300 dark:ring-slate-800 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-amber-500 sm:text-sm sm:leading-6 transition-colors" placeholder="Password">
            </div>
          </div>

          @if (error()) {
            <div class="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <div class="flex">
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-red-800 dark:text-red-400">{{ error() }}</h3>
                </div>
              </div>
            </div>
          }

          <div>
            <button type="submit" [disabled]="isLoading()" class="group relative flex w-full justify-center rounded-lg bg-amber-600 px-3 py-3 text-sm font-semibold text-white hover:bg-amber-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all">
              @if (isLoading()) {
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing in...
              } @else {
                Sign in
              }
            </button>
            <button type="button" (click)="bypassLogin()" class="mt-4 group relative flex w-full justify-center rounded-lg border border-amber-600 px-3 py-3 text-sm font-semibold text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-600 transition-all">
              Skip Login (Dev Mode)
            </button>
          </div>
        </form>
      </div>
    </div>
  `
})
export class LoginComponent {
  private fb: FormBuilder = inject(FormBuilder);
  private api = inject(ApiService);
  private router: Router = inject(Router);

  isLoading = signal(false);
  error = signal('');

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  async onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    this.error.set('');

    try {
      const { email, password } = this.loginForm.value;
      await this.api.login(email!, password!);
      this.router.navigate(['/dashboard']);
    } catch (err: any) {
      this.error.set(err.message || 'Failed to login');
    } finally {
      this.isLoading.set(false);
    }
  }

  async bypassLogin() {
    localStorage.setItem('vidgen_token', 'dev_token');
    
    // Set a dummy user structure that matches what ApiService expects
    const dummyUser = {
      _id: 'dev_user_id',
      email: 'dev@vidgen.ai',
      username: 'developer'
    };
    
    localStorage.setItem('vidgen_user', JSON.stringify(dummyUser));
    
    // Force refresh of current user signal in API service if possible, or just reload
    // Since we can't easily access the signal setter from here without exposing it, 
    // we'll rely on the dashboard guard/init to pick it up or just reload.
    // Better: let's try to reload the page to ensure fresh state or just navigate.
    
    // We need to update the ApiService state. Since we can't directly set the signal from here (it's protected/private logic usually, 
    // but looking at ApiService, currentUser is a public signal but loadUser is private).
    // Actually, ApiService.currentUser is initialized from localStorage.
    // So if we set localStorage and then trigger a refresh/navigate, it might work if we reload.
    // Or we can add a method to ApiService to setDevMode.
    // For now, simple localStorage + reload/navigate.
    
    // Let's use window.location.reload() to be sure everything initializes correctly with the token.
    window.location.href = '/#/dashboard';
    window.location.reload();
  }
}
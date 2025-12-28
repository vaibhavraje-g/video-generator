import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-slate-950 transition-colors duration-300">
      <div class="w-full max-w-md space-y-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">Create your account</h2>
          <p class="mt-2 text-sm text-gray-600 dark:text-slate-400">
            Already have an account?
            <a routerLink="/login" class="font-medium text-amber-600 hover:text-amber-500 dark:text-amber-500 dark:hover:text-amber-400">
              Sign in
            </a>
          </p>
        </div>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="mt-8 space-y-6">
          <div class="space-y-4 rounded-md shadow-sm">
            <div>
              <label for="username" class="sr-only">Username</label>
              <input id="username" type="text" formControlName="username" class="relative block w-full rounded-lg border-0 bg-white dark:bg-slate-900 py-3 px-3 text-gray-900 dark:text-white ring-1 ring-inset ring-gray-300 dark:ring-slate-800 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-amber-500 sm:text-sm sm:leading-6 transition-colors" placeholder="Username">
            </div>
            <div>
              <label for="email" class="sr-only">Email address</label>
              <input id="email" type="email" formControlName="email" class="relative block w-full rounded-lg border-0 bg-white dark:bg-slate-900 py-3 px-3 text-gray-900 dark:text-white ring-1 ring-inset ring-gray-300 dark:ring-slate-800 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-amber-500 sm:text-sm sm:leading-6 transition-colors" placeholder="Email address">
            </div>
            <div>
              <label for="password" class="sr-only">Password</label>
              <input id="password" type="password" formControlName="password" class="relative block w-full rounded-lg border-0 bg-white dark:bg-slate-900 py-3 px-3 text-gray-900 dark:text-white ring-1 ring-inset ring-gray-300 dark:ring-slate-800 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-amber-500 sm:text-sm sm:leading-6 transition-colors" placeholder="Password (min 6 chars)">
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
            <button type="submit" [disabled]="isLoading()" class="group relative flex w-full justify-center rounded-lg bg-amber-600 px-3 py-3 text-sm font-semibold text-white hover:bg-amber-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-600 disabled:opacity-50 transition-all">
              @if (isLoading()) {
                <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                   <!-- Spinner -->
                </span>
                Creating account...
              } @else {
                Register
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  `
})
export class RegisterComponent {
  private fb: FormBuilder = inject(FormBuilder);
  private api = inject(ApiService);
  private router: Router = inject(Router);

  isLoading = signal(false);
  error = signal('');

  registerForm = this.fb.group({
    username: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  async onSubmit() {
    if (this.registerForm.invalid) return;

    this.isLoading.set(true);
    this.error.set('');

    try {
      const { email, username, password } = this.registerForm.value;
      await this.api.register(email!, username!, password!);
      this.router.navigate(['/dashboard']);
    } catch (err: any) {
      this.error.set(err.message || 'Registration failed');
    } finally {
      this.isLoading.set(false);
    }
  }
}
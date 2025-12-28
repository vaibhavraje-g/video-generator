import { Injectable, signal, effect } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  isDark = signal<boolean>(true);

  constructor() {
    const stored = localStorage.getItem('vidgen_theme');
    if (stored) {
      this.isDark.set(stored === 'dark');
    } else {
      // Default to dark if no preference
      this.isDark.set(true); 
    }

    effect(() => {
      const isDark = this.isDark();
      const html = document.documentElement;
      if (isDark) {
        html.classList.add('dark');
        localStorage.setItem('vidgen_theme', 'dark');
      } else {
        html.classList.remove('dark');
        localStorage.setItem('vidgen_theme', 'light');
      }
    });
  }

  toggle() {
    this.isDark.update(v => !v);
  }
}
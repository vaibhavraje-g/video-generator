import { Component, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { ApiService } from './services/api.service';
import { ThemeService } from './services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html'
})
export class AppComponent {
  private api = inject(ApiService);
  private router: Router = inject(Router);
  // Inject to initialize
  private themeService = inject(ThemeService);

  currentUser = this.api.currentUser;

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
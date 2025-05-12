import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { ThemeService } from '../../services/theme.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  standalone: false
})
export class SidebarComponent {
  isDarkTheme$ = this.themeService.isDarkTheme$;
  currentUrl: string = '';

  constructor(
    private readonly themeService: ThemeService,
    private router: Router
  ) {
    // Subscribe to router events to update active link
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentUrl = event.url;
    });
  }

  // Navigate programmatically
  navigate(path: string): void {
    this.router.navigate([path], { 
      skipLocationChange: false,
      replaceUrl: false
    });
  }

  // Check if route is active
  isActive(route: string): boolean {
    return this.currentUrl === route;
  }
}
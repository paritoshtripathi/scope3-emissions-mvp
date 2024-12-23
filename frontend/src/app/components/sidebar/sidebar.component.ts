import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  standalone: false
})
export class SidebarComponent implements OnInit {
  activeLink: string = '';
  hasError = false;
  errorMessage = 'Something went wrong loading the sidebar.';
  constructor(private router: Router, private activatedRoute: ActivatedRoute) {}

  ngOnInit(): void {
    try{
    // Listen to route changes and update the active link
    this.router.events.subscribe(() => {
      this.activeLink = this.router.url; // Set the current route as active
      console.log('Sidebar initialized + this.activeLink:', this.activeLink);
    });
    } catch (error) {
      console.error('Error in SidebarComponent:', error);
    this.hasError = true;
    }
  }

  navigate(link: string): void {
    this.router.navigate([link]); // Navigate programmatically
  }
}

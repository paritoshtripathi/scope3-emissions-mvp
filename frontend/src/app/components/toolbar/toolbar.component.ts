import { Component } from '@angular/core';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss'],
  standalone: false
})
export class ToolbarComponent {
  isDarkTheme$ = this.themeService.isDarkTheme$;

  constructor(private themeService: ThemeService) {}

  triggerWalkthrough(): void {
    const walkthroughEvent = new CustomEvent('startWalkthrough');
    window.dispatchEvent(walkthroughEvent);
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
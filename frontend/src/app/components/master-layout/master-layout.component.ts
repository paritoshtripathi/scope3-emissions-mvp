import { Component, ViewChild } from '@angular/core';
import { AvatarComponent } from '@components/avatar/avatar.component';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-master-layout',
  templateUrl: './master-layout.component.html',
  styleUrls: ['./master-layout.component.scss'],
  standalone: false
})
export class MasterLayoutComponent {
  isDarkTheme$ = this.themeService.isDarkTheme$;

  @ViewChild(AvatarComponent) avatarComponent!: AvatarComponent;

  constructor(private readonly themeService: ThemeService) {}

  ngOnInit(): void {
    console.log('Master layout initialized');
  }

  reinitiateWalkthrough(): void {
    if (this.avatarComponent) {
      this.avatarComponent.reinitiateWalkthrough();
    }
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
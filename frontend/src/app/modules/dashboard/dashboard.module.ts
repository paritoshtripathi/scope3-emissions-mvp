import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { SidebarComponent } from '@components/sidebar/sidebar.component';
import { ToolbarComponent } from '@components/toolbar/toolbar.component';
import { VisualizationSectionComponent } from '@components/visualization-section/visualization-section.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';

@NgModule({
  declarations: [
    DashboardComponent,
    SidebarComponent,
    ToolbarComponent,
    VisualizationSectionComponent,
  ],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    MatSidenavModule,
    MatListModule,
    MatTooltipModule,
    MatButtonModule,
  ],
})
export class DashboardModule {}

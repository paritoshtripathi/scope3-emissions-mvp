import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardComponent } from '../../components/dashboard/dashboard.component';

@NgModule({
  declarations: [
    DashboardComponent
  ],
  imports: [
    CommonModule,
    DashboardRoutingModule // Import routing module for dashboard routes
  ],
  exports: [
    DashboardComponent // Export if used outside of this module
  ]
})
export class DashboardModule { }

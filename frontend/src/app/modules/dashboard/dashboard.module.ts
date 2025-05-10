import { NgModule } from '@angular/core';
import { SharedModule } from '@modules/shared/shared.module';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';

@NgModule({
  declarations: [
    DashboardComponent
  ],
  imports: [
    SharedModule,
    DashboardRoutingModule,
    MatCardModule,
    MatIconModule,
    MatDividerModule
  ]
})
export class DashboardModule { }
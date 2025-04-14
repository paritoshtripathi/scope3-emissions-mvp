import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { SharedModule } from '@modules/shared/shared.module'; // Import SharedModule
import { CanvasModule } from '../canvas/canvas.module';


@NgModule({
  declarations: [DashboardComponent],
  imports: [CommonModule, DashboardRoutingModule, CanvasModule, SharedModule],// Include SharedModule here
  exports: [DashboardComponent]
})
export class DashboardModule {}

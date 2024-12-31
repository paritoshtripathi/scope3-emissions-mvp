import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { SharedModule } from '@modules/shared/shared.module'; // Import SharedModule
import { AvatarComponent } from '@components/avatar/avatar.component';

@NgModule({
  declarations: [DashboardComponent,AvatarComponent],
  imports: [CommonModule, DashboardRoutingModule, SharedModule],// Include SharedModule here
  exports: [DashboardComponent, AvatarComponent]
})
export class DashboardModule {}

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { CanvasComponent } from '@components/canvas/canvas.component';

const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'canvas', component: CanvasComponent }

];

@NgModule({
  //declarations: [DashboardComponent],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class DashboardRoutingModule {}

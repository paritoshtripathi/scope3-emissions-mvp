import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CanvasComponent } from '../../components/canvas/canvas.component';

const routes: Routes = [
  { path: '', component: CanvasComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CanvasRoutingModule {}
// This module defines the routing for the Canvas module in an Angular application.
// It imports the necessary Angular modules and sets up a route that maps the empty path ('') to the CanvasComponent.
// The CanvasRoutingModule is then imported into the CanvasModule, allowing the application to navigate to the CanvasComponent when the user accesses the root path of the Canvas module.
// The CanvasRoutingModule is imported into the CanvasModule, allowing the application to navigate to the CanvasComponent when the user accesses the root path of the Canvas module.
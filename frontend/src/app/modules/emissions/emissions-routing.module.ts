import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { EmissionsComponent } from '@components/emissions/emissions.component';

const routes: Routes = [
  { path: '', component: EmissionsComponent }
];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})

export class EmissionsRoutingModule { }

// src/app/components/data-upload/data-upload-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DataUploadComponent } from '@components/data-upload/data-upload.component';

const routes: Routes = [
  {
    path: '',
    component: DataUploadComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DataUploadRoutingModule { }

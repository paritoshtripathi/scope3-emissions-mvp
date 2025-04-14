// src/app/components/data-upload/data-upload.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { DataUploadRoutingModule } from '@modules/data-upload/data-upload-routing.module';
import { DataUploadComponent } from '@components/data-upload/data-upload.component';

@NgModule({
  declarations: [DataUploadComponent],
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    DataUploadRoutingModule
  ]
})
export class DataUploadModule { }

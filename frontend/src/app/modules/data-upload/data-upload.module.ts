import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

// Material Imports
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';

import { DataUploadRoutingModule } from './data-upload-routing.module';
import { DataUploadComponent } from '../../components/data-upload/data-upload.component';

@NgModule({
  declarations: [
    DataUploadComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    DataUploadRoutingModule,
    // Material Modules
    MatSelectModule,
    MatButtonModule,
    MatProgressBarModule,
    MatFormFieldModule,
    MatInputModule,
    MatCardModule,
    MatIconModule,
    MatTableModule
  ]
})
export class DataUploadModule { }
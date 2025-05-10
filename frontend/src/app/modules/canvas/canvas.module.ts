import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasComponent } from '../../components/canvas/canvas.component';
import { NgApexchartsModule } from 'ng-apexcharts';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [CanvasComponent],
  imports: [
    CommonModule,
    NgApexchartsModule,
    HttpClientModule
  ],
  exports: [CanvasComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CanvasModule { }
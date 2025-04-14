
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasComponent } from '../../components/canvas/canvas.component';
import { NgApexchartsModule } from 'ng-apexcharts';

@NgModule({
  declarations: [CanvasComponent],
  imports: [CommonModule, NgApexchartsModule],
  exports: [CanvasComponent]
})
export class CanvasModule {}

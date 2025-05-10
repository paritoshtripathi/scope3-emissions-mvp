import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgxEchartsModule, NGX_ECHARTS_CONFIG } from 'ngx-echarts';
import * as echarts from 'echarts';

// Material Imports
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';

import { VisualizationSectionComponent } from '@components/visualization-section/visualization-section.component';
import { AvatarComponent } from '@components/avatar/avatar.component';

@NgModule({
  declarations: [
    VisualizationSectionComponent,
    AvatarComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    NgxEchartsModule.forRoot({
      echarts
    }),
    // Material Modules
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDividerModule,
    MatListModule,
    MatToolbarModule,
    MatSidenavModule
  ],
  providers: [
    {
      provide: NGX_ECHARTS_CONFIG,
      useValue: { echarts }
    }
  ],
  exports: [
    CommonModule,
    FormsModule,
    VisualizationSectionComponent,
    AvatarComponent,
    // Material Modules
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDividerModule,
    MatListModule,
    MatToolbarModule,
    MatSidenavModule
  ]
})
export class SharedModule { }
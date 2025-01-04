import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
//import { RouterModule } from '@angular/router';
//import { AppRoutingModule } from 'src/app/app-routing.module';
// import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; // Import this module
import { NgxEchartsModule, NGX_ECHARTS_CONFIG } from 'ngx-echarts';
import * as echarts from 'echarts';

import { VisualizationSectionComponent } from '@components/visualization-section/visualization-section.component';
import { ChatComponent } from '@components/chat/chat.component';
import { AvatarComponent } from '@components/avatar/avatar.component';

//import { RouterModule } from '@angular/router';
//import { Router } from '@angular/router';

@NgModule({
  declarations: [
    VisualizationSectionComponent,
    AvatarComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    // RouterModule.forChild([]),
    NgxEchartsModule.forRoot({
      echarts
    })

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
    AvatarComponent
  ]
})
export class SharedModule { }

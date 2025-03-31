import { NgModule } from '@angular/core';
import { SharedModule } from '@modules/shared/shared.module';
import { MasterLayoutComponent } from '@components/master-layout/master-layout.component';
import { RouterModule } from '@angular/router';
import { SidebarComponent } from '@components/sidebar/sidebar.component';
import { ToolbarComponent } from '@components/toolbar/toolbar.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';


@NgModule({
  declarations: [
    MasterLayoutComponent,
    SidebarComponent,
    ToolbarComponent
  ],
  imports: [
    SharedModule,
    RouterModule,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatListModule,
    MatTooltipModule
  ],
  exports: [
    MasterLayoutComponent
  ]
})
export class MasterLayoutModule {}

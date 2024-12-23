import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';

import { AppComponent } from './app.component';
import { MasterLayoutComponent } from '@components/master-layout/master-layout.component';
import { SidebarComponent } from '@components/sidebar/sidebar.component';
import { ToolbarComponent } from '@components/toolbar/toolbar.component';
import { ChatComponent } from '@components/chat/chat.component';
import { ErrorBoundaryComponent } from '@components/error-boundary/error-boundary.component';

@NgModule({
  declarations: [
    AppComponent,
    MasterLayoutComponent,
    SidebarComponent,
    ToolbarComponent,
    ChatComponent,
    ErrorBoundaryComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    RouterModule.forRoot([]),
    MatToolbarModule,
    MatSidenavModule,
    MatIconModule,
    MatListModule
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}

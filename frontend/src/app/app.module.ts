import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { JwtModule } from '@auth0/angular-jwt';
import { RouterModule } from '@angular/router';
import { SharedModule } from './modules/shared/shared.module';
import { MasterLayoutModule } from './modules/masterlayout/masterlayout.module';
import { AuthInterceptor } from './modules/auth/interceptors/auth.interceptor';
import { CHAT_CONFIG } from './services/chat.types';
import { KBManagerComponent } from './components/kb-manager/kb-manager.component';
import { KnowledgeBaseService } from '@services/knowledge-base.service';

// Function to get JWT token
export function tokenGetter() {
  return localStorage.getItem('token');
}

@NgModule({
  declarations: [
    AppComponent,
    KBManagerComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    RouterModule,
    SharedModule,
    MasterLayoutModule,
    JwtModule.forRoot({
      config: {
        tokenGetter: tokenGetter,
        allowedDomains: [window.location.host, 'localhost:5000'],
        disallowedRoutes: [`${window.location.origin}/api/auth`]
      }
    })
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
    {
      provide: CHAT_CONFIG,
      useValue: {
        ragApiUrl: 'http://localhost:5000/api/v1/rag',
        maxHistory: 50,
        retryAttempts: 3,
        messageTimeout: 30000
      }
    },
    KnowledgeBaseService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
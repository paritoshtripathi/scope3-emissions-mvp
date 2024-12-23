import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { RouterModule, RoutesRecognized, Router  } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { AiMlService } from '@services/ai-ml.service';
import { AppComponent } from './app.component';
import { ChatComponent } from '@components/chat/chat.component';
import { ErrorBoundaryComponent } from '@components/error-boundary/error-boundary.component';
import { MasterLayoutModule } from '@modules/masterlayout/masterlayout.module';
//import { Router } from '@angular/router';
@NgModule({
  declarations: [
    AppComponent,
    // MasterLayoutComponent,
    ChatComponent
    //ErrorBoundaryComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    AppRoutingModule,
    RouterModule.forRoot([]),
    MasterLayoutModule
  ],
  exports: [
    //MasterLayoutModule
  ],
  providers: [
    // { provide: ErrorHandler, useClass: AppErrorHandler },
    AiMlService,
    provideHttpClient(withInterceptorsFromDi())
  ],
  bootstrap: [AppComponent]
  
})
export class AppModule {

  constructor(private router: Router) {
    this.router.events.subscribe(event => {
      if (event instanceof RoutesRecognized) {
            console.log('Route:TESTINGGGGGGGGGG', event.state.root.children);
        }
    });
  }
  
}



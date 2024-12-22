import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

import { AppComponent } from './app.component';
import { PredictionComponent } from './components/prediction/prediction.component';
import { AiMlService } from './services/ai-ml.service';
import { ChatComponent } from './components/chat/chat.component';
import { DashboardModule } from './modules/dashboard/dashboard.module'; // Import DashboardModule


@NgModule({ declarations: [AppComponent, PredictionComponent, ChatComponent],
    bootstrap: [AppComponent], imports: [BrowserModule, FormsModule, DashboardModule], providers: [AiMlService, provideHttpClient(withInterceptorsFromDi())] })
export class AppModule {}

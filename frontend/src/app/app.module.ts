import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { PredictionComponent } from './components/prediction/prediction.component';
import { AiMlService } from './services/ai-ml.service';
import { ChatComponent } from './components/chat/chat.component';

@NgModule({
  declarations: [AppComponent, PredictionComponent, ChatComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [AiMlService],
  bootstrap: [AppComponent]
})
export class AppModule {}

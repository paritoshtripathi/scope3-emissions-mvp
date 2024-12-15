import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { PredictionComponent } from './components/prediction/prediction.component';
import { AiMlService } from './services/ai-ml.service';

@NgModule({
  declarations: [AppComponent, PredictionComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [AiMlService],
  bootstrap: [AppComponent]
})
export class AppModule {}

// frontend/src/app/components/prediction/prediction.component.ts
import { Component } from '@angular/core';
import { AiMlService } from '../../services/ai-ml.service';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.scss']
})
export class PredictionComponent {
  inputText: string = ''; // User input
  predictionResult: any;  // Prediction result
  isLoading: boolean = false; // Loader state

  constructor(private aiMlService: AiMlService) {}

  // Function to handle prediction request
  getPrediction(): void {
    if (!this.inputText.trim()) {
      alert('Please enter some text to predict.');
      return;
    }

    this.isLoading = true;
    this.aiMlService.getPrediction(this.inputText).subscribe(
      (response) => {
        this.predictionResult = response;
        this.isLoading = false;
      },
      (error) => {
        console.error('Error fetching prediction:', error);
        this.isLoading = false;
        alert('Failed to fetch prediction. Please try again later.');
      }
    );
  }
}

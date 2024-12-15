// src/app/services/ai-ml.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AiMlService {
  private apiUrl = 'http://localhost:3000/api/ai-ml/predict'; // Backend endpoint

  constructor(private http: HttpClient) {}

  // Function to send text to the backend for AI/ML prediction
  getPrediction(inputText: string): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { text: inputText };
    return this.http.post<any>(this.apiUrl, body, { headers });
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private baseUrl = '/api/data';

  constructor(private http: HttpClient) {}

  // Fetch emission insights
  // getInsights(): Observable<any> {
  //   return this.http.get<any>(`${this.baseUrl}/insights`);
  // }

  // // Predict emission reductions
  // predictReduction(payload: any): Observable<any> {
  //   return this.http.post<any>(`${this.baseUrl}/predict`, payload);
  // }
  getInsights(): Observable<any> {
    return this.http.get('/api/insights'); // Replace with your backend API
  }
  
  predictReduction(payload: any): Observable<any> {
    return this.http.post('/api/predict-reduction', payload); // Replace with your backend API
  }
}


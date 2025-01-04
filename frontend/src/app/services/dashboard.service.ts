import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  constructor(private http: HttpClient) {}

  getInsights(): Observable<any> {
    return this.http.get('http://localhost:3000/api/data/insights').pipe(
      map((response: any) => {
        // Transform the API data into a format suitable for pie and bar charts
        const pieData = response.insights.map((item: any) => ({
          value: item.total_emissions,
          category: item.category
        }));

        const barData = response.insights.map((item: any) => ({
          category: item.category,
          value: item.total_reduction
        }));

        return { pieData, barData };
      }),
      catchError((error) => {
        console.error('Error fetching insights:', error);
        // Fallback: Use dummy data for testing
        const dummyData = {
          pieData: [
            { value: 1000, category: 'Transport' },
            { value: 500, category: 'Energy' },
            { value: 300, category: 'Waste' }
          ],
          barData: [
            { category: 'Transport', value: 150 },
            { category: 'Energy', value: 80 },
            { category: 'Waste', value: 50 }
          ]
        };
        return of(dummyData);
      })
    );
  }

  predictReduction(payload: any): Observable<any> {
    return this.http.post('http://localhost:3000/api/data/predict', payload).pipe(
      map((response: any) => {
        // Transform prediction data
        return {
          category: response.category,
          predictedReduction: response.predicted_reduction,
          newEmissions: response.new_emissions
        };
      }),
      catchError((error) => {
        console.error('Error fetching predictions:', error);
        // Fallback: Use dummy prediction data
        return of({
          category: payload.category,
          predictedReduction: 10, // Default predicted reduction
          newEmissions: 900 // Default new emissions
        });
      })
    );
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private baseUrl = '/api/data';

  constructor(private http: HttpClient) {}

  // getInsights(): Observable<any> {
  //   return this.http.get('/api/data/insights').pipe(
  //     catchError((error) => {
  //       console.error('Error fetching insights:', error);
  //       // Return default mock data
  //       return of([
  //         { category: 'Category A', value: 100 },
  //         { category: 'Category B', value: 200 }
  //       ]);
  //     })
  //   );
  // }

  // predictReduction(payload: any): Observable<any> {
  //   return this.http.post('/api/data/predict', payload).pipe(
  //     catchError((error) => {
  //       console.error('Error predicting reductions:', error);
  //       // Return default mock data
  //       return of([{ category: 'Category A', value: 80 }]);
  //     })
  //   );
  // }


  getInsights(): Observable<any> {
    return this.http.get('/api/data/insights').pipe(
      map((response: any) => {
        // Transform the API data into a format suitable for pie and bar charts
        const pieData = response.insights.map((item: any) => ({
          value: item.total_emissions,
          name: item.category
        }));
  
        const barData = response.insights.map((item: any) => ({
          category: item.category,
          value: item.total_reduction
        }));
  
        return { pieData, barData };
      }),
      catchError((error) => {
        console.error('Error fetching insights:', error);
        return of({ pieData: [], barData: [] });
      })
    );
  }
  
  predictReduction(payload: any): Observable<any> {
    return this.http.post('/api/data/predict', payload).pipe(
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
        return of([]);
      })
    );
  }
  
}

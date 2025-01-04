import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AvatarService {

  private insightsApiUrl = 'http://localhost:3000/api/data/insights'; // NodeJS API to fetch data from DB
  private explanationApiUrl = 'http://localhost:3000/api/data/generateExplanation'; // NodeJS API for AI explanations


  constructor(private http: HttpClient) {}

  getInsights(): Observable<any[]> {
    return this.http.get(this.insightsApiUrl).pipe(
      map((response: any) => {
        console.log('Insights:', response);
        // Fetch data and pass to Llama 3 for dynamic explanations
        return response.insights.map((item: any) => ({
          category: item.category,
          total_emissions: item.total_emissions,
          total_reduction: item.total_reduction,
          title: `Insight on ${item.category}`,
          description: this.generateDynamicResponse(item.category,item.total_emissions,item.total_reduction)
        }));
      })
    );
  }

  generateExplanation(context: any): Observable<string> {
    console.log('Generating explanation with context Inside GenerateExplanation:', context);
    return this.http.post<string>(this.explanationApiUrl, { context });
  }

  private generateDynamicResponse(category: any, total_emissions: any, total_reduction: any): string {
    // Simulate Llama 3 analysis with retrieved context
    const context = `Emissions in ${category} are ${total_emissions} tons.`;
    const strategy = `And total reduction so far is ${total_reduction}, what is the best strategy to reduce emissions further?`;
    return `${context} ${strategy}`;
  }
}

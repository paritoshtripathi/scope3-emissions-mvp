import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AvatarService {
  private insightsApiUrl = 'http://localhost:3000/api/data/insights';
  private explanationApiUrl = 'http://localhost:3000/api/data/generateExplanation';
  private tourStatus = new BehaviorSubject<boolean>(false);
  private tourMessages = new BehaviorSubject<string | null>(null);

  constructor(private http: HttpClient) {}

  getInsights(): Observable<any[]> {
    return this.http.get(this.insightsApiUrl).pipe(
      map((response: any) => {
        console.log('Insights:', response);
        return response.insights.map((item: any) => ({
          category: item.category,
          total_emissions: item.total_emissions,
          total_reduction: item.total_reduction,
          title: `Insight on ${item.category}`,
          description: this.generateDynamicResponse(item.category, item.total_emissions, item.total_reduction)
        }));
      })
    );
  }

  generateExplanation(context: any): Observable<string> {
    console.log('Generating explanation with context Inside GenerateExplanation:', context);
    return this.http.post<string>(this.explanationApiUrl, { context });
  }

  private generateDynamicResponse(category: string, total_emissions: number, total_reduction: number): string {
    const context = `Emissions in ${category} are ${total_emissions} tons.`;
    const strategy = `And total reduction so far is ${total_reduction}, what is the best strategy to reduce emissions further?`;
    return `${context} ${strategy}`;
  }

  // New methods for tour functionality
  getTourStatus(): Observable<boolean> {
    return this.tourStatus.asObservable();
  }

  getTourMessages(): Observable<string | null> {
    return this.tourMessages.asObservable();
  }

  setTourStatus(isComplete: boolean): void {
    this.tourStatus.next(isComplete);
  }

  sendTourMessage(message: string): void {
    this.tourMessages.next(message);
  }

  completeTour(): void {
    this.tourStatus.next(true);
    // Dispatch event for chat toggle
    const event = new CustomEvent('toggleChat', { detail: true });
    window.dispatchEvent(event);
  }
}
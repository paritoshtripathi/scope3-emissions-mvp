import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AvatarService {
  private stepsUrl = '/api/walkthrough'; // Update this with your backend API endpoint

  constructor(private http: HttpClient) {}

  getWalkthroughSteps(): Observable<{ title: string; description: string }[]> {
    return this.http.get<{ title: string; description: string }[]>(this.stepsUrl);
  }
}

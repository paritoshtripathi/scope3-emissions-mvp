import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpEvent } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface UploadResponse {
  type?: 'progress' | 'response';
  progress?: number;
  columns?: string[];
  preview?: any[];
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DataUploadService {
  private apiUrl = 'http://localhost:3000/api/data/ingest';

  constructor(private http: HttpClient) {}

  uploadFile(file: File, s3Url?: string, category?: string): Observable<UploadResponse> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (s3Url) {
      formData.append('s3Url', s3Url);
    }
    if (category) {
      formData.append('category', category);
    }

    return this.http.post<any>(this.apiUrl, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progress = event.total ? Math.round(100 * event.loaded / event.total) : 0;
            return { type: 'progress', progress };
          case HttpEventType.Response:
            return {
              type: 'response',
              columns: event.body.columns,
              preview: event.body.preview,
              message: event.body.message
            };
          default:
            return { type: 'progress', progress: 0 };
        }
      })
    );
  }
}
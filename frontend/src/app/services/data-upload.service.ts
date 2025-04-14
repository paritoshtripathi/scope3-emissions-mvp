// src/app/services/data-upload.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataUploadService {
  private apiUrl = 'http://localhost:3000/api/data/ingest';

  constructor(private http: HttpClient) {}

  uploadFile(file: File, s3Url?: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (s3Url) {
      formData.append('s3Url', s3Url);
    }

    return this.http.post<any>(this.apiUrl, formData);
  }
}

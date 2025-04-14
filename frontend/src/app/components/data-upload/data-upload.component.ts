import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-data-upload',
  templateUrl: './data-upload.component.html',
  styleUrls: ['./data-upload.component.scss'],
  standalone: false
})
export class DataUploadComponent {
  selectedFile: File | null = null;
  s3Url: string = '';

  constructor(private http: HttpClient) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  submitData(): void {
    if (!this.selectedFile && !this.s3Url) {
      alert('Please upload a file or specify an S3 URL.');
      return;
    }

    const formData = new FormData();
    if (this.selectedFile) {
      formData.append('file', this.selectedFile);
    }

    if (this.s3Url) {
      formData.append('s3Url', this.s3Url);
    }

    this.http.post('/api/data/ingest', formData).subscribe({
      next: (response) => {
        alert('Data ingestion triggered successfully!');
        console.log(response);
      },
      error: (error) => {
        alert('Error in data ingestion.');
        console.error(error);
      }
    });
  }
}

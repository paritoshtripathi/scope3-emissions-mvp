import { Component } from '@angular/core';
import { DataUploadService } from '@services/data-upload.service';

@Component({
  selector: 'app-data-upload',
  templateUrl: './data-upload.component.html',
  styleUrls: ['./data-upload.component.scss'],
  standalone: false
})
export class DataUploadComponent {
  selectedFile: File | null = null;
  s3Url: string = '';
  columns: string[] = [];
  preview: any[] = [];

  constructor(private dataUploadService: DataUploadService) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  submitData(): void {
    if (!this.selectedFile && !this.s3Url) {
      alert('Please upload a file or specify an S3 URL.');
      return;
    }

    this.dataUploadService.uploadFile(this.selectedFile!, this.s3Url).subscribe({
      next: (response) => {
        this.columns = response.columns;
        this.preview = response.preview;
        console.log('File uploaded successfully:', response);
      },
      error: (err) => {
        console.error('Upload failed:', err);
        alert('Failed to upload file.');
      }
    });
  }
}

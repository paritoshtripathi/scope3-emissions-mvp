import { Component } from '@angular/core';
import { DataUploadService, UploadResponse } from '@services/data-upload.service';

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
  isUploading: boolean = false;
  uploadProgress: number = 0;
  errorMessage: string = '';
  successMessage: string = '';
  fileCategory: string = '';

  categories: string[] = [
    'Purchased Goods and Services',
    'Capital Goods',
    'Fuel and Energy',
    'Transportation and Distribution',
    'Waste Generated',
    'Business Travel',
    'Employee Commuting',
    'Other'
  ];

  constructor(private dataUploadService: DataUploadService) {}

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        this.errorMessage = 'Please upload a CSV file';
        this.selectedFile = null;
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        this.errorMessage = 'File size should not exceed 10MB';
        this.selectedFile = null;
        return;
      }
      this.selectedFile = file;
      this.errorMessage = '';
    }
  }

  submitData(): void {
    if (!this.selectedFile && !this.s3Url) {
      this.errorMessage = 'Please upload a file or specify an S3 URL.';
      return;
    }

    if (!this.fileCategory) {
      this.errorMessage = 'Please select a category for the data.';
      return;
    }

    this.isUploading = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.uploadProgress = 0;

    this.dataUploadService.uploadFile(this.selectedFile!, this.s3Url, this.fileCategory).subscribe({
      next: (response: UploadResponse) => {
        if (response.type === 'progress') {
          this.uploadProgress = response.progress || 0;
        } else {
          this.columns = response.columns || [];
          this.preview = response.preview || [];
          this.successMessage = response.message || 'File uploaded successfully!';
          this.isUploading = false;
          this.uploadProgress = 100;
        }
      },
      error: (err) => {
        this.isUploading = false;
        this.errorMessage = err.error?.message || 'Failed to upload file. Please try again.';
        console.error('Upload failed:', err);
      },
      complete: () => {
        this.isUploading = false;
      }
    });
  }

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }

  resetForm(): void {
    this.selectedFile = null;
    this.s3Url = '';
    this.fileCategory = '';
    this.columns = [];
    this.preview = [];
    this.clearMessages();
    this.uploadProgress = 0;
  }
}
import { Component, OnInit } from '@angular/core';
import { KnowledgeBaseService, KBStats, QualityMetrics } from '@services/knowledge-base.service';
import { Observable } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';

interface ProcessingStatus {
  status: 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
}

interface DistributionItem {
  label: string;
  value: number;
  percentage: number;
}

@Component({
  selector: 'app-kb-manager',
  templateUrl: './kb-manager.component.html',
  styleUrls: ['./kb-manager.component.scss'],
  standalone: false
})
export class KBManagerComponent implements OnInit {
  kbStats$: Observable<KBStats | null>;
  processingStatus: { [key: string]: ProcessingStatus } = {};
  qualityMetrics: QualityMetrics | null = null;
  selectedFiles: File[] = [];
  urls: string[] = [];
  Object = Object; // Make Object available in template
  
  constructor(
    private kbService: KnowledgeBaseService,
    private snackBar: MatSnackBar
  ) {
    this.kbStats$ = this.kbService.getKBStats();
  }

  ngOnInit() {
    this.loadInitialStats();
  }

  async loadInitialStats() {
    try {
      await this.kbService.refreshStats();
      this.qualityMetrics = await this.kbService.assessQuality();
    } catch (error) {
      this.showError('Error loading KB stats');
    }
  }

  onFileSelected(event: Event) {
    const element = event.target as HTMLInputElement;
    const fileList = element.files;
    if (fileList) {
      this.selectedFiles = Array.from(fileList);
      this.showSuccess(`${this.selectedFiles.length} files selected`);
    }
  }

  onUrlAdded(url: string) {
    if (url.trim()) {
      this.urls.push(url);
      this.showSuccess('URL added successfully');
    }
  }

  async processDocuments() {
    if (this.selectedFiles.length === 0 && this.urls.length === 0) {
      this.showError('Please select files or add URLs to process');
      return;
    }

    // Process files
    for (const file of this.selectedFiles) {
      this.processingStatus[file.name] = { status: 'processing', progress: 0 };
      try {
        await this.kbService.addDocument(file, (progress: number) => {
          if (this.processingStatus[file.name]) {
            this.processingStatus[file.name].progress = progress;
          }
        });
        this.processingStatus[file.name].status = 'completed';
        this.showSuccess(`Processed ${file.name} successfully`);
      } catch (error) {
        this.processingStatus[file.name].status = 'error';
        this.processingStatus[file.name].error = error instanceof Error ? error.message : 'Unknown error';
        this.showError(`Error processing ${file.name}`);
      }
    }

    // Process URLs
    for (const url of this.urls) {
      this.processingStatus[url] = { status: 'processing', progress: 0 };
      try {
        await this.kbService.addDocumentFromUrl(url, (progress: number) => {
          if (this.processingStatus[url]) {
            this.processingStatus[url].progress = progress;
          }
        });
        this.processingStatus[url].status = 'completed';
        this.showSuccess(`Processed ${url} successfully`);
      } catch (error) {
        this.processingStatus[url].status = 'error';
        this.processingStatus[url].error = error instanceof Error ? error.message : 'Unknown error';
        this.showError(`Error processing ${url}`);
      }
    }

    // Refresh stats and quality metrics
    await this.kbService.refreshStats();
    this.qualityMetrics = await this.kbService.assessQuality();
  }

  removeUrl(url: string) {
    this.urls = this.urls.filter(u => u !== url);
    this.showSuccess('URL removed');
  }

  clearFiles() {
    this.selectedFiles = [];
    this.showSuccess('Files cleared');
  }

  getScoreColor(score: number): string {
    if (score >= 0.8) return '#4CAF50';  // Green
    if (score >= 0.6) return '#2196F3';  // Blue
    if (score >= 0.4) return '#FFC107';  // Yellow
    if (score >= 0.2) return '#FF9800';  // Orange
    return '#f44336';  // Red
  }

  getDistributionItems(distribution: Record<string, number>): DistributionItem[] {
    if (!distribution) return [];
    
    const total = Object.values(distribution).reduce((sum, val) => sum + val, 0);
    return Object.entries(distribution).map(([label, value]) => ({
      label,
      value,
      percentage: (value / total) * 100
    }));
  }

  private showSuccess(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['error-snackbar']
    });
  }
}
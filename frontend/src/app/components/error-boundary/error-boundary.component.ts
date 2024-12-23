import { Component, ErrorHandler, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-error-boundary',
  template: `
    <ng-container *ngIf="!hasError; else errorTemplate">
      <ng-content></ng-content>
    </ng-container>
    <ng-template #errorTemplate>
      <div class="error-placeholder">
        <p>Snap! Something went wrong. We'll be right back!</p>
      </div>
    </ng-template>
  `,
  styles: [
    `
      .error-placeholder {
        text-align: center;
        color: #f44336;
        font-size: 18px;
        margin-top: 20px;
      }
    `
  ],
 standalone: false
})

export class ErrorBoundaryComponent implements ErrorHandler {
  @Input() fallbackMessage = 'Something went wrong.';
  hasError = false;

  handleError(error: any): void {
    console.error('Component Error:', error);
    this.hasError = true;
  }
}

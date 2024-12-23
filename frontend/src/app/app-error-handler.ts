import { ErrorHandler, Injectable } from '@angular/core';

@Injectable()
export class AppErrorHandler implements ErrorHandler {
  handleError(error: any): void {
    console.error('Global Error Handler:', error);
    // Optionally, log errors to an external service
  }
}

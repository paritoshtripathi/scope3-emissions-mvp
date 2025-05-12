import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          if (!this.isRefreshing) {
            this.isRefreshing = true;
            
            return this.authService.refreshToken().pipe(
              switchMap(() => {
                this.isRefreshing = false;
                const token = localStorage.getItem('token');
                if (token) {
                  request = request.clone({
                    setHeaders: {
                      Authorization: `Bearer ${token}`
                    }
                  });
                }
                return next.handle(request);
              }),
              catchError((refreshError) => {
                this.isRefreshing = false;
                this.authService.logout();
                this.router.navigate(['/auth/login']);
                return throwError(() => refreshError);
              })
            );
          }
        }
        return throwError(() => error);
      })
    );
  }
}
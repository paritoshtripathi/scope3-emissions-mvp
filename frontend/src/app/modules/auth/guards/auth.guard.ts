import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    if (this.authService.isAuthenticated()) {
      // Check for required roles
      const requiredRoles = route.data['roles'] as Array<string>;
      if (requiredRoles) {
        const hasRole = requiredRoles.some(role => this.authService.hasRole(role));
        if (!hasRole) {
          this.router.navigate(['/dashboard']);
          return false;
        }
      }
      
      // Check for required permissions
      const requiredPermissions = route.data['permissions'] as Array<string>;
      if (requiredPermissions) {
        const hasPermission = requiredPermissions.every(permission => 
          this.authService.hasPermission(permission)
        );
        if (!hasPermission) {
          this.router.navigate(['/dashboard']);
          return false;
        }
      }

      return true;
    }

    this.router.navigate(['/auth/login'], { queryParams: { returnUrl: state.url }});
    return false;
  }
}
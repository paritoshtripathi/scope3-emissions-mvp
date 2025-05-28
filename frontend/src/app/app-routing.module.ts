import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { KBManagerComponent } from './components/kb-manager/kb-manager.component';
import { MasterLayoutComponent } from '@components/master-layout/master-layout.component';

const routes: Routes = [
  {
    path: '',
    component: MasterLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
      },
      {
        path: 'home',
        loadChildren: () => import('./modules/home/home.module').then(m => m.HomeModule)
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./modules/dashboard/dashboard.module').then(m => m.DashboardModule)
      },
      {
        path: 'emissions',
        loadChildren: () => import('./modules/emissions/emissions.module').then(m => m.EmissionsModule)
      },
      {
        path: 'analytics',
        loadChildren: () => import('./modules/analytics/analytics.module').then(m => m.AnalyticsModule)
      },
      {
        path: 'data-upload',
        loadChildren: () => import('./modules/data-upload/data-upload.module').then(m => m.DataUploadModule)
      },
      {
        path: 'settings',
        loadChildren: () => import('./modules/settings/settings.module').then(m => m.SettingsModule)
      },
      {
        path: 'kb-manager',
        component: KBManagerComponent
      }
    ]
  },
  {
    path: 'auth',
    loadChildren: () => import('./modules/auth/auth.module').then(m => m.AuthModule)
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MasterLayoutComponent } from '@components/master-layout/master-layout.component';

const routes: Routes = [
  {
    path: '',
    
    children: [
      //{ path: 'home', loadChildren: () => import('@modules/home/home.module').then(m => m.HomeModule) },
      { path: 'dashboard', loadChildren: () => import('@modules/dashboard/dashboard.module').then(m => m.DashboardModule) }
      //{ path: 'emissions', loadChildren: () => import('@modules/emissions/emissions.module').then(m => m.EmissionsModule) },
      //{ path: 'analytics', loadChildren: () => import('@modules/analytics/analytics.module').then(m => m.AnalyticsModule) },
      //{ path: 'settings', loadChildren: () => import('@modules/settings/settings.module').then(m => m.SettingsModule) }
    ]
  }
  //{ path: '', redirectTo: 'home' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}

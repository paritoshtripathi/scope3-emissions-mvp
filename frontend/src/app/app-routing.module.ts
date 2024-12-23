import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MasterLayoutComponent } from '@components/master-layout/master-layout.component';
import { HomeComponent } from '@components/home/home.component';
import { EmissionsComponent } from '@components/emissions/emissions.component';
import { AnalyticsComponent } from '@components/analytics/analytics.component';
import { SettingsComponent } from '@components/settings/settings.component';
import { DashboardComponent } from '@components/dashboard/dashboard.component';

const routes: Routes = [
  {
    path: '',
    component: MasterLayoutComponent,
    children: [
      { path: 'home', component: HomeComponent },
      { path: 'emissions', component: EmissionsComponent },
      { path: 'analytics', component: AnalyticsComponent },
      { path: 'settings', component: SettingsComponent },
      { path: 'dashboard', component: DashboardComponent },
      { path: '**', redirectTo: 'home', pathMatch: 'full' }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}

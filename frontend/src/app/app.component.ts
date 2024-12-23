import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DashboardComponent } from '@components/dashboard/dashboard.component'; // Adjust the import path as needed

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html', // Use external HTML file
  styleUrls: ['./app.component.scss'], // Include styles
  standalone: false
})
export class AppComponent implements OnInit {
  backendData: number[] = [];

 
  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Existing functionality to fetch data from the backend
    // this.http.get<any>('http://localhost:3000/api/sample').subscribe({
    //   next: (response) => {
    //     this.backendData = response.data;
    //   },
    //   error: (error) => {
    //     console.error('Error fetching data from backend', error);
    //   },
    //   complete: () => {
    //     console.log('Request complete');
    //   }
    // });
  }

   // Add a ViewChild reference to access the DashboardComponent
   //@ViewChild(DashboardComponent, { static: true }) dashboard!: DashboardComponent;

}

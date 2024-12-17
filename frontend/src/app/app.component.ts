import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

// @Component({
//   selector: 'app-root',
//   template: `
//     <div>
//       <h1>Data from Backend (Sample API):</h1>
//       <ul>
//         <li *ngFor="let item of backendData">{{ item }}</li>
//       </ul>
//       <hr />

//       <app-prediction></app-prediction> <!-- Embed the Prediction Component -->
//     </div>
//     <div class="app-container">
//     <!-- Your existing content -->
//       <app-chat></app-chat> <!-- Chat overlay component -->
//     </div>
//   `
// })
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html', // Use external HTML file
  styleUrls: ['./app.component.scss'] // Include styles
})

export class AppComponent implements OnInit {
  backendData: number[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<any>('http://localhost:3000/api/sample').subscribe({
      next: (response) => {
        this.backendData = response.data;
      },
      error: (error) => {
        console.error('Error fetching data from backend', error);
      },
      complete: () => {
        console.log('Request complete');
      }
    });
  }
}

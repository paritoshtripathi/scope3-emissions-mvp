
import { Component } from '@angular/core';

@Component({
  selector: 'app-master-layout',
  templateUrl: './master-layout.component.html',
  styleUrls: ['./master-layout.component.scss'],
  standalone:false
})
export class MasterLayoutComponent {
  ngOnInit(): void {
    console.log('Master layout initialized');
  }
}


import { Component } from '@angular/core';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrl: './toolbar.component.scss',
  standalone: false
})
export class ToolbarComponent {
  ngOnInit(): void {
    console.log('Toolbar initialized');
  }

}

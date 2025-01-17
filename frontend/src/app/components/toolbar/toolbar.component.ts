import { Component } from '@angular/core';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss'],
  standalone: false
})
export class ToolbarComponent {
  triggerWalkthrough(): void {
    const walkthroughEvent = new CustomEvent('startWalkthrough');
    window.dispatchEvent(walkthroughEvent);
  }
}

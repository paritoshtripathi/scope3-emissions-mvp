
import { Component, ViewChild } from '@angular/core';
import { AvatarComponent } from '@components/avatar/avatar.component';

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

  @ViewChild(AvatarComponent) avatarComponent!: AvatarComponent;

  reinitiateWalkthrough(): void {
    if (this.avatarComponent) {
      this.avatarComponent.reinitiateWalkthrough();
    }
  }

}


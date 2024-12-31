import { Component, OnInit } from '@angular/core';
import { AvatarService } from '@services/avatar.service';


@Component({
  selector: 'app-avatar',
  templateUrl: './avatar.component.html',
  styleUrls: ['./avatar.component.scss']
})
export class AvatarComponent implements OnInit {
  walkthroughActive = false;
  currentStepIndex = 0;
  steps: { title: string; description: string }[] = [];
  avatarImage = 'assets/avatar.png';

  constructor(private avatarService: AvatarService) {}

  ngOnInit(): void {
    this.loadWalkthroughSteps();
  }

  loadWalkthroughSteps(): void {
    this.avatarService.getWalkthroughSteps().subscribe(
      (steps) => {
        this.steps = steps;
        this.currentStepIndex = 0;
      },
      (error) => {
        console.error('Failed to load walkthrough steps', error);
      }
    );
  }

  toggleChat(): void {
    this.walkthroughActive = !this.walkthroughActive;
  }

  nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.currentStepIndex++;
    } else {
      this.completeWalkthrough();
    }
  }

  skipWalkthrough(): void {
    this.walkthroughActive = false;
  }

  completeWalkthrough(): void {
    this.walkthroughActive = false;
    console.log('Walkthrough complete');
  }

  get currentStep(): { title: string; description: string } {
    return this.steps[this.currentStepIndex];
  }

  isLastStep(): boolean {
    return this.currentStepIndex === this.steps.length - 1;
  }
}

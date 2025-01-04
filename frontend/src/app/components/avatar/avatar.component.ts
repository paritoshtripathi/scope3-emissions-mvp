import { Component, OnInit, OnDestroy } from '@angular/core';
import { AvatarService } from '@services/avatar.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-avatar',
  templateUrl: './avatar.component.html',
  styleUrls: ['./avatar.component.scss'],
  standalone: false
})
export class AvatarComponent implements OnInit, OnDestroy {
  walkthroughActive = true;
  isChatMode = false;
  avatarImage = '../assets/icons/avatar1.png';
  currentStepIndex = 0;
  steps: any[] = [];
  messages: { user: string; text: string }[] = [];
  userMessage = '';
  private subscriptions: Subscription = new Subscription();

  constructor(private avatarService: AvatarService) {}

  ngOnInit(): void {
    this.loadWalkthroughSteps();

    // Listen for toolbar event
    window.addEventListener('startWalkthrough', this.reinitiateWalkthrough.bind(this));
  }

  ngOnDestroy(): void {
    // Clean up event listeners to prevent memory leaks
    window.removeEventListener('startWalkthrough', this.reinitiateWalkthrough.bind(this));
    this.subscriptions.unsubscribe();
  }

  /**
   * Load walkthrough steps by fetching insights and generating explanations.
   */
  loadWalkthroughSteps(): void {
    const subscription = this.avatarService.getInsights().subscribe({
      next: (insights: any[]) => {
        const generatedSteps: any[] = [];
        const explanationSubscriptions: Subscription[] = [];

        insights.forEach((item) => {
          const explanationSubscription = this.avatarService
            .generateExplanation({
              category: item.category,
              emissions: item.total_emissions,
              reduction: item.total_reduction
            })
            .subscribe({
              next: (response) => {
                generatedSteps.push({
                  title: `Insight on ${item.category}`,
                  description: response // AI-generated explanation
                });

                // Sort steps to maintain order
                if (generatedSteps.length === insights.length) {
                  this.steps = [
                    { title: 'Welcome aboard!', description: this.generateWelcomeText() },
                    ...generatedSteps
                  ];
                }
              },
              error: (error) => {
                console.log('Generating explanation prompt:', insights);
                console.error(`Failed to generate explanation for ${item.category}:`, error);
              }
            });

          explanationSubscriptions.push(explanationSubscription);
        });

        // Add all explanation subscriptions to the main Subscription object
        explanationSubscriptions.forEach((sub) => this.subscriptions.add(sub));
      },
      error: (error) => {
        console.error('Failed to load insights:', error);
        this.steps = [
          { title: 'Error', description: 'Failed to load insights. Please try again later.' }
        ];
      },
      complete: () => {
        console.log('Walkthrough steps loaded successfully.');
      }
    });

    this.subscriptions.add(subscription);
  }

  /**
   * Generate welcome text for the first walkthrough step.
   */
  generateWelcomeText(): string {
    return `Welcome! I'm Avatar, your maritime expert for Scope 3 emissions. Let’s explore actionable insights to reduce emissions effectively.`;
  }

  nextStep(): void {
    if (this.steps.length === 0) {
      console.error('No steps available to move to the next step.');
      return;
    }

    if (this.currentStepIndex < this.steps.length - 1) {
      this.currentStepIndex+=1;
    } else {
      console.log('No more steps available.');
    }
  }

  startWalkthrough(): void {
    this.walkthroughActive = true;
  }

  endWalkthrough(): void {
    this.walkthroughActive = false;
  }

  toggleChatMode(): void {
    this.isChatMode = !this.isChatMode;
  }

  sendMessage(): void {
    this.messages.push({ user: 'User', text: this.userMessage });

    const observer = {
      next: (insights: any[]) => {
        const response = insights.find((insight) =>
          this.userMessage.includes(insight.title)
        );
        const botResponse = response
          ? response.description
          : "I'm sorry, I couldn't understand your query.";
        this.messages.push({ user: 'Bot', text: botResponse });
      },
      error: (error: any) => {
        console.error('Failed to fetch chat insights:', error);
        this.messages.push({ user: 'Bot', text: 'An error occurred while processing your query.' });
      },
      complete: () => {
        console.log('Chat response processing complete.');
      }
    };

    const subscription = this.avatarService.getInsights().subscribe(observer);
    this.subscriptions.add(subscription);

    this.userMessage = '';
  }

  get currentStep(): any {
    return this.steps[this.currentStepIndex];
  }

  isLastStep(): boolean {
    return this.currentStepIndex === this.steps.length - 1;
  }

  reinitiateWalkthrough(): void {
    this.walkthroughActive = true; // Activate walkthrough mode
    this.isChatMode = false; // Hide chat mode
    this.currentStepIndex = 0; // Reset steps
    this.loadWalkthroughSteps(); // Fetch steps again (optional)
  }
}

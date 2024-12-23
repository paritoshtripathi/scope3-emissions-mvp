import { ComponentFixture, TestBed } from '@angular/core/testing';
import { VisualizationSectionComponent } from './visualization-section.component';

describe('VisualizationSectionComponent', () => {
  let component: VisualizationSectionComponent;
  let fixture: ComponentFixture<VisualizationSectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VisualizationSectionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VisualizationSectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

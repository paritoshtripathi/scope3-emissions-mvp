import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmissionsComponent } from './emissions.component';

describe('EmissionsComponent', () => {
  let component: EmissionsComponent;
  let fixture: ComponentFixture<EmissionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmissionsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EmissionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

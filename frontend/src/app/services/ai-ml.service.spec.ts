import { TestBed } from '@angular/core/testing';

import { AiMlService } from './ai-ml.service';

describe('AiMlService', () => {
  let service: AiMlService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AiMlService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

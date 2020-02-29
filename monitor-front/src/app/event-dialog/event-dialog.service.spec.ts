import { TestBed } from '@angular/core/testing';

import { EventDialogService } from './event-dialog.service';

describe('EventDialogService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: EventDialogService = TestBed.get(EventDialogService);
    expect(service).toBeTruthy();
  });
});

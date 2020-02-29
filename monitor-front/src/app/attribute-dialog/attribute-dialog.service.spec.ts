import { TestBed } from '@angular/core/testing';

import { AttributeDialogService } from './attribute-dialog.service';

describe('AttributeDialogService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: AttributeDialogService = TestBed.get(AttributeDialogService);
    expect(service).toBeTruthy();
  });
});

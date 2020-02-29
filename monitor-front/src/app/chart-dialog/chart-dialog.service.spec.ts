import { TestBed } from '@angular/core/testing';

import { ChartDialogService } from './chart-dialog.service';

describe('ChartDialogService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ChartDialogService = TestBed.get(ChartDialogService);
    expect(service).toBeTruthy();
  });
});

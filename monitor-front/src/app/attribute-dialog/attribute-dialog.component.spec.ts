import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AttributeDialogComponent } from './attribute-dialog.component';

describe('AttributeDialogComponent', () => {
  let component: AttributeDialogComponent;
  let fixture: ComponentFixture<AttributeDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AttributeDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AttributeDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { FormGroup, FormControl, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';
import { EventDialogService } from './event-dialog.service';
import { Component, Inject, OnInit } from '@angular/core';

@Component({
  selector: 'app-event-dialog',
  templateUrl: './event-dialog.component.html',
  styleUrls: ['./event-dialog.component.css']
})
export class EventDialogComponent implements OnInit {


    eventForm = new FormGroup({
        nameControl: new FormControl('', [Validators.required]),
        streamControl: new FormControl(''),
        startControl: new FormControl(''),
        endControl: new FormControl('')
    });


    name;
    start;
    end;


    constructor(@Inject(MAT_DIALOG_DATA) public data: any, private dialogRef: MatDialogRef<EventDialogComponent>, private eventDialogService: EventDialogService) { }


    ngOnInit() {

        this.name = this.data.name;
        this.start = this.data.start;
        this.end = this.data.end;

    }


    submitEvent() {

        var eventName = this.eventForm.get('nameControl').value;
        var streamName = this.name;
        var start = this.start;
        var end = this.end;

        let success = this.eventDialogService.submitEventData(eventName, streamName, start, end).then(success => {
            this.dialogRef.close();
        });

    }

    close() {
        this.dialogRef.close();
    }

}

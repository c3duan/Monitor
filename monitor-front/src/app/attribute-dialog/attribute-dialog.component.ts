import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AttributeDialogService } from './attribute-dialog.service';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';
import { Component, Inject, OnInit } from '@angular/core';

@Component({
  selector: 'app-attribute-dialog',
  templateUrl: './attribute-dialog.component.html',
  styleUrls: ['./attribute-dialog.component.css']
})
export class AttributeDialogComponent implements OnInit {


    attributeForm = new FormGroup({
        streamControl: new FormControl(''),
        attributeControl: new FormControl('', [Validators.required]),
        valueControl: new FormControl('', [Validators.required])
    });


    stream;
    attribute;
    value;


    constructor(@Inject(MAT_DIALOG_DATA) public data: any, private dialogRef: MatDialogRef<AttributeDialogComponent>, private attributeDialogService: AttributeDialogService) { }


    ngOnInit() {

        this.stream = this.data.stream;
        this.attribute = this.data.attribute;
        this.value = this.data.value;

        this.attributeForm.setValue({
            streamControl: this.stream,
            attributeControl: this.attribute,
            valueControl: this.value
        });

    }


    closeDialog() {
        this.dialogRef.close();
    }


    submitAttribute() {

        var streamName = this.attributeForm.get('streamControl').value;
        var attributeName = this.attributeForm.get('attributeControl').value;
        var valueName = this.attributeForm.get('valueControl').value;

        this.attributeDialogService.deleteAttributeData(streamName, attributeName, valueName).then(success => {
        });
        this.attributeDialogService.submitAttributeData(streamName, attributeName, valueName).then(success_2 => {
            this.dialogRef.close();
        });

    }


    deleteAttribute() {

        var streamName = this.attributeForm.get('streamControl').value;
        var attributeName = this.attributeForm.get('attributeControl').value;
        var valueName = this.attributeForm.get('valueControl').value;

        this.attributeDialogService.deleteAttributeData(streamName, attributeName, valueName).then(success => {
            this.dialogRef.close();
        });

    }

}

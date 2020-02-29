import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, startWith } from 'rxjs/operators';
import { FormService } from './form.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {


    attributeForm = new FormGroup({
        attributeControl: new FormControl('', [Validators.required]),
        textControl: new FormControl('', [Validators.required]),
        operatorControl: new FormControl('', [Validators.required]),
        valueControl: new FormControl('', [Validators.required])
    });


	filteredAttributes: Observable<string[]>;
    filteredOperators: Observable<string[]>;
	attributes: string[];	
    operators: string[];
	attributesExist;
    duplicateText;


	constructor(private http: HttpClient, private formService: FormService) { }


	ngOnInit() {

        this.operators = [ '>', '<', '>=', '<=', '=' ];
        this.filterOperatorsInit();

		this.attributesExist = true;
        this.duplicateText = false;
		this.attributes = null;
		this.getAttributes();

	}

    
	getAttributes() {

		this.formService.getAttributes(this);

	}


	filterAttributesInit() {
		this.filteredAttributes = this.attributeForm.get('attributeControl').valueChanges.pipe(
			startWith(''),
			map(value => this.filterAttribute(value))
		);
	}


	filterOperatorsInit() {
		this.filteredOperators = this.attributeForm.get('operatorControl').valueChanges.pipe(
			startWith(''),
			map(value => this.filterOperator(value))
		);
	}


	filterAttribute(value: string): string[] {
		const filterValue = value.toLowerCase();
		return this.attributes.filter(attribute => attribute.toLowerCase().includes(filterValue));
	}


	filterOperator(value: string): string[] {
		const filterValue = value.toLowerCase();
		return this.operators.filter(operator => operator.toLowerCase().includes(filterValue));
	}


    submitAttribute() {

        var attribute = this.attributeForm.get('attributeControl').value;
        var text = this.attributeForm.get('textControl').value;
        var operator = this.attributeForm.get('operatorControl').value;
        var value = this.attributeForm.get('valueControl').value;

        this.formService.saveAttribute(attribute, text, operator, value).then(success => {

            if (success) {

                this.duplicateText = false;
                this.attributeForm.reset();

                for(let i in this.attributeForm.controls) {
                    this.attributeForm.controls[i].setErrors(null);
                }

                this.getAttributes();

            } else {

                this.duplicateText = true;                 
                this.attributeForm.get('textControl').reset();

            }

        });

    }

}

import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable'
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';

@Injectable()
export class FormService {

	constructor(private http: HttpClient) {}

	getAttributes(formComponent): void {
        var url = GlobVars.baseUrl + ':3000/api/attributes/';
		this.http.get(url).subscribe(rows => {
			var data = [];
			for (var row_index in rows) {
				data.push(rows[row_index]['attribute']);
			}
			formComponent.attributes = data;
			formComponent.attributes_exist = true;
			formComponent.filterAttributesInit();
		});
	}

    async saveAttribute(attribute, text, operator, value): Promise<{}> {

        var url = GlobVars.baseUrl + ':3000/api/saveAlias/';
        let promise = new Promise((resolve, reject) => {

            this.http.post(url, {

                'formData': {
                    'attribute': attribute,
                    'text': text,
                    'operator': operator,
                    'value': value
                }

            })
            .toPromise()
            .then(success => { 
                resolve(success); 
            });

        });

        return promise;

    }

}

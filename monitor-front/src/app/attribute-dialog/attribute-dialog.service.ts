import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';

@Injectable({ providedIn: 'root' })
export class AttributeDialogService {


    constructor(private http: HttpClient) { }


    async submitAttributeData(streamName, attributeName, valueName): Promise<{}> {
        var url = GlobVars.baseUrl + ':3000/api/submitAttribute';
        return new Promise((resolve, reject) => {
            this.http.post(url, {
                'attributeData': {
                    'streamName': streamName,
                    'attributeName': attributeName,
                    'valueName': valueName
                }
            })
            .toPromise()
            .then(success => {
                resolve(success);
            });
        });
    }


    async deleteAttributeData(streamName, attributeName, valueName): Promise<{}> {
        var url = GlobVars.baseUrl + ':3000/api/deleteAttribute';
        return new Promise((resolve, reject) => {
            this.http.post(url, {
                'attributeData': {
                    'streamName': streamName,
                    'attributeName': attributeName,
                    'valueName': valueName
                }
            })
            .toPromise()
            .then(success => {
                resolve(success);
            });
        });
    }


}

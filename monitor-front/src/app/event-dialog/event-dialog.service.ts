import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';

@Injectable({ providedIn: 'root' })
export class EventDialogService {


    constructor(private http: HttpClient) { }

 
    async submitEventData(eventName, streamName, start, end): Promise<{}> {
        var url = GlobVars.baseUrl + ':3000/api/saveEvent';
        return new Promise((resolve, reject) => {
            this.http.post(url, {
                'eventData':  {
                    'event': eventName,
                    'stream': streamName,
                    'start': start,
                    'end': end
                }
            })
            .toPromise()
            .then(success => {
                resolve(success);
            });
        });
    }


}

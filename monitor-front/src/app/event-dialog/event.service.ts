import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class EventService {


    constructor(private http: HttpClient) { }

 
    async submitEventData(eventName, streamName, start, end, isAniyama): Promise<{}> {
        var url = GlobVars.baseUrl + ':3000/api/saveEvent';
        return new Promise((resolve, reject) => {
            this.http.post(url, {
                'eventData':  {
                    'event': eventName,
                    'stream': streamName,
                    'start': start,
                    'end': end,
                    'isAniyama': isAniyama
                }
            })
            .toPromise()
            .then(success => {
                resolve(success);
            });
        });
    }

    getEventData(): Observable<any> {
        var url = GlobVars.baseUrl + ':3000/api/event';
        return this.http.get(url);
    }


}

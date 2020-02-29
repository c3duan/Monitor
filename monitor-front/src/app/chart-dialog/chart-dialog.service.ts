import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';

@Injectable({ providedIn: 'root' })
export class ChartDialogService {


    constructor(private http: HttpClient) { }

    getChartAttributes(name): Promise<{}> {

        var url = GlobVars.baseUrl + ':3000/api/attributes_by_stream/' + name

        return new Promise((resolve, reject) => {
            this.http.get(url).subscribe(rows => {
                for (var row_index in rows) {
                    resolve(rows);
                }
            });
        });

    }
}

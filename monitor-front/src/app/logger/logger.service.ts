import { Injectable } from '@angular/core';
import { NGXLogger, CustomNGXLoggerService, NgxLoggerLevel } from 'ngx-logger';
import { startTimeRange } from '@angular/core/src/profile/wtf_impl';

@Injectable({
  providedIn: 'root'
})
export class LoggerService {

  private logger: NGXLogger;
  constructor(customLogger: CustomNGXLoggerService) {
    this.logger = customLogger.create({
      level: NgxLoggerLevel.INFO,
      disableConsoleLogging: false,
      serverLogLevel: NgxLoggerLevel.INFO,
      enableSourceMaps: true,
      timestampFormat: 'medium'
    });
  }

  log(param: any) {
    this.logger.info(param);
  }

  logToCsvFile(data: any) {
    let rows = this.mapDataToArray(data);
    let filename = `${rows[0].stream}_${rows[0].start}_${rows[0].end}_${(new Date()).toLocaleString()}.csv`;
    this.exportToCsv(filename, rows.slice(1));
  }

  mapDataToArray(data: any) {
    let rows = [];
    for(let i = 0; i < data.length; i++) {
      for(let j = 0; j < data[i].streams.length; j++) {
        rows.push({
          stream: data[i].streams[j].stream,
          start: data[i].start[j],
          end: data[i].end[j],
          match: data[i].streams[j].match,
        });
      }
    }
    return rows;
  }

  exportToCsv(filename: string, rows: object[]) {
    if (!rows || !rows.length) {
      return;
    }
    const separator = ',';
    const keys = Object.keys(rows[0]);
    const csvContent =
      keys.join(separator) +
      '\n' +
      rows.map(row => {
        return keys.map(k => {
          let cell = row[k] === null || row[k] === undefined ? 'unknown' : row[k];
          cell = cell instanceof Date
            ? cell.toLocaleString()
            : cell.toString().replace(/"/g, '""');
          if (cell.search(/("|,|\n)/g) >= 0) {
            cell = `"${cell}"`;
          }
          return cell;
        }).join(separator);
      }).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
      navigator.msSaveBlob(blob, filename);
    } else {
      const link = document.createElement('a');
      if (link.download !== undefined) {
        // Browsers that support HTML5 download attribute
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  }
}

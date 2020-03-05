import { Injectable } from '@angular/core';
import { NGXLogger, CustomNGXLoggerService, NgxLoggerLevel } from 'ngx-logger';

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
}

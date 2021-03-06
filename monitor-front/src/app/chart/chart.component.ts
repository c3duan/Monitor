import { MatTabChangeEvent, MatDialogConfig, MatDialog } from '@angular/material';
import { ChartDialogComponent } from '../chart-dialog/chart-dialog.component';
import { EventDialogComponent } from '../event-dialog/event-dialog.component';
import { Component, OnInit, ViewChild } from '@angular/core';
import { ChartService } from './chart.service';
import { LoggerService } from '../logger/logger.service';
import { EventService } from '../event-dialog/event.service';
import { SwiperComponent, SwiperConfigInterface, SwiperPaginationInterface, SwiperNavigationInterface, SwiperScrollbarInterface } from 'ngx-swiper-wrapper';

@Component({
	selector: 'app-chart',
	templateUrl: './chart.component.html',
	styleUrls: ['./chart.component.css'],
})
export class ChartComponent implements OnInit {
    @ViewChild(SwiperComponent) componentRef?: SwiperComponent;

    all_groups: any[];
    vis_groups: any[];
    isEvent: boolean;
    isEval: boolean;
    no_results: boolean;
    waiting: boolean;
    pages: number[];
    events = [];

    navigation: SwiperNavigationInterface = {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    };
    
    pagination: SwiperPaginationInterface = {
        el: '.swiper-pagination',
        type: 'fraction'
    };

    scrollbar: SwiperScrollbarInterface = {
        el: '.swiper-scrollbar',
        hide: false,
        draggable: true
    };

    config: SwiperConfigInterface = {
        a11y: true,
        direction: 'horizontal',
        slidesPerView: 1,
        spaceBetween: 30,
        simulateTouch: false,
        keyboard: true,
        scrollbar: this.scrollbar,
        navigation: this.navigation,
        pagination: this.pagination
    };

    
    constructor(
        private chartService: ChartService, 
        private loggerService: LoggerService,
        private eventService: EventService,
        private dialog: MatDialog) { }


	ngOnInit() { 

        this.no_results = false;
        this.all_groups = null;
        this.vis_groups = null;
        this.isEvent = false;
        this.isEval = false;
        this.waiting = false;
        this.pages = null;
        this.eventService.getEventData().subscribe(rows => {
            for (var row_index in rows) {
                this.events.push(rows[row_index]['event']);
            }
        });
    }

    saveToCsvFile() {
        if (this.all_groups) {
            this.loggerService.logToCsvFile(this.all_groups);
        }
    }

	search(query) {

        if (this.all_groups) {
            this.loggerService.log(this.all_groups);
        }

        this.all_groups = null;
        this.vis_groups = null;
        this.waiting = true;
        this.pages = null;
        
        let translated = this.chartService.translateQuery(query).then(translated => {
            var query = translated['newQuery'];

            if (query.includes('event')) {
                this.isEvent = true;
            } else {
                this.isEvent = false;
            }

            if (query.includes('eval')) {
                this.isEval = true;
            } else {
                this.isEval = false;
            }

            this.chartService.search(query, this);
        });

	}


	getChart(event: MatTabChangeEvent, group_name) {
        var stream = event.tab.textLabel;
        if (this.isEval) {
            this.chartService.getChartDataEval(stream, group_name, stream, this);
        } else {
            this.chartService.getChartData(stream, stream, this);
        }
	}

    resetCharts(): void {

        if (this.isEvent) {
            for (var row_index = 0; row_index <= 1; row_index++) {
                this.getEventChart(row_index);
            }
        } else {
            for (var row in this.vis_groups) {
                var name = this.vis_groups[row]['streams'][0].stream;
                if (this.isEval) {
                    var type = this.vis_groups[row]['group_name'];
                    this.chartService.getChartDataEval(name, type, name, this);
                } else {
                    this.chartService.getChartData(name, name, this);
                }
            }
        }

        this.waiting = false;

    }

    onIndexChange(index: number) {
        this.getEventChart(index + 1);
    }

    getEventChart(index: number) {
        var name = this.all_groups[index]['streams'][0].stream;
        var start = this.all_groups[index]['start'][0];
        var end = this.all_groups[index]['end'][0];
        this.chartService.getChartDataEvent(name, name, start, end, this);
    }


	getPage(page) {
        this.vis_groups = this.all_groups[page];
		this.resetCharts();
	}


    openDialog(display: boolean, group) {
        const dialogConfig = new MatDialogConfig();

        dialogConfig.height = "800px";
        dialogConfig.width = "1500px";
        dialogConfig.data = { 
            'name': group.group_name,
            'value': group.group_val,
            'streams': group.streams,
            'isEval': this.isEval,
            'groupName': group.group_name,
            'showMatch': this.isEvent && display,
            'start': group.start,
            'end': group.end
        };

        this.dialog.open(ChartDialogComponent, dialogConfig);

    }

    openCurrentEventDialog(stream) {
        const { start, end } = this.chartService.getEventRange(stream);

        this.openEventDialog(stream, start, end)
    }

    openEventDialog(name, start, end) {
        const dialogConfig = new MatDialogConfig();
        // dialogConfig.height = "600px";
        // dialogConfig.width = "400px";
        dialogConfig.data = {
            'name': name,
            'start': start,
            'end': end,
            'events': this.events
        }
        dialogConfig.disableClose = true;

        let dialogRef = this.dialog.open(EventDialogComponent, dialogConfig);
        dialogRef.afterClosed().subscribe(result => {
            this.chartService.onFinishedEventSelect(name);
        });
    }

    onRadioChange(event, stream) {
        stream.match = event.value;
    }

}

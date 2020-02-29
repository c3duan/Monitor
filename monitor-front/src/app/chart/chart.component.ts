import { MatTabChangeEvent, MatDialogConfig, MatDialog } from '@angular/material';
import { ChartDialogComponent } from '../chart-dialog/chart-dialog.component';
import { EventDialogComponent } from '../event-dialog/event-dialog.component';
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ChartService } from './chart.service';

@Component({
	selector: 'app-chart',
	templateUrl: './chart.component.html',
	styleUrls: ['./chart.component.css'],
})
export class ChartComponent implements OnInit {


    all_groups;
    vis_groups;
    no_results;
    waiting;
    pages;


	constructor(private http: HttpClient, private chartService: ChartService, private dialog: MatDialog) { }


	ngOnInit() { 

        this.no_results = false;
        this.all_groups = null;
        this.vis_groups = null;
        this.waiting = false;
        this.pages = null;

	}


	search(query) {

        this.all_groups = null;
        this.vis_groups = null;
        this.waiting = true;
        this.pages = null;
        
        let translated = this.chartService.translateQuery(query).then(translated => {
            var query = translated['newQuery'];
            this.chartService.search(query, this);
        });

	}


	getChart(event: MatTabChangeEvent) {

		var stream = event.tab.textLabel;
        this.chartService.getChartData(stream, stream, this);
	}


    resetCharts(): void {
        for (var row_index in this.vis_groups) {

            var name = this.vis_groups[row_index]['streams'][0];
            if (this.vis_groups[row_index]['start'] === null) {
                this.chartService.getChartData(name, name, this);
            } else {
                var start = this.vis_groups[row_index]['start'][0];
                var end = this.vis_groups[row_index]['end'][0];
                this.chartService.getChartDataEvent(name, name, start, end, this);
            }

        }

        this.waiting = false;

    }


	getPage(page) {

		this.vis_groups = this.all_groups[page];
		this.resetCharts();

	}


    openDialog(group) {

        const dialogConfig = new MatDialogConfig();

        dialogConfig.height = "800px";
        dialogConfig.width = "1500px";
        dialogConfig.data = { 
            'name': group.group_name,
            'value': group.group_val,
            'streams': group.streams,
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
            'end': end
        }
        dialogConfig.disableClose = true;

        this.dialog.open(EventDialogComponent, dialogConfig);
    }

}

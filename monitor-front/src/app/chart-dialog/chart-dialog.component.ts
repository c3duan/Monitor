import { MAT_DIALOG_DATA, MatTabChangeEvent, MatDialogConfig, MatDialog } from '@angular/material';
import { AttributeDialogComponent } from '../attribute-dialog/attribute-dialog.component';
import { EventDialogComponent } from '../event-dialog/event-dialog.component';
import { ChartDialogService } from './chart-dialog.service';
import { Component, Inject, OnInit } from '@angular/core';
import { ChartService } from '../chart/chart.service';

@Component({
  selector: 'app-chart-dialog',
  templateUrl: './chart-dialog.component.html',
  styleUrls: ['./chart-dialog.component.css']
})
export class ChartDialogComponent implements OnInit {

    name;
    value;
    streams;
    events;
    stream;
    groupName;
    isAniyama;
    showMatch;
    checked;
    starts;
    ends;
    atts;


    constructor(
        @Inject(MAT_DIALOG_DATA) public data: any, 
        private chartDialogService: ChartDialogService, 
        private chartService: ChartService,
        private dialog: MatDialog
    ) { }


    ngOnInit() {

        this.name = this.data.name;
        this.value = this.data.value;
        this.streams = this.data.streams;
        this.events = this.data.events;
        this.stream = this.streams[0].stream;
        this.groupName = this.data.groupName;
        this.isAniyama = this.data.isAniyama;
        this.showMatch = this.data.showMatch;
        this.checked = this.data.checked;
        this.starts = this.data.start;
        this.ends = this.data.end;
        this.atts = [];
        var stream_label = this.stream + '_dialog';

        if (!this.isAniyama) {
            let attributes = this.chartDialogService.getChartAttributes(this.stream).then(attributes => {
                for (var att_index in attributes) {
                    this.atts.push({
                        'stream': this.stream,
                        'attribute': attributes[att_index]['attribute'],
                        'value': attributes[att_index]['value']
                    });
                }
            });
    
            if (this.starts === null) {
                this.chartService.getChartData(this.stream, stream_label, this, { height: 400, xaxis: { nticks: 25 } });
            } else {
                var start = this.starts[0];
                var end = this.ends[0];
                this.chartService.getChartDataEvent(this.stream, stream_label, start, end, this, { height: 400 });
            }
        } else {
            this.chartService.getChartDataAniyama(this.stream, this.groupName, stream_label, this, { height: 500 });
        }

    }


	get_chart(event: MatTabChangeEvent) {

		this.stream = event.tab.textLabel;
        var stream_label = this.stream + '_dialog';

        if (!this.isAniyama) {
            this.atts = [];
            let attributes = this.chartDialogService.getChartAttributes(this.stream).then(attributes => {
                for (var att_index in attributes) {
                    this.atts.push({
                        'stream': this.stream,
                        'attribute': attributes[att_index]['attribute'],
                        'value': attributes[att_index]['value']
                    });
                }
            });

            this.chartService.getChartData(this.stream, stream_label, this);
        } else {
            this.chartService.getChartDataAniyama(this.stream, this.groupName, stream_label, this, { height: 500 });
        }

	}


    newAttributeDialog() {

        const dialogConfig = new MatDialogConfig();

        dialogConfig.height = "600px";
        dialogConfig.width = "400px";
        dialogConfig.data = {
            'stream': this.stream,
            'attribute': null,
            'value': null 
        };

        this.dialog.open(AttributeDialogComponent, dialogConfig)
        .afterClosed().subscribe(result => {
            this.atts = [];
            let attributes = this.chartDialogService.getChartAttributes(this.stream).then(attributes => {
                for (var att_index in attributes) {
                    this.atts.push({
                        'stream': this.stream,
                        'attribute': attributes[att_index]['attribute'],
                        'value': attributes[att_index]['value']
                    });
                }
            });
        });

    }


    openAttributeDialog(att) {

        const dialogConfig = new MatDialogConfig();

        dialogConfig.height = "600px";
        dialogConfig.width = "400px";
        dialogConfig.data = {
            'stream': att.stream,
            'attribute': att.attribute,
            'value': att.value
        };

        this.dialog.open(AttributeDialogComponent, dialogConfig)
        .afterClosed().subscribe(result => {
            this.atts = [];
            let attributes = this.chartDialogService.getChartAttributes(this.stream).then(attributes => {
                for (var att_index in attributes) {
                    this.atts.push({
                        'stream': this.stream,
                        'attribute': attributes[att_index]['attribute'],
                        'value': attributes[att_index]['value']
                    });
                }
            });
        });

    }

    openCurrentEventDialog(stream) {
        var stream = stream.substring(0, stream.length-7);
        const { start, end } = this.chartService.getEventRange(stream);

        this.openEventDialog(stream, start, end)
    }

    openEventDialog(name, start, end) {
        const dialogConfig = new MatDialogConfig();
        dialogConfig.height = "600px";
        dialogConfig.width = "400px";
        dialogConfig.data = {
            'name': name,
            'start': start,
            'end': end,
            'events': this.events,
            'isAniyama': this.isAniyama
        }
        dialogConfig.disableClose = true;

        let dialogRef = this.dialog.open(EventDialogComponent, dialogConfig);
        dialogRef.afterClosed().subscribe(result => {
            this.chartService.onFinishedEventSelect(name + '_dialog');
        });
    }

    onRadioChange(event, stream) {
        stream.value = event.value;
    }
}

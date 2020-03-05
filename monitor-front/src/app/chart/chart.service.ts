import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable'
import { Injectable } from '@angular/core';
import { GlobVars } from '../global';
import { stringify } from 'querystring';

@Injectable()
export class ChartService {


	default_config = {
		modeBarButtons: [
			['toImage'],
			['sendDataToCloud'],
			['zoom2d'],
			['pan2d'],
			['select2d'],
			['zoomIn2d'],
			['zoomOut2d'],
			['autoScale2d'],
			['resetScale2d'],
			['toggleSpikelines'],
			['hoverClosestCartesian'],
			['hoverCompareCartesian']
		]
	};

	default_layout = { 
		shapes: [],
		height: 300,
		selectdirection: 'h',
		dragmode: 'select',
		xaxis: { nticks: 10, automargin: true },
		yaxis: { automargin: true },
		plot_bgcolor: '#ffffff',
		paper_bgcolor: '#ffffff',
		margin: { l: -10, r: -10, t: 30, pad: 2 }
	};

	charts = {}

	constructor(private http: HttpClient) {}


    async translateQuery(query): Promise<{}> {

        var url = GlobVars.baseUrl + ':3000/api/translateQuery/' + query;

        return new Promise((resolve, reject) => {
            this.http.get(url).subscribe(rows => {
               resolve(rows); 
            });
        });

    }


    search(query, chartComponent): void {

        var url = GlobVars.baseUrl + ':3000/api/search/' + query;
        this.http.get(url).subscribe(rows => {

            var data_size = Object.keys(rows).length;
            var page_data = [];
            var all_data = [];
            var count = 1;

            for (var row_index in rows) {

                page_data.push({
                    'group_name': rows[row_index]['group_name'],
                    'group_val': rows[row_index]['group_val'],
                    'streams': this.mapStreams(rows[row_index]['streams']),
                    'start': 'start' in rows[row_index] ? rows[row_index]['start'] : null,
                    'end': 'end' in rows[row_index] ? rows[row_index]['end'] : null
                });

                if ((count % 10 === 0 && count > 0) || count > data_size-1) {
                    all_data.push(page_data);
                    page_data = [];
                    if (count >= 100) { break }
                }

                count += 1

            }

            chartComponent.all_groups = all_data;
			chartComponent.vis_groups = all_data[0];
			chartComponent.pages = Array.apply(null, {length: all_data.length}).map(Number.call, Number);
			chartComponent.no_results = all_data.length > 0 ? false : true;
			this.charts = {}; // reset all cached layouts and configs
            chartComponent.resetCharts();

        });
	}

	mapStreams(streams) {
		return streams.map(stream => {
			return {
				'stream': stream,
				'checked': false
			};
		})
	}

	getShape(start, end) {
		return {
			type: 'rect',
			// x-reference is assigned to the x-values
			xref: 'x',
			// y-reference is assigned to the plot paper [0,1]
			yref: 'paper',
			x0: start,
			y0: 0,
			x1: end,
			y1: 1,
			fillcolor: '#d3d3d3',
			opacity: 0.5,
			line: {
				width: 0
			}
		};
	}

	drawPlot(id: string, rows: any, chartComponent, start?, end?, layout?, config?) {
		var x = []; 
		var y = [];

		for (var row_index in rows) {
			x.push(new Date(rows[row_index]['timestamp'] * 1000).toLocaleString());
			y.push(rows[row_index]['value']);
		}

		x = x.reverse();
		y = y.reverse();
		
		if (!(id in this.charts)) {
			this.charts[id] = { 
				layout: JSON.parse(JSON.stringify(this.default_layout)),
				config: JSON.parse(JSON.stringify(this.default_config))
			};
		}

		if (layout) {
			const new_layout = Object.assign(this.charts[id].layout, layout);
			this.charts[id].layout = new_layout;
		}

		if (config) {
			const new_config = Object.assign(this.charts[id].config, config);
			this.charts[id].config = new_config;
		}

		if (start && end) {
			start = new Date(start * 1000).toLocaleString();
			end = new Date(end * 1000).toLocaleString();
			const shape = this.getShape(start, end);
			this.charts[id].layout.shapes.push(shape);
		}

		Plotly.newPlot(
			id, 
			[{ 'x': x, 'y': y }], 
			this.charts[id].layout, 
			this.charts[id].config
		);

		var plotDiv: any = document.getElementById(id);
		plotDiv.on('plotly_selected', (eventData) => {
			const start = eventData.range.x[0];
			const end = eventData.range.x[1];
			this.onSelected(id, start, end, this.charts[id].layout, chartComponent);
		});
	}

	onSelected(id, start, end, layout, chartComponent): void {
		const shape = this.getShape(start, end);
		layout.shapes.push(shape);
		const key = `shapes[${layout.shapes.length-1}]`;
		Plotly.relayout(id, { key: shape })

		if (id.search('dialog') !== -1) {
			id = id.substring(0, id.length-7);
		}
		chartComponent.openEventDialog(id, start, end);
	}


    getChartData(name, id, chartComponent, layout?, config?): void {
        var url = GlobVars.baseUrl + ':3000/api/name/' + name
		this.http.get(url).subscribe(rows => {
			this.drawPlot(id, rows, chartComponent, null, null, layout, config);
		});
	}

    getChartDataEvent(name, id, start, end, chartComponent, layout?, config?): void {

        var url = GlobVars.baseUrl + ':3000/api/selection'
        this.http.post(url, {
            'selectionData' : {
                'stream': name,
                'start': start,
                'end': end
            }
        }).subscribe(rows => {
			this.drawPlot(id, rows, chartComponent, start, end, layout, config);
		});

		// var url = GlobVars.baseUrl + ':3000/api/name/' + name
		// this.http.get(url).subscribe(rows => {
		// 	this.drawPlot(id, rows, chartComponent, start, end, layout, config);
		// });
	}

	getEventRange(stream) {
        var plotDiv: any = document.getElementById(stream);
        var ix1 = parseInt(plotDiv.layout['xaxis']['range'][0]);
        var ix2 = parseInt(plotDiv.layout['xaxis']['range'][1]);
        var xvals = plotDiv.data[0]['x'];

        ix1 = ix1 >= 0 ? ix1 : 0;
        ix2 = ix2 >= 0 ? ix2 : 0;
        ix1 = ix1 <= xvals.length-1 ? ix1 : xvals.length-1;
        ix2 = ix2 <= xvals.length-1 ? ix2 : xvals.length-1;
        
        var start = xvals[ix1];
        var end = xvals[ix2];

        console.log(plotDiv);

        return { start, end }
    }

}

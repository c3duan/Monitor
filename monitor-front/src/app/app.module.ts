import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';

import { AttributeDialogComponent } from './attribute-dialog/attribute-dialog.component';
import { ChartDialogComponent } from './chart-dialog/chart-dialog.component';
import { EventDialogComponent } from './event-dialog/event-dialog.component';
import { ChartComponent } from './chart/chart.component';
import { FormComponent } from './form/form.component';
import { ChartService } from './chart/chart.service';
import { FormService } from './form/form.service';
import { AppComponent } from './app.component';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input'
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatToolbarModule, MatSidenavModule, MatListModule, MatRadioModule } from '@angular/material';
import { SwiperModule, SwiperConfigInterface, SWIPER_CONFIG } from 'ngx-swiper-wrapper';
import { HelpComponent } from './help/help.component';
import { LoggerModule } from 'ngx-logger';

const DEFAULT_SWIPER_CONFIG: SwiperConfigInterface = {
	direction: 'horizontal',
	slidesPerView: 'auto'
  };


@NgModule({
	declarations: [
		AttributeDialogComponent,
		ChartDialogComponent,
		EventDialogComponent,
		ChartComponent,
		FormComponent,
		AppComponent,
		HelpComponent,
	],
	imports: [
        MatProgressSpinnerModule,
		BrowserAnimationsModule,
		MatAutocompleteModule,
		ReactiveFormsModule,
		MatFormFieldModule,
		HttpClientModule,
		MatSelectModule,
        MatButtonModule,
        MatDialogModule,
		MatInputModule,
        MatChipsModule,
		BrowserModule,
		MatTabsModule,
		MatIconModule,
		FormsModule,
		DragDropModule,
		MatRadioModule,
		MatToolbarModule,
		MatSidenavModule,
		MatListModule,
		SwiperModule,
		LoggerModule
	],
	providers: [
		ChartService,
		FormService,
		{
			provide: SWIPER_CONFIG,
			useValue: DEFAULT_SWIPER_CONFIG
		}
	],
    bootstrap: [ AppComponent ],
    entryComponents: [ 
        AttributeDialogComponent,
        ChartDialogComponent,
        EventDialogComponent
    ]
})
export class AppModule { }

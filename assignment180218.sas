/*
 * Exam: Forecasting the Airline Passengers Time Series
 * Student: Adrian Florea
 * Date: February 18th, 2018
 */

data work.Air1990_2000;
	set LWFETSP.usairlines
       (where=(date<='31DEC2000'd));
run;

/*
 * Exercise 1
 */

proc timeseries 
	/* input data */
	data=work.Air1990_2000 
	
	/*
	 * output data
	 * containing decomposed and/or seasonally adjusted time series
	 */
	outdecomp=work.outdecomp 
	plots=
	(
		/* time series */ series 
		/* trend component */ tc 
		/* seasonal component */ sc
		/* autocorrelation function */ acf
		/* seasonal decomposition/adjustment panel */ decomp
	);
	/* date is the time id variable with a monthly accumulation frequency */
	id date interval=month;
	/* passengers is the variable to analyze*/
	var passengers;
run;

data work.outdecomp;
	/* take the observations for years greater than 1998 */
	set work.outdecomp (where=(year(date)>=1998));
run;

/*
 * it results from the plot that: 
 * - the highest travel month is August
 * - the lowest travel month is February
 */
proc sgplot 
	data=work.outdecomp; 
	series x=Date y=SC; 
	/* add a refline at 1 on Oy */
	refline 1;
run;

/*
 * Exercise 2
 */

proc spectra 
	data=work.Air1990_2000 
	out=work.exercise2 
	/* spectral density estimates */
	s; 
	/* passengers is the variable to analyze */
	var passengers;
	/* smoothing with the Parzen kernel */
	weights parzen; 
run;

proc sgplot data=work.exercise2;
	series x=period y=s_01;
	/* reflines added after the plot to show the best seasonal periods */
	refline 2.4 / axis=x;
	refline 4 / axis=x;
	refline 12 / axis=x;
	where period < 20 and period > 2;
run;

/*
 * Exercise 3
 */

/*
 * add candidate trend and seasonal terms to the data
 * 
 * Answers:
 * - 24 forecasting periods are extrapolated from the input
 * - 11 dummies are created for months (MON1-MON11)
 * - variable Time is created as a time index
 */
data work.Air1990_2000;
	set work.Air1990_2000 end=lastobs;
	array Seas{*} MON1-MON11;
	retain TwoPi . Time 0 MON1-MON11 .;
	
	if (TwoPi=.) then TwoPi=2*constant("pi");
	if (MON1=.) then
	do index=1 to 11;
		Seas[index]=0;
	end;
	Time+1;
	S2p4=sin(TwoPi*Time/2.4);
	C2p4=cos(TwoPi*Time/2.4);
	S4=sin(TwoPi*Time/4);
	C4=cos(TwoPi*Time/4);
	S12=sin(TwoPi*Time/12);
	C12=cos(TwoPi*Time/12);

	if (month(Date)<12) then
	do;
		Seas[month(Date)]=1;
		output;
		Seas[month(Date)]=0;
	end;
	else output;
	if (lastobs) then
	do;
		Passengers=.;
		do index=1 to 24;
			Time+1;
			Date=intnx("month", Date, 1);
			S2p4=sin(TwoPi*Time/2.4);
			C2p4=cos(TwoPi*Time/2.4);
			S4=sin(TwoPi*Time/4);
			C4=cos(TwoPi*Time/4);
			S12=sin(TwoPi*Time/12);
			C12=cos(TwoPi*Time/12);
			if (month(Date)<12) then
			do;
				Seas[month(Date)]=1;
				output;
				Seas[month(Date)]=0;
			end;
			else output;
		end;
	end;
	drop index TwoPi;
run;

/*
 * Exercise 4
 */

/* results an acceptable fit but with a more complex error component*/
proc arima 
	data=work.Air1990_2000;
	identify var=passengers(1 12) noprint;
	estimate q=(1)(12) method=ml;
	/* forecast 24 months */
	forecast id=date interval=month lead=24;
run;

/* results a better fit, better white noise */
proc arima 
	data=work.Air1990_2000;
	identify var=passengers(1 12) noprint;
	/* added p=1 */
	estimate p=1 q=(1)(12) method=ml;
	/* forecast 24 months */
	forecast id=date interval=month lead=24;
run;

/*
 * Exercise 5
 */

/* ARMA model with linear trend and seasonal dummies */
proc arima 
	data=work.Air1990_2000;
	identify var=passengers cross=(Time MON1 MON2 MON3 MON4 MON5 MON6 MON7 MON8 MON9 MON10 MON11) noprint;
	estimate input=(Time MON1 MON2 MON3 MON4 MON5 MON6 MON7 MON8 MON9 MON10 MON11) ml;
run;

/* ARMA(0,0,1) with linear trend and seasonal dummies, forecasted on 24 months */
proc arima 
	data=work.Air1990_2000;
	identify var=passengers cross=(Time MON1 MON2 MON3 MON4 MON5 MON6 MON7 MON8 MON9 MON10 MON11) noprint;
	estimate input=(Time MON1 MON2 MON3 MON4 MON5 MON6 MON7 MON8 MON9 MON10 MON11) p=1 ml;
	forecast id=date interval=month lead=24;
run;

/*
 * Exercise 6
 */

%AutoESM(work.Air1990_2000, work.exercise6, passengers, date);

proc sort 
	data=work.exercise6;
	by mape;
run;

proc print 
	data=work.exercise6 noobs;
	var model aic sbc rmse mape smape;
run;

proc esm data=work.Air1990_2000 outfor=work.addwinters lead=24 print=(statistics summary estimates) plot=(forecasts corr);
	id date interval=month;
	forecast passengers / model=addwinters;
	where (date<='31dec2000'd);
run;
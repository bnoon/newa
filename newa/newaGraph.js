/*global $ */
function ymdToUTC(x) {
	var ymd = x.split("-");
	while (ymd.length < 3) {
		ymd.push(1);
	}
	return Date.UTC(ymd[0], ymd[1] - 1, ymd[2], 0);
}

function defineGraphOptions(options) {
	var yaxisCnt = options && options.yaxisCnt ? options.yaxisCnt : 1,
		darkColor = "darkblue",
		medColor = "#3baae3",
		ltColor = "#aed0ea",
		yaxis_array = [{
			title: {
				style: {
					color: darkColor
				}
			},
			lineColor: medColor,
			gridLineColor: ltColor,
			gridLineWidth: 1,
			gridLineDashStyle: "shortdash",
			minorGridLineWidth: 1,
			minorGridLineDashStyle: "dot",
			minorTickInterval: "auto",
			minorTickWidth: 1,
			showFirstLabel: true,
			showLastLabel: true,
			labels: {
				align: "right",
				x: -5,
				y: -5,
				rotation: 270,
				style: {
					color: darkColor
				}
			}
		}, {
			title: {
				style: {
					color: darkColor
				}
			},
			lineColor: medColor,
			gridLineWidth: 0,
			minorGridLineWidth: 0,
			minorTickInterval: "auto",
			minorTickWidth: 1,
			showFirstLabel: true,
			showLastLabel: true,
			labels: {
				align: "left",
				x: 5,
				y: -5,
				rotation: 90,
				style: {
					color: darkColor
				}
			},
			opposite: true
		}];
	return {
		chart: {
			zoomType: "x",
			borderWidth: 0,
			borderColor: medColor,
			spacingBottom: 20,
			width: 600
		},
		title: {
			style: {
					fontSize: "15px",
				color: darkColor
			}
		},
		subtitle: {
			style: {
				color: medColor
			}
		},
		credits: {
			text: "Powered by ACIS",
			href: "http://www.rcc-acis.org",
			style: {
				color: medColor
			}
		},
		exporting: {
			enabled: false
		},
		legend: {
			enabled: true,
			borderColor: medColor,
			reversed: false,
			itemStyle: {
				color: darkColor
			}
		},
		tooltip: {
			enabled: true,
			shared: true,
			headerFormat: '<b>{point.key}<\/b><br \/>'
		},
		xAxis: {
			type: "datetime",
			dateTimeLabelFormats: {
				hour: "%b %e -",
				day: "%b %e",
				week: "%b %e",
				month: "%b %Y"
			},
			minRange: 8 * 24 * 3600000,	// eight days
			lineColor: medColor,
			gridLineColor: ltColor,
			gridLineWidth: 1,
			gridLineDashStyle: "shortdash",
			startOnTick: false,
			endOnTick: false,
			labels: {
				style: {
					color: darkColor
				}
			}
		},
		yAxis: yaxisCnt === 1 ? yaxis_array[0] : yaxis_array,
		plotOptions: {
			line: {
				marker: {
					enabled: false,
					symbol: "diamond",
					states: {
						hover: {
							enabled: true,
							radius: 4
						}
					}
				}
			},
			arearange: {
				fillOpacity: 0.5,
				lineWidth: 0
			},
			column: {
				grouping: false,
				pointPadding: 0.1,
				borderWidth: 0
			},
			scatter: {
				marker: {
					symbol: "diamond"
				},
				tooltip: {
					dateTimeLabelFormats: "%m-%d",
					xDateFormat: "%m-%d"
				},
				dataLabels: {
					enabled: true,
					color: 'black',
					zIndex: 5,
					x: 15,
					y: 20
				}
			},
			columnrange: {
				grouping: false,
				pointPadding: 0.1,
				borderWidth: 0
			}
		},
		series: []
	};
}

function produce_tp_graph(params, obs_dict) {
	var date_val, d,
		data_series = [[], []],
		graphOptions = defineGraphOptions({'yaxisCnt': 2});
	for (d = 0; d < obs_dict.obs_days.length; d += 1) {
		date_val = ymdToUTC(obs_dict.obs_days[d]);
		if (obs_dict.maxt[d] !== -999 && obs_dict.mint[d] !== -999) {
			data_series[0].push([date_val, obs_dict.mint[d], obs_dict.maxt[d]]);
		} else {
			data_series[0].push([date_val, null, null]);
		}
		if (obs_dict.prcp[d] !== -999) {
			data_series[1].push([date_val, Math.round(obs_dict.prcp[d]*100)/100]);
		} else {
			data_series[1].push([date_val, null]);
		}
	}
	if (obs_dict.frobs_days.length) {
		data_series.push([], []);
		for (d = 0; d < obs_dict.frobs_days.length; d += 1) {
			date_val = ymdToUTC(obs_dict.frobs_days[d]);
			if (obs_dict.fmaxt[d] !== -999 && obs_dict.fmint[d] !== -999) {
				data_series[2].push([date_val, obs_dict.fmint[d], obs_dict.fmaxt[d]]);
			} else {
				data_series[2].push([date_val, null, null]);
			}
			if (obs_dict.fprcp[d] !== -999) {
				data_series[3].push([date_val, Math.round(obs_dict.fprcp[d]*100)/100]);
			} else {
				data_series[3].push([date_val, null]);
			}
		}
	}
	graphOptions.series.push({
		data: data_series[0],
		color: 'blue',
		name: 'Daily lowest and highest hourly temperatures',
		type: 'columnrange',
		zIndex: 3,
		turboThreshold: data_series[0].length
	}, {
		data: data_series[1],
		color: '#328332',
		name: 'Daily precipitation',
		type: 'column',
		yAxis: 1,
		zIndex: 2,
		turboThreshold: data_series[1].length
	});
	if (obs_dict.frobs_days.length) {
		graphOptions.series.push({
			data: data_series[2],
			color: 'brown',
			name: 'Forecast lowest and highest hourly temperatures',
			type: 'columnrange',
			zIndex: 3,
			turboThreshold: data_series[2].length
		}, {
			data: data_series[3],
			color: 'orange',
			name: 'Forecast precipitation',
			type: 'column',
			yAxis: 1,
			zIndex: 2,
			turboThreshold: data_series[3].length
		});
	}
	$.extend(graphOptions.chart, {
		height: 400,
		spacingTop: 0
	});
	$.extend(graphOptions.title, {
		text: null
	});
	$.extend(graphOptions.credits, {
		enabled: false
	});
	$.extend(graphOptions.yAxis[0].title, {
		text: "Temperature (F)"
	});
	$.extend(graphOptions.yAxis[1].title, {
		text: "Precipitation (inches)"
	});
	$.extend(graphOptions.xAxis, {
		opposite: true,
		labels: { y: -10 }
	});
	$.extend(graphOptions.yAxis[1], {
		max: 4
	});
	$.extend(graphOptions.xAxis, {
		plotLines: [{value: ymdToUTC(params.biofix), color: "green", dashStyle: "dash", width: 2, zIndex: 1}]
	});
	$.extend(graphOptions.tooltip, {
		formatter: function () {
			var tts = "<b>" + Highcharts.dateFormat('%A, %B %e, %Y', this.x) + "<\/b>";
			$.each(this.points, function (i, point) {
				if (point.series.tooltipOptions.pointFormat.length) {
					tts += '<br \/><span style="color:' + point.series.color + ';">' + point.series.name + ': ' +
						(point.series.name.search("precipitation") >= 0 ? (point.y + ' inches') : 
						(point.point.low + ' F to ' + point.point.high + ' F')) + '<\/span>';
				}
			});
			return tts;
		}
	});
	$("#tp_chart_area").highcharts(graphOptions);
}

function produce_applescab_graph(params, obs_dict, ascospore_dict) {
	var date_val, d, hi_error, lo_error,
		data_series = [[], []],
		biofixYMD = params.biofix.split('-'),
		graphOptions = defineGraphOptions({'yaxisCnt': 2});
	data_series[0].push([ymdToUTC(obs_dict.obs_days[0]), null]);
	for (d = 0; d < ascospore_dict.dates.length; d += 1) {
		date_val = ymdToUTC(ascospore_dict.dates[d]);
		if (ascospore_dict.maturity[d] !== -999) {
			data_series[0].push([date_val, Math.round(ascospore_dict.maturity[d])]);
			if (ascospore_dict.maturity[d] >= 95 && data_series.length === 2) {
				data_series.push([[date_val, parseInt(ascospore_dict.maturity[d], 10)]]);
			}
		} else {
			data_series[0].push([date_val, null]);
		}
		if (ascospore_dict.maturity[d] !== -999 && ascospore_dict.error[d] !== -999) {
			lo_error = Math.max(0.0, ascospore_dict.maturity[d] - ascospore_dict.error[d]);
			hi_error = Math.min(100.0, ascospore_dict.maturity[d] + ascospore_dict.error[d]);
			data_series[1].push([date_val, Math.round(lo_error), Math.round(hi_error)]);
		} else {
			data_series[1].push([date_val, null, null]);
		}
	}
	graphOptions.series.push({
		data: data_series[0],
		color: 'red',
		name: 'Ascospore Maturity',
		type: 'line',
		zIndex: 3,
		turboThreshold: data_series[0].length
	}, {
		data: data_series[1],
		color: 'pink',
		name: 'Uncertainty',
		type: 'arearange',
		yAxis: 1,
		zIndex: 2,
		turboThreshold: data_series[1].length
	});
	if (data_series.length === 3) {
		graphOptions.series.push({
			data: data_series[2],
			color: 'black',
			name: 'Ascospore 95%',
			type: 'scatter',
			tooltip: { valueSuffix: "%" },
			dataLabels: { format: '{y}%' },
			zIndex: 4
		});
	}
	$.extend(graphOptions.chart, {
		height: 200,
		spacingBottom: 5
	});
	$.extend(graphOptions.credits, {
		enabled: false
	});
	$.extend(graphOptions.legend, {
		enabled: false
	});
	$.extend(graphOptions.title, {
		text: "Ascospore Maturity and Weather Summary for " + params.station_name
	});
	$.extend(graphOptions.subtitle, {
		text: params.biofix_name + ' date (' + parseInt(biofixYMD[1], 10) + '/' + parseInt(biofixYMD[2], 10) +
			') is indicated by a dashed green line'
	});
	$.extend(graphOptions.yAxis[0].title, {
		text: "Ascospore Maturity (%)"
	});
	$.extend(graphOptions.yAxis[1].title, {
		text: "Ascospore Maturity (%)"
	});
	$.extend(graphOptions.yAxis[0], {
		max: 100,
		min: 0,
		plotLines: [{value: 95, color: "red", dashStyle: "dash", width: 1, zIndex: 4}]
	});
	$.extend(graphOptions.yAxis[1], {
		max: 100,
		min: 0
	});
	$.extend(graphOptions.xAxis, {
		labels: { enabled: false },
		plotLines: [{value: ymdToUTC(params.biofix), color: "green", dashStyle: "dash", width: 2, zIndex: 1}]
	});
	$.extend(graphOptions.tooltip, {
		formatter: function () {
			var tts = "<b>" + Highcharts.dateFormat('%A, %B %e, %Y', this.x) + "<\/b>";
			$.each(this.points, function (i, point) {
				if (point.series.tooltipOptions.pointFormat.length) {
					tts += '<br \/><span style="color:' + point.series.color + ';">' + point.series.name + ': ' +
						(point.series.name.search("Maturity") >= 0 ? (point.y + ' percent') : 
						(point.point.low + ' percent to ' + point.point.high + ' percent')) + '<\/span>';
				}
			});
			return tts;
		}
	});

	$("#dis_chart_area").highcharts(graphOptions);
	if (data_series.length === 3) {
		$('<div id="message_area" style="width:430;border:1px solid red;margin:0 80px;padding:5px;font-size:90%;"><\/div>').insertAfter("#dis_chart_area");
		$("#message_area").html("The Ascospore Maturity model predicts that 95% of the spores are matured. At this point, essentially all ascospores will be released after a daytime rain of greater than 0.10 inch with temperatures above 50 deg F.");
	}
	produce_tp_graph(params, obs_dict);
}

function produce_fireblight_graph(params, obs_dict, deghr_dict) {
	var date_val, d, i, color,
		data_series = [],
		biofixYMD = params.biofix.split('-'),
		graphOptions = defineGraphOptions({'yaxisCnt': 2}),
		orchard_history = params.orchard_history,
		orchard_choices = {
			1: 'No fire blight in your neighborhood last year',
			2: 'Fire blight occurred in your neighborhood last year',
			3: 'Fire blight is now active in your neighborhood'
		},
		risk_thresholds = {
			1: [0, 300, 500, 800],
			2: [0, 150, 300, 500],
			3: [0, 100, 200, 300]
		},
		risk_colors = {
			0: "green",
			1: "gold",
			2: "orange",
			3: "red"
		};
	data_series.push([ymdToUTC(obs_dict.obs_days[0]), null]);
	for (d = 0; d < deghr_dict.dates.length; d += 1) {
		date_val = ymdToUTC(deghr_dict.dates[d]);
		if (deghr_dict.d4dh[d] !== -999) {
			color = "red";
			for (i = 1; i <= 3; i += 1) {
				if (deghr_dict.d4dh[d] < risk_thresholds[orchard_history][i]) {
					color = risk_colors[i - 1];
					break;
				}
			}
			data_series.push({x: date_val, y: deghr_dict.d4dh[d], color: color});
		} else {
			data_series.push({x: date_val, y: null, color: null});
		}
	}
	graphOptions.series.push({
		data: data_series,
		name: '4-Day Degree Hour Sum',
		type: 'column',
		zIndex: 3,
		turboThreshold: data_series.length
	});
	$.extend(graphOptions.chart, {
		height: 200,
		spacingBottom: 5
	});
	$.extend(graphOptions.credits, {
		enabled: false
	});
	$.extend(graphOptions.legend, {
		enabled: false
	});
	$.extend(graphOptions.title, {
		text: "CougarBlight Risk and Weather Summary for " + params.station_name
	});
	$.extend(graphOptions.subtitle, {
		text: params.biofix_name + ' date (' + parseInt(biofixYMD[1], 10) + '/' + parseInt(biofixYMD[2], 10) +
			') is indicated by a dashed green line.'
	});
	$.extend(graphOptions.yAxis[0].title, {
		text: "4-Day Degree Hour Sum"
	});
	$.extend(graphOptions.yAxis[1].title, {
		text: "4-Day Degree Hour Sum"
	});
	$.extend(graphOptions.yAxis[0].labels, {
		format: "{value:.0f}"
	});
	$.extend(graphOptions.yAxis[1].labels, {
		format: "{value:.0f}"
	});
	$.extend(graphOptions.yAxis[0], {
		max: 1000,
		min: 0,
		plotLines: [
			{value: risk_thresholds[orchard_history][3], label: {text: "Extreme", style: {color: risk_colors[3]}}, color: risk_colors[3], dashStyle: "solid", width: 2, zIndex: 2},
			{value: risk_thresholds[orchard_history][2], label: {text: "High", style: {color: risk_colors[2]}}, color: risk_colors[2], dashStyle: "solid", width: 2, zIndex: 2},
			{value: risk_thresholds[orchard_history][1], label: {text: "Caution", style: {color: risk_colors[1]}}, color: risk_colors[1], dashStyle: "solid", width: 2, zIndex: 2},
			{value: risk_thresholds[orchard_history][0], label: {text: "Low", style: {color: risk_colors[0]}}, color: risk_colors[0], dashStyle: "solid", width: 2, zIndex: 2}
		]
	});
	$.extend(graphOptions.yAxis[1], {
		max: 1000,
		min: 0
	});
	$.extend(graphOptions.xAxis, {
		labels: { enabled: false },
		plotLines: [{value: ymdToUTC(params.biofix), color: "green", dashStyle: "dash", width: 2, zIndex: 1}]
	});
	$("#dis_chart_area").highcharts(graphOptions);
	produce_tp_graph(params, obs_dict);
	$("#tp_chart_area").append("<p style='width:600; margin:0; text-align:center; font-size:90%; font-style:italic;'>First three days after blossom open date are partial accumulations." +
		"<br \/>Orchard history = " + orchard_history + " (" + orchard_choices[orchard_history] + ").<\/p>");
}

function produce_cabbagemaggot_graph() {
	var date_val, d, ymd, lastvalue,
		data_series = [],
		degday_dict = {},
		se = 288,
		se25 = 366,
		se50 = 452,
		se75 = 547,
		se95 = 697,
		f1 = 809,
		f2 = f1+915,
		f3 = f2+838,
		f4 = f3+718,
		plotlines = [
			{value: se, label: {text: "Spring Emergence", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se50, label: {style: {color: "darkred"}}, color: "red", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: f1, label: {text: "First Generation", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se50 + f1, label: {style: {color: "red", fontSize:'80%'}}, color: "red", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: f2, label: {text: "Second Generation", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se50 + f2, label: {style: {color: "red", fontSize:'80%'}}, color: "red", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: f3, label: {text: "Third Generation", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se50 + f3, label: {style: {color: "red", fontSize:'80%'}}, color: "red", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: f4, label: {text: "Fourth Generation", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3}
		],
		emergencelines = [
			{value: se25, label: {text: "25% Emergence", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se75, label: {text: "75% Emergence", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3},
			{value: se95, label: {text: "95% Emergence", style: {color: "darkblue"}}, color: "darkblue", dashStyle: "ShortDot", width: 1, zIndex: 3}
		],
		graphOptions = defineGraphOptions({'yaxisCnt': 1});
		
	if ($("#dd_dict").text().length) {
		degday_dict = $.parseJSON($("#dd_dict").text().replace(/\(/g, "[").replace(/\)/g, "]"));
		lastvalue = degday_dict[degday_dict.length-1][4];
		for (d = 0; d < degday_dict.length; d += 1) {
			ymd = degday_dict[d][0]
			date_val = Date.UTC(ymd[0], ymd[1] - 1, ymd[2], 0)
			if (degday_dict[d][4] !== -999) {
				data_series.push([date_val, degday_dict[d][4]]);
			} else {
				data_series.push([date_val, null]);
			}
		}
		graphOptions.series.push({
			data: data_series,
			color: 'black',
			name: 'Accumulated Degree-Days',
			type: 'line',
			zIndex: 4,
			turboThreshold: data_series.length
		});
		$.extend(graphOptions.chart, {
			height: 250,
			width: 620,
			spacingBottom: 5
		});
		$.extend(graphOptions.credits, {
			enabled: false
		});
		$.extend(graphOptions.legend, {
			enabled: false
		});
		$.extend(graphOptions.title, {
			text: "Accumulated Cabbage Maggot Degree-Days (Base 40&deg;F)",
			useHTML: true
		});
		$.extend(graphOptions.title.style, {
			fontSize: "13px"
		});
		$.extend(graphOptions.xAxis, {
			gridZIndex: 2
		});
		$.extend(graphOptions.xAxis.dateTimeLabelFormats, {
			hour: "%b %e -",
			day: "%b %e",
			week: "%b %e",
			month: "%b %e"
		});
		$.extend(graphOptions.yAxis.labels, {
			formatter: function () {
				 return Highcharts.numberFormat(this.value, 0);
			}
		});
		$.extend(graphOptions.yAxis.title, {
			text: "Accumulated Degree-Days"
		});
		$.extend(graphOptions.yAxis.title.style, {
			fontWeight: "normal"
		});
		$.extend(graphOptions.tooltip, {
			formatter: function () {
				var tts = "<b>" + Highcharts.dateFormat('%a, %B %e, %Y', this.x) + "<\/b>" +
					"<br \/>Accumulated degree-days: " + Highcharts.numberFormat(this.y, 0);
				return tts;
			}
		});
		if (lastvalue <= f1 && lastvalue !== -999) {
			$.extend(plotlines[0].label, {text: "First Emergence"});
			$.extend(plotlines[1].label, {text: "50% Emergence"});
			$.merge(plotlines, emergencelines);
		} else if (lastvalue < f2) {
			$.extend(plotlines[3].label, {text: "50% First Generation"});
		} else if (lastvalue < f3) {
			$.extend(plotlines[5].label, {text: "50% Second Generation"});
		} else if (lastvalue < f4) {
			$.extend(plotlines[7].label, {text: "50% Third Generation"});
		}
		$.extend(graphOptions.yAxis, {
			min: 0,
			minRange: 500,
			endOnTick: false,
			plotLines: plotlines,
			plotBands: [
				{from: se, to: f1, color: "rgba(153,101,21,0.9)", zIndex: 2},
				{from: f1, to: f2, color: "rgba(205,133,63,0.9)", zIndex: 2},
				{from: f2, to: f3, color: "rgba(218,165,32,0.9)", zIndex: 2},
				{from: f3, to: f4, color: "rgba(238,232,170,0.9)", zIndex: 2}
			]
		});
		$("#chart_area").highcharts(graphOptions);
	}
}
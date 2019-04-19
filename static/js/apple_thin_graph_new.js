function defineGraphOptions() {
	return {
		chart: {
			height: 200,
			marginRight: 20
		},
		credits: {
			text: "Powered by ACIS",
			href: "http://www.rcc-acis.org"
		},
		title: {
			text: "Carbohydrate Balance",
			style: {
				fontSize: '12px'
			}
		},
		tooltip: {
			xDateFormat: '%b %e',
			valueDecimals: 2
		},
		legend: {
			enabled: false
		},
		xAxis: {
			type: "datetime",
			dateTimeLabelFormats: {
				hour: "%b %e -",
				day: "%b %e",
				week: "%b %e",
				month: "%b %e"
			},
			minRange: 8 * 24 * 3600000,	// eight days
			gridLineWidth: 1
		},
		yAxis: {
			title: {
				text: "7-Day Ave Balance",
				style: {
					fontSize: '12px',
					fontWeight: 'normal'
				}
			},
			minorGridLineDashStyle: 'dot',
			minorTickInterval: 20
		},
		series: []
	};
}

function buildChartSeries() {
	var i, mdtext, valtext,
		miss = "-999",
		data_series = [],
		year = $("#greentip").val().split("/")[2],
		ymdToUTC = function(x) {
			var md = x.split("/");
			return Date.UTC(year, md[0] - 1, md[1], 0);
		};
	for (i = 2; i <= $("#results_table tr").length - 4; i += 1) {
		mdtext = $("#results_table tr").eq(i).find("td:nth-child(1)").text();
		valtext = $("#results_table tr").eq(i).find("td:nth-child(6)").text();
		data_series.push([ymdToUTC(mdtext), valtext !== miss && valtext !== "-" && valtext !== "" ? parseFloat(valtext) : null]);
	}
	return {
		data: data_series,
		type: 'line',
		name: '7-day ave balance',
		turboThreshold: data_series.length
	};
}

function displayGraph() {
	var container = "#chart_area",
		chartSeries = buildChartSeries(),
		graphOptions = defineGraphOptions();
	if (chartSeries.data.length > 0) {
		graphOptions.series.push(chartSeries);
		$(container).highcharts('Chart', graphOptions);
	} else {
		$(container).append("Graph unavailable");
		return false;
	}
}
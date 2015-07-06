		function setSelectValue(oVal) {
			var oSel = document.dmcast.stn;
			for ( var i = 0; i < oSel.options.length; i++ ) {
				if( oSel.options[i].value == oVal ) { oSel.options[i].selected = true; }
			}
		}

		function getdmcast() {
			var params = {type: 'dmcast'};
			$('select[name=stn], input[name=accend], select[name=cultivar]').each(function () { params[this.name] = this.value; });
			$('#second').empty().html('<img src="http://newa.nrcc.cornell.edu/gifs/ajax-loader.gif" alt="Processing" id="loading" /> Loading');
			$('#righttabs').tabs('select',1);
			$.get('http://newa.nrcc.cornell.edu/newaModel/process_input',params,function(data) {
				$('#loading').fadeOut(500, function() { $(this).remove(); });
				$("#second").html(data);
			});
			return false;
		}

		function update_help() {
			var params = {type: 'dmcast'};
			$.get('http://newa.nrcc.cornell.edu/newaModel/process_help',params,function(data) { $('#third').html(data); });
			return false;
		  }

		$(document).ready(function() {
			$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+1d" });
			var myDate = new Date();
			var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
			$("#enddpick").val(todayDate);
			$("#righttabs").tabs();
			$("form .button").click(function (evt) { getdmcast(); });
			set_up();
			setTimeout(updateLatLon("lwrh"),0);
			update_help();
		 })


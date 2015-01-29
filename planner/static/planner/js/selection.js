function selectf(begin, end) {
	// console.debug("selectf")
	var range1 = { begin: begin, end: end };
	$(".s_range").each(function(index) {
		var range2 = { begin: moment($(this).attr("s_begin")), end: moment($(this).attr("s_end"))}
		if (!if_disjoint(range1, range2)) {
			range1 = join_ranges(range1, range2);
			this.remove();
		}
	});

    var begin_str = range1.begin.format('YYYY-MM-DD');
    var end_str = range1.end.format('YYYY-MM-DD');

    var days_between = range1.end.diff(range1.begin, 'days');
    console.debug(days_between);

    $('#absence_select').append(''
        + '<a href="#" class="s_range list-group-item rm-absence-selection" '
        + 's_begin=\'' + begin_str + '\' s_end=\'' + end_str + '\'>'
        + '<span class="badge">' + days_between + '</span>'
    	+ range1.begin.format('DD MMM') + ' - ' + range1.end.format('DD MMM')
        + '<input type="hidden" name="begin[]" value="' + begin_str + '" />'
        + '<input type="hidden" name="end[]" value="' + end_str + '" />'
     	+ '</a>');

    // sorting after every entry, fuck the poverty!
    
    function comp(a,b) {
    	// console.debug("comp")
     	return ($(b).attr("s_begin") < $(a).attr("s_begin")) ?  1 : -1
     }
    $('#absence_select a').sort(comp).appendTo('#absence_select');
}

function unselectf(view, jsEvent) {
	console.debug("unselectf");
	$('#yourCalendar').fullCalendar('unselect');
}

// (b1 <= b2) =>
// 1. [b1  [b2   e2]  e1] -> [b1  e1]
// 2. [b1  [b2   e1]  e2] -> [b1  e2]

// if_disjoint :: { begin: moment, end: moment} , {begin: moment, end: moment} -> bool 
function if_disjoint(range1, range2) {
	if (range1.begin > range2.begin)
		return if_disjoint(range2, range1); // now we know that range1.begin <= range2.begin
	return range1.end < range2.begin;
}

// join_ranges :: { begin: moment, end: moment} , {begin: moment, end: moment} -> {moment, moment} 
function join_ranges(range1, range2) {
	if (range1.begin > range2.begin)
		return join_ranges(range2, range1); // now we know that range1.begin <= range2.begin
	if (range1.end <= range2.end) 
		return {begin: range1.begin, end: range2.end }; // 2.
	else
		return {begin: range1.begin, end: range1.end }; // 1.
}

$(document).on('click', '.rm-absence-selection', function(){
	console.debug('removing selected range');
	// if someone has more stupid idea to refresh all selected days, please show me
	$(this).remove();
	$('#calendar').fullCalendar('next');
	$('#calendar').fullCalendar('prev');
	
	$(".s_range").each(function(index) {
		console.debug($(this).attr("s_begin"));
		console.debug($(this).attr("s_end"));
		m1 = moment($(this).attr("s_begin"));
		m2 = moment($(this).attr("s_end"));
		$('#calendar').fullCalendar('select', m1, m2)
	})

	
})

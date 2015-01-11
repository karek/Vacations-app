function selectf(begin, end) {
	// console.log("selectf")
	var range1 = { begin: begin, end: end }
	$(".s_range").each(function(index) {
		var range2 = { begin: moment($(this).attr("s_begin")), end: moment($(this).attr("s_end"))}
		if (!if_disjoint(range1, range2)) {
			range1 = join_ranges(range1, range2)
			this.remove()
		}
			
	})

    $('#absence_select').append('<li class="s_range" s_begin=\'' + range1.begin.format('YYYY-MM-DD')
    	+ '\' s_end=\'' + range1.end.format('YYYY-MM-DD') + '\'>'
    	+ range1.begin.format('DD MMM') + ' -- ' 
    	+ range1.end.format('DD MMM') + "                   " 
     	+ '<button type="button" class="btn btn-danger btn-xs btn-remove"> Delete </button>' + '</li>')

    // sorting after every entry, fuck the poverty!
    
    function comp(a,b) {
    	// console.log("comp")
     	return ($(b).attr("s_begin") < $(a).attr("s_begin")) ?  1 : -1
     }
    $('#absence_select li').sort(comp).appendTo('#absence_select');

}

function unselectf(view, jsEvent) {
	console.log("unselectf")
}


// (b1 <= b2) =>
// 1. [b1  [b2   e2]  e1] -> [b1  e1]
// 2. [b1  [b2   e1]  e2] -> [b1  e2]

// if_disjoint :: { begin: moment, end: moment} , {begin: moment, end: moment} -> bool 
function if_disjoint(range1, range2) {
	if (range1.begin > range2.begin)
		return if_disjoint(range2, range1) // now we now that range1.begin <= range2.begin 
	if (range1.end < range2.begin)
		return true
	else
		return false	
}

// join_ranges :: { begin: moment, end: moment} , {begin: moment, end: moment} -> {moment, moment} 
function join_ranges(range1, range2) {
	if (range1.begin > range2.begin)
		return join_ranges(range2, range1) // now we now that range1.begin <= range2.begin 	
	if (range1.end <= range2.end) 
		return {begin: range1.begin, end: range2.end } // 2.
	else
		return {begin: range1.begin, end: range1.end } // 1.
}
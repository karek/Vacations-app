function log_date(msg, date) {
    console.debug(msg + " " + date.format("YYYY-MM-DD HH:mm:ss:SS") + " | " + date);
}

// Selection mode switch. If empty, it means the select action was called by the user, so we must
// check intersections and calculate the real selection range. If 'confirmed', the callback was called
// just to refresh days highlighted in the calendar, so selectf may do nothing else.
// If 'deselect', the action was called by the user, but we are deselecting days.
global_select_mode = 'deselect';
function deselect_enabled() { return global_select_mode === 'deselect'; }
function compute_selections() { return global_select_mode != 'confirmed'; }
// For manual selection disabling, e.g. when processing an absence in management panel
global_disable_selecting = false;

function get_selection_highlight_classes() {
    if (global_select_mode === 'deselect' ) return [ 'fc-highlight', 'deselect-highlight' ];
    if (global_select_mode === 'confirmed' ) return [ 'fc-highlight', 'confirmed-highlight' ];
    return [ 'fc-highlight' ];
}

// If the selection starts within an already selected range, set mode to deselecting
function set_selection_type(start_point) {
    global_select_mode = '';
    if (start_point !== null) {
        $(".s_range").each(function(index) { 
            var old_range = { begin: moment($(this).attr("s_begin")), end: moment($(this).attr("s_end"))};
            if (in_range(start_point, old_range)) {
                //console.debug('activating DESELECT');
                global_select_mode = 'deselect';
            }
        });
    }
}

function selectf(begin, end, jsEvent, view) {
	// console.debug("selectf")
    if (compute_selections() && !global_disable_selecting) {
        log_date("selectf.begin:", begin);
        log_date("selectf.end:", end);
        var range = {
            begin: moment(begin.format('YYYY-MM-DD')),
            end: moment(end.format('YYYY-MM-DD')) 
        };
        check_and_add_range(range);
    } else if (compute_selections() && global_disable_selecting) {
        // we are called by a normal selection event, but selecting is disabled.
        // we must refresh the currently selected ranges, to remove FC's selection highlight which
        // is apparently done before calling selectf()
        //console.debug('selecting disabled!');
        highlight_selected_ranges();
    } else {
        // if we are called just to highlight the range, abort further calculations
        //console.debug('compute off');
    }
}

function is_holiday(date) {
    var result = false;
    $.each(global_holidays, (function(index) {
        if (moment(global_holidays[index].day).isSame(date)) {
            result = true;
        }
    }));
    return result;
};

function count_range_length(begin, end) {
    var absence_length = 0;
    var days = 0;

    duration = moment.duration(end - begin).days()

    date = begin.add(-1,'days');
    while (duration > 0) {
        date = date.add(1, 'days');
        if (!is_holiday(date)) {
          days += 1;
        }
        duration -= 1;
    }

    return days

}

function count_absence_length() {
    // get absence_length
    var days = 0;
    $(".s_range").each(function(index) {
        days += count_range_length(moment($(this).attr("s_begin")), moment($(this).attr("s_end")))
    });

    $('#absence_length').html(days)
}

// Check the range selected by the user for intersections with [1] already selected ranges,
// [2] previously booked user's absences; then append the remaining range[s] to absence list.
function check_and_add_range(range) {
    // [1] check with already selected ranges
    // merge with old ranges (or subtract from them if we're deselecting)
	$(".s_range").each(function(index) {
		var old_range = { begin: moment($(this).attr("s_begin")), end: moment($(this).attr("s_end"))};
        //log_date("--- loop old_range.begin:", old_range.begin);
        //log_date("    loop old_range.end:  ", old_range.end);
        // ranges intersect!
		if (!if_disjoint(range, old_range)) {
            if (deselect_enabled()) {
                // deselect: remove old range, add back what remains besides the new one
                this.remove();
                //since this is not a merge of ranges, we have to check if this wasn't the last range on the list
                //and if it is, we should hide Plan button
                display_or_hide_planning_controls();
                var old_minus_new = subtract_range(old_range, range);
                for (var i in old_minus_new) {
                    add_checked_range(old_minus_new[i]);
                }
            } else {
                // merge: delete the original range and extend the new one to contain it
                range = join_ranges(range, old_range);
                this.remove();
            }
		}
	});
    //log_date("after disjoints .begin:", range.begin);
    //log_date("after disjoints .end:", range.end);

    if (!deselect_enabled()) {
        // [2] subtract already reserved absences and really select what's left
        // (but only if we are adding a selection)
        for (var i in global_logged_user_absences) {
            var cur_range = mapAjaxAbsenceToRange(global_logged_user_absences[i]);
            subtracted = subtract_range(range, cur_range);
            //console.debug("subtracted ", cur_range.begin, " - ", cur_range.end, " -> ", subtracted.length);
            switch(subtracted.length) {
                case 0: // current range covers whole remaining range, nothing more to do
                    range = null;
                    break;
                case 1: // ranges are disjoint or current range cut only one end of the remaining range
                    range = subtracted[0];
                    break;
                case 2:
                    // Current range split the remaining range. We assume that the stored ranges are
                    // sorted and disjoint, thus we know that the first range is ready for displyaing,
                    // but we must still check the latter one.
                    add_checked_range(subtracted[0]);
                    range = subtracted[1];
                    break;
                default:
                    console.error("this should never happen");
            }
            // stop if there is nothing left
            if (range === null) break;
        }
        // if it wasn't erased, the remaining range is also valid
        if (range !== null) add_checked_range(range);
    }

    // when all work is done, refresh the selections, in case we modified the original range
    highlight_selected_ranges();
}

// finalize selectf's job -- add a cleaned and checked range to selected absences
function add_checked_range(range) {
    var begin_str = range.begin.format('YYYY-MM-DD');
    var end_str = range.end.format('YYYY-MM-DD');

    var display_date = {begin: moment(range.begin), end: moment(range.end)};
    display_date.end.subtract(1, "days");

    log_date("display_date.begin:", display_date.begin);
    log_date("display_date.end:", display_date.end);

    var days_between = count_range_length(range.begin, range.end)
    var display_range_str;

    if (days_between != 0) {
        if (days_between == 1) {
            display_range_str = display_date.begin.format('DD MMM');
        } else {
            if (display_date.begin.year() != display_date.end.year()) {
                display_range_str = display_date.begin.format('DD MMM YYYY') + ' - ' + display_date.end.format('DD MMM YYYY');
            }
            else if (display_date.begin.month() == display_date.end.month()) {
                display_range_str = display_date.begin.format('DD') + ' - ' + display_date.end.format('DD MMM');
            } else {
                display_range_str = display_date.begin.format('DD MMM') + ' - ' + display_date.end.format('DD MMM');
            }
        }

        var accept_mode = accept_mode_enabled();

        $('#absence_select').append(''
            + '<li class="s_range list-group-item" '
            + 's_begin=\'' + begin_str + '\' s_end=\'' + end_str + '\'>'
            + display_range_str
            + '<span class="badge">'
            + (accept_mode ? "" : '<a href="#" class="rm-absence-selection" style="text-decoration: none; color: #ffffff">')
            + days_between
            + (accept_mode ? "" : ' <span class="glyphicon glyphicon-remove"></span></a>')
            + '</span>'
            + '<input type="hidden" name="begin[]" value="' + begin_str + '" />'
            + '<input type="hidden" name="end[]" value="' + end_str + '" />'
            + '</li>');


        function comp(a, b) {
            return ($(b).attr("s_begin") < $(a).attr("s_begin")) ? 1 : -1
        }

        $('#absence_select li').sort(comp).appendTo('#absence_select');
        display_or_hide_planning_controls();
    }

    count_absence_length()
}

function unselectf(view, jsEvent) {
	//console.debug("unselectf");
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

// Substract range2 from range1. Returns an array of zero, one or two ranges.
function subtract_range(range1, range2) {
    if (if_disjoint(range1, range2)) return [range1];
    if (range2.begin <= range1.begin) {
        // range2 completely covers range1
        if (range2.end >= range1.end) return new Array();
        // range2 covers only beginning of range1
        return [{begin: range2.end, end: range1.end}];
    } else {
        // range2 covers only ending of range1
        if (range2.end >= range1.end) return [{begin: range1.begin, end: range2.begin}];
        // range2 splits range1 into two ranges
        return [{begin: range1.begin, end: range2.begin}, {begin: range2.end, end: range1.end}];
    }
}

// Returns whether a moment is within given range.
function in_range(point, range) {
    return point >= range.begin && point < range.end;
}

function mapAjaxAbsenceToRange(absence) {
    return { begin: moment(absence.begin), 
             end: moment(absence.end) };
}

// Shows or hides Plan button if there are no ranges selected at the moment
function display_or_hide_planning_controls() {
    console.debug("display_or_hide_planning_controls");
    var currently_selected_ranges = $('#absence_select > li').length;
    var ranges_not_selected = currently_selected_ranges == 0;

    console.debug("manage_mode_enabled = " + manage_mode_enabled());
    console.debug("user_is_logged_in = " + user_is_logged_in());
    console.debug("ranges_not_selected = " + ranges_not_selected);


    var manage_list = $('#manage_absence_list');
    var manage_no_absences = $('#manage_no_absences');
    var manage_buttons = $('#manage_buttons');
    var manage_invitation_log_in = $('#manage_invitation_log_in');
    var manage_back_exit_button = $('#manage_back_button');
    var manage_exit_button = $('#exit_manager_mode');

    var invitation_select_days = $('#invitation_select_days');
    var absence_comment = $('#absence_comment');
    var absence_other_fields = $('#absence_other_fields');
    var plan_absence_button = $('#plan_absence_button');
    var invitation_log_in = $('#invitation_log_in');

    var absence_select = $('#absence_select');

    manage_list.hide();
    manage_no_absences.hide();
    manage_buttons.hide();
    manage_invitation_log_in.hide();
    manage_back_exit_button.hide();
    manage_exit_button.hide();

    invitation_select_days.hide();
    // absence_comment.hide();
    absence_other_fields.hide();
    plan_absence_button.hide();
    invitation_log_in.hide();

    absence_select.hide();

    if (manage_mode_enabled()) {
        // TODO zmienilem tutaj zarzadzanie widocznymi elementami,
        // mozna ukryc cos jak uzytkownik nie jest zalogowany w trybie akceptowania
        // wywoluje ta funkcje przy renderowaniu index.html i manage.html

        if (!accept_mode_enabled()) {
            manage_exit_button.show();
            if(user_is_logged_in()) {
                manage_no_absences.show();
                get_management_absences();
            } else {
                manage_invitation_log_in.show();
            }
        } else {
            manage_list.show();
            absence_select.show();
            manage_back_exit_button.show();
            if (user_is_logged_in()) {
                manage_buttons.show();
            } else {
                manage_invitation_log_in.show();
            }
        }
    } else {
        if (ranges_not_selected) {
            if (user_is_logged_in()) {
                invitation_select_days.show();
            } else {
                invitation_log_in.show();
            }
        } else {
            absence_select.show();
            if (user_is_logged_in()) {
                // absence_comment.show();
                absence_other_fields.show();
                plan_absence_button.show();
            } else {
                invitation_log_in.show();
            }
        }
    }
}

$(document).on('click', '.rm-absence-selection', function(){
	console.debug('removing selected range');
	$(this).closest('li').remove();
    highlight_selected_ranges();
    count_absence_length();
	display_or_hide_planning_controls();
});

// When passed as 'selectOverlap' calendar's parameter, this function disallows selections
// intersecting with user's current absences.
function check_select_overlap(cal_event) {
    console.debug("check_select_overlap for event #" + cal_event.id + ": " + cal_event.title + ", "
            + cal_event.user_id);
    return cal_event.user_id !== global_logged_user_id;
}

// Highlight ("select") all currently planned absence ranges on the calendar.
// To be used on view switching or after manual unselect (to "unhighlight" some days).
function highlight_selected_ranges() {
    // switch off computing selections, to avoid recursive re-calculations inside `select` callback
    global_select_mode = 'confirmed';
    // first, delete all current selections (I see no way to do this partially or less brutally)
    $('div.fc-highlight-skeleton').remove();
	// then, reselect remaining selections
	$(".s_range").each(function(index) {
		m1 = moment($(this).attr("s_begin"));
		m2 = moment($(this).attr("s_end"));
		$('#calendar').fullCalendar('select', m1, m2);
	});
    // restore normal selection mode
    global_select_mode = '';
}

// To be connected to FC's viewRender callback, triggered after every view switch.
function view_render_callback(view, element) {
    highlight_selected_ranges();
    if (typeof global_view_filters_clicked !== 'undefined' && !global_view_filters_clicked) {
        if (view.name == 'weekWorkers' && global_teams_selected[global_logged_user_team_id] == 0) {
            getUsersFromSelectedTeamsById(global_logged_user_team_id);
            changeButtonState(global_logged_user_team_id, true);
        }
        if (view.name == 'month' && global_teams_selected[global_logged_user_team_id] == 1) {
            global_teams_selected[global_logged_user_team_id] = 0;
            changeButtonState(global_logged_user_team_id, false);
            $('#calendar').fullCalendar('refetchEvents');
        }
    }
}

// Manually add selection from given ranges (from DB's json)
function select_ranges_from_json(ranges) {
    console.debug('select from json: ' + ranges.length + 'ranges');
    for (i in ranges) {
        var range = {
            begin: moment(ranges[i].begin),
            end: moment(ranges[i].end) 
        };
        // we trust data from DB enough to skip checks :)
        add_checked_range(range);
    }
    // ensure at least the first of selected ranges is visible
	$('#calendar').fullCalendar('gotoDate', moment(ranges[0].begin));
    highlight_selected_ranges();
}

// Returns true if we are in management mode
function manage_mode_enabled() {
    return (typeof global_manage_mode !== 'undefined');
}

function manage_mode_selfcare() {
    return manage_mode_enabled() && global_manage_mode == 'selfcare';
}

function manage_mode_team_manager() {
    return manage_mode_enabled() && global_manage_mode == 'manager';
}

// Returns true if we are in management mode AND processing an absence request
function accept_mode_enabled() {
    return (typeof global_accept_absence_id !== 'undefined');
}

function user_is_logged_in() {
    return global_logged_user_id != -1;
}

function edit_mode_enabled() {
    return (typeof global_edit_absence !== 'undefined');
}

global_show_my_absences = true;
function toggle_my_absences(jsevent, state) {
    global_show_my_absences = state;
	$('#calendar').fullCalendar('refetchEvents');
    global_view_filters_clicked = true;
}

function getUsersFromSelectedTeams(jsevent) {

    var curTeam = jsevent.target.value;
    getUsersFromSelectedTeamsById(curTeam);
}

function getUsersFromSelectedTeamsById(team_id) {
    if (global_teams_selected[team_id] != team_id)
        global_teams_selected[team_id] = team_id;
    else
        global_teams_selected[team_id] = 0;

    filterGlobalUsers();
	$('#calendar').fullCalendar('refetchEvents');
}


function selectAllTeams() {

    for (var i = 0; i < global_teams_selected.length; i++)
        global_teams_selected[i] = i;

    filterGlobalUsers();
	$('#calendar').fullCalendar('refetchEvents');
}

function unselectAllTeams() {

    for (var i = 0; i < global_teams_selected.length; i++)
        global_teams_selected[i] = 0;

    filterGlobalUsers();
	$('#calendar').fullCalendar('refetchEvents');
}

function changeButtonState(id, state) {
    var curTeam = "#id_teams_" + (id - 1);
    var a = $(curTeam);
    a.bootstrapSwitch('state', state, true);
}

function filterGlobalUsers() {
    global_users_filtered = [];
    for (var i in global_users) {
        if(global_teams_selected[global_users[i].team_id] != 0) {
            global_users_filtered.push(global_users[i]);
        }
    }
    calcSorted(global_users_filtered);

    //Somebody fix dat shit down there please VVV :(
    var date = $('#calendar').fullCalendar('getDate');
    $('#calendar').fullCalendar('next');
    $('#calendar').fullCalendar( 'gotoDate', date );
}

function prettify_team_select() {
    $('ul#id_teams').siblings('label').remove();
    var labels= $('ul#id_teams label');
    labels.each(function(index){
        var text = $(this).html().replace(/.*>/, '');
        var rest = $(this).html().replace(text, '');
        $(this).html(rest);
        $(this).children('input').bootstrapSwitch({
            state: false,
            size: 'mini',
            offColor: 'warning',
            onColor: 'primary',
            inverse: true,
            labelText: text,
            handleWidth: 50,
            labelWidth: 189,
            onSwitchChange: team_select_clicked,
        });
    });
}

function team_select_clicked(jsevent, state) {
    getUsersFromSelectedTeams(jsevent);
    global_view_filters_clicked = true;
}

function event_render_callback(event, element) {
    if (event.tooltip_text) {
        element.tooltip({
            title: event.tooltip_text,
            html: true,
        });
    }
}

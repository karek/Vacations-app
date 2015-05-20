// Global arrays used by all scripts
global_users = new Array();
global_users_by_id = new Array();
// These arrays will hold absences currently pulled in by the calendar (most likely the visible ones)
global_ranges = new Array();
global_logged_user_absences = new Array();
global_holidays = new Array();
global_mng_absences = new Array()
// number to put in user_id field for holiday events
global_event_is_holiday = -1;

global_users_filtered = new Array();
global_teams_selected = new Array();
global_users_loaded = false;
global_users_sorted = new Array();
global_users_order = new Array();

absence_text_accepted = "Accepted";
absence_text_pending = "Pending";
absence_text_rejected = "Rejected";

status_PENDING = 0;
status_ACCEPTED = 1;
status_REJECTED = 2;
status_PENDING_OR_ACCEPTED = '0,1';

// Get and save absence ranges, and execute the function on them.
// Pass empty users array to get everyone's absences.
function getAbsenceRangesBetween(begin, end, users, on_success) {
    var req_url = global_range_url + '?begin=' + begin + '&end=' + end;
    for (var i in users) req_url += '&user[]=' + users[i]; 
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            console.debug('ajax returned: ' + data.length + ' absence ranges');
            // TODO: remove this in the future
            debugShowRanges(data);
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting absence ranges!');
        }
    });
}


// Get and save holidays between given dates.
function getHolidaysBetween(begin, end, on_success) {
    var req_url = global_holiday_url + '?begin=' + begin + '&end=' + end;
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: 'GET',
        url: req_url,
        success: function(data) {
            console.debug('ajax returned: ' + data.length + ' holidays');
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting holidays!');
        }
    });
}


// Get and save users (and execute callback).
function getAllUsers(on_success) {
    if (global_users_loaded) {
        console.debug('users already loaded, running on_success immediately');
        on_success(global_users);
        return;
    }
    var req_url = global_user_url;
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            console.debug('ajax returned ' + data.length + ' users');

            saveUserData(data);
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting users!');
        }
    });
}

function calcSorted(data) {
    gloabal_users_by_id = [];
    global_users_sorted = [];
    global_users_order = [];

    for (u in data) {
        data[u]['full_name'] = data[u].first_name + ' ' + data[u].last_name;
        console.debug('saving user ' + data[u].email);
        global_users_by_id[data[u].id] = data[u];
        global_users_sorted[data[u].id] = data[u];
    }

// In future functions sort it in some other way
//    global_users_sorted = global_users_sorted.filter(
//        function (a) {
//            return a.id != global_logged_user_id;
//        });

    sortAndSaveUsersOrder(function (a, b) {

//Logged user will be first
        if(a.id == global_logged_user_id)
            return false;

        if(b.id == global_logged_user_id)
            return true;

//grouping by team
        if (a.team_id != b.team_id)
        {
            if (a.team_id == global_logged_user_team_id)
                return false;

            if (b.team_id == global_logged_user_team_id)
                return true;

            return a.team_id > b.team_id;
        }

//They are in the same team -> further sorting
        if (a.is_teamleader)
            return false;

        if (b.is_teamleader)
            return true;

        return a.last_name.toUpperCase() > b.last_name.toUpperCase();
    });

}

// Save received users' data.
function saveUserData(data) {
    global_users = data;
    filterGlobalUsers();
}

//Function used for sorting user and later Map users ids in the order to their position
//Function f orders sort
function sortAndSaveUsersOrder(f) {

    global_users_sorted.sort(f);

    for (i in global_users_sorted)
        global_users_order[global_users_sorted[i].id] = i;
}


// Save holidays
function saveHolidays(data) {
    global_holidays = data;
}

// Get all users in fullCalendar's format
function getAbsencesForCalendar(begin, end, timezone, callback) {
    console.debug('calendar calls for events from ' + begin.format('YYYY-MM-DD')
        + ' to ' + end.format('YYYY-MM-DD'));
    // TODO: should we be concerned about the timezone?
    // TODO: add user/team selection when it's needed
    getAbsenceRangesBetween(
        begin.format('YYYY-MM-DD'),
        end.format('YYYY-MM-DD'),
        [],
        function (ranges) {
            var event_objects = new Array();
            var logged_user_absences = new Array();
            for (var i in ranges) {
                // in accept mode, don't show the processed absence as events
                if (accept_mode_enabled() && ranges[i].absence_id == global_accept_absence_id) {
                    continue;
                }
                if (edit_mode_enabled() && ranges[i].absence_id == global_edit_absence.id) {
                    continue;
                }

                // not in currently selected teams
                if (global_teams_selected[global_users_by_id[ranges[i].user_id].team_id] == 0
                        && ranges[i].user_id != global_logged_user_id) {
                    continue;
                }
                if (!global_show_my_absences && ranges[i].user_id == global_logged_user_id) {
                    continue;
                }

                event_objects.push(calendar_event_from_range(ranges[i]));

                // pull out current user's absences
                if (global_logged_user_id === ranges[i].user_id) {
                    logged_user_absences.push(ranges[i]);
                }
            }
            // copy data to global arrays, for convenience of other calculations
            global_ranges = ranges;
            global_logged_user_absences = logged_user_absences;
            console.debug('saved ' + event_objects.length + ' ranges');
            console.debug('saved ' + logged_user_absences.length + ' logged user\'s ranges');
            // now also get holidays for the given range
            getHolidaysBetween(
                begin.format('YYYY-MM-DD'),
                end.format('YYYY-MM-DD'),
                function(holidays) {
                    for (var i in holidays) {
                        var event = {
                            id: 'holiday' + holidays[i].id,
                            title: holidays[i].name,
                            start: holidays[i].day,
                            end: holidays[i].day,
                            className: ['absence-type-holiday'],
                            user_id: global_event_is_holiday,
                            icon: 'gift'
                        };
                        event_objects.push(event);
                        // clone the holiday as a background event
                        var event2 = JSON.parse(JSON.stringify(event));
                        event2.rendering = 'background';
                        event2.color = 'red';
                        event2.className = new Array();
                        event_objects.push(event2);
                    }
                    saveHolidays(holidays);
                    callback(event_objects);
                    if (global_after_load_callbacks.has()) {
                        global_after_load_callbacks.fire();
                        global_after_load_callbacks.empty();
                    }
                }
            );
        }
    );
}

function calendar_event_from_range(range) {
    var classes = new Array();
    if (range.status == status_ACCEPTED) classes.push('absence-status-accepted');
    else classes.push('absence-status-pending');
    var kindclass = 'absence-kind-' + range.kind_name.toLowerCase().replace(' ', '-');
    classes.push(kindclass);
    var tooltip_text = '';
    if (range.comment) tooltip_text = '<i>' + range.comment + '</i>';

    var cal_event = {
        id: range.id,
        title: global_users_by_id[range.user_id].full_name,
        start: range.begin,
        end: range.end,
        user_id: range.user_id,
        className: classes,
        type: range.kind_name,
        icon: range.kind_icon,
    };

    // On clicking an event, open its absence details or management
    if (!manage_mode_team_manager() && range.user_id == global_logged_user_id) {
        cal_event.url = '/my-absences/?absence-id=' + range.absence_id;
        if (tooltip_text) tooltip_text += '<br/>';
        tooltip_text += '<span class="glyphicon glyphicon-zoom-in"></span>&nbsp;Click to view details';
    } else if (global_logged_user_team_id == global_users_by_id[range.user_id].team_id
            && global_logged_user_is_teamleader && range.status == status_PENDING) {
        cal_event.url = '/manage-absences/?absence-id=' + range.absence_id;
        if (tooltip_text) tooltip_text += '<br/>';
        tooltip_text += '<span class="glyphicon glyphicon-wrench"></span>&nbsp;Click to manage';
    }

    if (tooltip_text) {
        cal_event.tooltip_text = tooltip_text;
    }

    return cal_event;
}


function saveAbsencesForCalendar(ranges, callback) {
}


// add received ranges to the debug list
// TODO: remove this in the future
function debugShowRanges(ranges) {
    console.debug('showing ' + ranges.length + ' ranges');
    $('#all_ranges').append('<hr />');
    for (i in ranges) {
        var uid = ranges[i].user_id;
        var li = '<li>from ' + ranges[i].begin + ' to ' + ranges[i].end + ', by '
            + global_users_by_id[uid].full_name + ' (' + global_users_by_id[uid].email + ')'
            + '</li>';
        $('#all_ranges').append(li);
    }
}

function make_get_param(url, param, value) {
    var paramstr = param + '=' + encodeURI(value);
    if (url.indexOf('?') != -1) return '&' + paramstr;
    return '?' + paramstr;
}

// Get absences (without AbsenceRanges), e.g. for management panel
// params should be a dict of filtering parameters accepted by backend
function getMatchingAbsences(params, on_success) {
    var req_url = global_absence_url;
    for (var param in params) {
        req_url += make_get_param(req_url, param, params[param]);
    }
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            console.debug('ajax returned: ' + data.length + ' absences');
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting absences!');
        }
    });
}

// Get absences for management panel according to mode:
// 'selfcare' => PENDING or ACCEPTED absences of logged user
// 'manager' => PENDING absences of manager's team
function get_management_absences() {
    var params = {};
    if (manage_mode_selfcare()) {
        params = {
            'user-id': global_logged_user_id,
            'date-not-before': moment().format('YYYY-MM-DD'),
            'status': status_PENDING_OR_ACCEPTED
        };
    } else {
        params = {
            'team-id': global_logged_user_team_id,
            'status': status_PENDING,
        }
    }
    getMatchingAbsences(
        params,
        function(absences) {
            global_mng_absences = absences;
            show_management_absences();
        });
}

// Show absences on management panel from data fetched into global_mng_absences.
function show_management_absences() {
    var manage_hdr = $('#manage_no_absences');
    var manage_list = $('#manage_absence_list');
    manage_hdr.hide();
    if (global_mng_absences.length == 0) {
        manage_hdr.show();
        var text = (manage_mode_selfcare()
                ? 'No upcoming absences.'
                : 'No pending absence requests.')
        manage_hdr.html(text);
        manage_list.hide();
        return;
    }
//    manage_hdr.html('<b>Pending requests:</b>');
    var absences = global_mng_absences.map(show_mng_absence_as_li).join('\n');
    manage_list.html(absences);
    manage_list.show()
}

// Show absence (as returned from DB) as list element, with link to its management
function show_mng_absence_as_li(absence) {
    var link = global_manage_url + '?absence-id=' + absence.id;
    var label_text = absence.total_workdays;
    var label_class = 'badge';
    if (manage_mode_selfcare() && absence.status == status_ACCEPTED) {
        label_class += ' progress-bar-success';
        label_text += '&nbsp;<span class="glyphicon glyphicon-ok"></span>';
    }
    var comment_row = '';
    if (absence.comment) {
        comment_row = '<tr><th scope="row">Comment</th><td>' + absence.comment + '</td></tr>';
    }
    var modified_row = '';
    if (absence.created_ts != absence.modified_ts) {
        modified_row = '<tr><th scope="row">Modified</th><td>' + absence.date_modified + '</td></tr>';
    }
    var date_desc = (absence.status == status_ACCEPTED) ? 'Created' : 'Requested';
    return ''
        + '<a class="list-group-item" href="' + link + '">'
        + '<span class="'+ label_class + '" style="margin-top: 10px;">' + label_text + '</span>'
        + '<h4>' + absence.user_name + '</h4>'
        + '<table class="table pending-details-table" style="margin-bottom: 0px;">'
        + '<tbody><tr>'
        + '<th scope="row">Kind</th><td>' + absence.kind_name + '</td></tr>'
        + '<tr><th scope="row">' + date_desc + '</th><td>' + absence.date_created + '</td></tr>'
        + modified_row
        + comment_row
        + '</tbody></table>'
        + '</a>';
}

function select_managed_absence() {
    select_ranges_from_json(global_accept_ranges);
    global_disable_selecting = true;
}

function select_edited_absence() {
    select_ranges_from_json(global_edit_ranges);
    $('#planning-comment').val(global_edit_absence.comment);
    var string_kind = new String(global_edit_absence.kind_id);
    console.debug('kind str: ', string_kind);
    $('#planning-kind-select').val(string_kind).change();
}

// Global arrays used by all scripts
global_users = new Array();
global_users_by_id = new Array();
// These arrays will hold absences currently pulled in by the calendar (most likely the visible ones)
global_absences = new Array();
global_logged_user_absences = new Array();
global_holidays = new Array();
// number to put in user_id field for holiday events
global_event_is_holiday = -1;

// Get and save absence ranges, and execute the function on them.
// Pass empty users array to get everyone's absences.
function getAbsencesBetween(begin, end, users, on_success) {
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
            alert('Error getting absences!');
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


// Save received users' data.
function saveUserData(data) {
    global_users = data;
    for (u in data) {
        data[u]['full_name'] = data[u].first_name + ' ' + data[u].last_name;
        console.debug('saving user ' + data[u].email);
        global_users_by_id[data[u].id] = data[u];
    }
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
    getAbsencesBetween(
            begin.format('YYYY-MM-DD'),
            end.format('YYYY-MM-DD'),
            [],
            function(ranges) {
                var event_objects = new Array();
                var logged_user_absences = new Array();
                for (i in ranges) {
                    event_objects[i] = {
                        id: ranges[i].id,
                        title: global_users_by_id[ranges[i].user_id].full_name,
                        start: ranges[i].begin,
                        end: ranges[i].end,
                        user_id: ranges[i].user_id
                    };
                    // pull out current user's absences
                    if (global_logged_user_id === ranges[i].user_id) {
                        logged_user_absences.push(ranges[i]);
                    }
                }
                // copy data to global arrays, for convenience of other calculations
                global_absences = ranges;
                global_logged_user_absences = logged_user_absences;
                console.debug('saved ' + ranges.length + ' ranges');
                console.debug('saved ' + logged_user_absences.length + ' logged user\'s ranges');
                // now also get holidays for the given range
                getHolidaysBetween(
                        begin.format('YYYY-MM-DD'),
                        end.format('YYYY-MM-DD'),
                        function(holidays) {
                            for (var i in holidays) {
                                event_objects.push({
                                    id: 'holiday' + holidays[i].id,
                                    title: holidays[i].name,
                                    start: holidays[i].day,
                                    end: holidays[i].day,
                                    color: 'red',
                                    user_id: global_event_is_holiday
                                });
                            }
                            saveHolidays(holidays);
                            callback(event_objects);
                        }
                );
            }
    );
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

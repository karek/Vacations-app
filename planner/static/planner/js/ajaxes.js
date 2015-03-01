// Global arrays used by all scripts
global_users = new Array();
global_users_by_id = new Array();
// These arrays will hold absences currently pulled in by the calendar (most likely the visible ones)
global_absences = new Array();
global_logged_users_absences = new Array();

// Get and save absence ranges, and execute the function on them.
// Pass empty users array to get everyone's absences.
function getAbsencesBetween(begin, end, users, on_success) {
    var req_url = global_range_url + '?begin=' + begin + '&end=' + end
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
                var logged_users_absences = new Array();
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
                        logged_users_absences.push(ranges[i]);
                    }
                }
                callback(event_objects);
                // copy data to global arrays, for convenience of other calculations
                global_absences = ranges;
                global_logged_users_absences = logged_users_absences;
                console.debug('saved ' + ranges.length + ' ranges');
                console.debug('saved ' + logged_users_absences.length + ' logged user\'s ranges');
            }
    );
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

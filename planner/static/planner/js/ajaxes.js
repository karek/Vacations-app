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

global_users = new Array();
global_users_by_id = new Array();
global_users_loaded = false;

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
                for (i in ranges) {
                    event_objects[i] = {
                        id: ranges[i].id,
                        title: global_users_by_id[ranges[i].user_id].full_name,
                        start: ranges[i].begin,
                        end: ranges[i].end
                    };
                }
                callback(event_objects);
            }
    );
}

// add received ranges to the debug list
// TODO: remove this in the future
function debugShowRanges(ranges) {
    console.debug('showing ' + ranges.length + ' ranges');
    $('#all_ranges').append('<hr />');
    for (i in ranges) {
        console.debug('appending range, i=' + i);
        var uid = ranges[i].user_id;
        var li = '<li>from ' + ranges[i].begin + ' to ' + ranges[i].end + ', by '
            + global_users_by_id[uid].full_name + ' (' + global_users_by_id[uid].email + ')'
            + '</li>';
        $('#all_ranges').append(li);
    }
}

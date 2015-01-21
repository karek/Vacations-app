global_ranges = new Array();

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
            global_ranges = data;
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

// Get and save users (and execute callback).
function getAllUsers(on_success) {
    var req_url = global_user_url;
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            console.debug('ajax returned ' + data.length + ' users');
            global_users = data;
            for (u in data) {
                data[u]['full_name'] = data[u].first_name + ' ' + data[u].last_name;
                console.debug('saving user ' + data[u].email);
                global_users_by_id[data[u].id] = data[u];
            }
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting users!');
        }
    });
}


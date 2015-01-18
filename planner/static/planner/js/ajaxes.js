// Global range array
g_ranges = new Array();

// Get and save absence ranges, and execute the function on them.
// Pass empty users array to get everyone's absences.
function getAbsencesBetween(begin, end, users, on_success) {
    var req_url = '/get-ranges-between/?begin=' + begin + '&end=' + end;
    for (var i in users) req_url += '&user[]=' + users[i];
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            data = $.parseJSON(data);
            console.debug('ajax returned: ' + data.length + ' absence ranges');
            g_ranges = data;
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting absences!');
        }
    });
}

// Global user arrays
g_users = new Array();
g_users_by_id = new Array();

// Get and save users (and execute callback).
function getAllUsers(on_success) {
    var req_url = '/get-all-users/';
    console.debug('ajax url: ' + req_url);
    $.ajax({
        type: "GET",
        url: req_url,
        success: function(data) {
            data = $.parseJSON(data);
            console.debug('ajax returned ' + data.length + ' users');
            g_users = data;
            for (u in data) {
                console.debug('saving user ' + data[u].email);
                g_users_by_id[data[u].id] = data[u];
            }
            on_success(data);
        },
        error: function(jqxhr, txt_status, error) {
            console.debug('ajax error: ' + error + ', text: ' + jqxhr.responseText);
            alert('Error getting users!');
        }
    });
}


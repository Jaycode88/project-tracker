// Fetch Commits
$(document).ready(function () {
    $('#fetch-commits').click(function () {
        var projectId = $(this).data('project-id');
        $.ajax({
            url: $(this).data('fetch-url'),
            type: 'POST',
            headers: { 'X-CSRFToken': $(this).data('csrf-token') },
            success: function (response) {
                if (response.status === 'success') {
                    $('#fetch-status').text(response.message).css('color', 'green');
                    location.reload(); // Reload the page to show the updated commit data
                } else {
                    $('#fetch-status').text(response.message).css('color', 'red');
                }
            },
            error: function () {
                $('#fetch-status').text('An error occurred while fetching commits.').css('color', 'red');
            }
        });
    });
});

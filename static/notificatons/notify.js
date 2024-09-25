document.addEventListener('DOMContentLoaded', function() {
    fetch('{% url "users:unread_count" %}', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const badge = document.getElementById('notification-badge');
        badge.textContent = data.unread_count;

        if (data.unread_count > 0) {
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    })
    .catch(error => console.error('Error fetching notifications:', error))
});

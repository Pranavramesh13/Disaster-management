// Main JavaScript file for the disaster management system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add alert creation handler if on alerts page
    const alertForm = document.getElementById('createAlertForm');
    if (alertForm) {
        alertForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(alertForm);
            const alertData = {
                message: formData.get('message'),
                location: formData.get('location'),
                severity: formData.get('severity')
            };

            try {
                const response = await fetch('/api/create-alert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(alertData)
                });

                if (response.ok) {
                    const result = await response.json();
                    showNotification('Alert created successfully!', 'success');
                    // Reload the page to show new alert
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification('Failed to create alert', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('An error occurred', 'error');
            }
        });
    }
});

function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
}

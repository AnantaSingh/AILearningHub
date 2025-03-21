function toggleBookmark(button) {
    const card = button.closest('.resource-card');
    const resourceData = {
        url: card.dataset.url,
        title: card.dataset.title,
        description: card.dataset.description,
        source: card.dataset.source,
        resource_type: card.dataset.resourceType || 'GITHUB'
    };

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/bookmarks/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(resourceData),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button appearance
            button.classList.toggle('bookmarked');
            
            // If we're on the bookmarks page, remove the card
            if (window.location.pathname.includes('/bookmarks/')) {
                card.remove();
                
                // If no more bookmarks, show empty message
                if (document.querySelectorAll('.resource-card').length === 0) {
                    const container = document.querySelector('.bookmarks-container');
                    container.innerHTML = '<div class="alert alert-info">No bookmarks yet!</div>';
                }
            }
            
            showAlert('success', data.message);
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Failed to update bookmark: ' + error.message);
    });
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
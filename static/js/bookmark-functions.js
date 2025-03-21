function getCsrfToken() {
    // Try to get the token from the cookie first
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    // If not in cookie, try to get from form or meta tag
    return cookieValue || 
           document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.content;
}

function toggleBookmark(button) {
    // Check if user is authenticated
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    if (!isAuthenticated) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        return;
    }

    const card = button.closest('.resource-card');
    const resourceData = {
        url: card ? card.dataset.url : button.dataset.url,
        title: card ? card.dataset.title : button.dataset.title,
        description: card ? card.dataset.description : button.dataset.description,
        source: card ? card.dataset.source : button.dataset.source,
        resource_type: card ? (card.dataset.resourceType || 'GITHUB') : (button.dataset.resourceType || 'GITHUB')
    };

    let metadata = {};
    try {
        metadata = JSON.parse(button.dataset.metadata || '{}');
    } catch (e) {
        console.error('Error parsing metadata:', e);
    }
    resourceData.metadata = metadata;

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        showAlert('danger', 'CSRF token not found. Please refresh the page.');
        return;
    }

    fetch('/bookmarks/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(resourceData),
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
            return;
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            if (window.location.pathname.includes('/bookmarks/')) {
                // If on bookmarks page, remove the card
                if (card) {
                    card.remove();
                    if (document.querySelectorAll('.resource-card').length === 0) {
                        const container = document.querySelector('.bookmarks-container');
                        container.innerHTML = '<div class="alert alert-info">No bookmarks yet!</div>';
                    }
                }
            } else {
                // Update button appearance on other pages
                const isBookmarked = button.classList.contains('btn-primary');
                if (!isBookmarked) {
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-primary');
                    button.innerHTML = '<i class="fas fa-bookmark"></i> Bookmarked';
                } else {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-outline-primary');
                    button.innerHTML = '<i class="far fa-bookmark"></i> Bookmark';
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

function removeBookmark(button) {
    const data = {
        url: button.dataset.url
    };

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value || 
                      document.querySelector('meta[name="csrf-token"]').content;

    fetch('/bookmarks/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        if (result.status === 'success') {
            const bookmarkItem = button.closest('.bookmark-item');
            if (bookmarkItem) {
                bookmarkItem.remove();
                
                const bookmarksList = document.querySelector('.row');
                if (!bookmarksList.querySelector('.bookmark-item')) {
                    bookmarksList.innerHTML = `
                        <div class="col-12 text-center">
                            <p class="lead">No bookmarks yet.</p>
                            <a href="/" class="btn btn-primary">Search Resources</a>
                        </div>
                    `;
                }
            }
            showAlert('success', 'Bookmark removed successfully');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Error removing bookmark');
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
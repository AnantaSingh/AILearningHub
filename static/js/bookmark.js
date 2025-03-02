function bookmarkResource(resourceData) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/bookmarks/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams(resourceData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'created') {
            alert('Resource bookmarked successfully!');
        } else {
            alert('Resource already bookmarked!');
        }
    })
    .catch(error => console.error('Error:', error));
}

function toggleBookmark(btn) {
    // Check if user is authenticated
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    if (!isAuthenticated) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        return;
    }

    const isBookmarked = btn.classList.contains('btn-primary');
    let metadata = {};
    
    try {
        metadata = JSON.parse(btn.dataset.metadata || '{}');
    } catch (e) {
        console.error('Error parsing metadata:', e);
    }

    const data = {
        url: btn.dataset.url,
        title: btn.dataset.title,
        description: btn.dataset.description,
        source: btn.dataset.source,
        metadata: metadata
    };

    console.log('Bookmark data being sent:', {
        url: data.url,
        title: data.title,
        description: data.description,
        source: data.source,
        metadata: data.metadata
    });

    console.log('Sending data:', data);

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    fetch('/bookmarks/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.redirected) {
            // User is not authenticated, redirect to login
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
            return;
        }
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        if (result) {  // Only process if we got a result (not redirected)
            if (!isBookmarked) {
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
                btn.innerHTML = '<i class="fas fa-bookmark"></i> Bookmarked';
            } else {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
                btn.innerHTML = '<i class="far fa-bookmark"></i> Bookmark';
            }
            console.log('Bookmark status:', result.status);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (error.message.includes('not valid JSON')) {
            // Likely not authenticated
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        } else {
            alert('Error saving bookmark. Please try again.');
        }
    });
}

function removeBookmark(btn) {
    const data = {
        url: btn.dataset.url
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

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
            // Remove the bookmark item from the DOM
            const bookmarkItem = btn.closest('.bookmark-item');
            if (bookmarkItem) {
                bookmarkItem.remove();
                
                // Check if there are any bookmarks left
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
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error removing bookmark');
    });
} 
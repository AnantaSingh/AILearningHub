console.log('GitHub Explorer JS loaded');  // Debug log

// Define the function in global scope
window.loadTrendingRepos = function() {
    console.log("Loading trending repos...");
    const trendingSection = document.getElementById('github-trending');
    const reposContainer = document.getElementById('trending-repos');
    
    if (!trendingSection || !reposContainer) {
        console.error("Required elements not found!");
        return;
    }
    
    trendingSection.style.display = 'block';
    reposContainer.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"></div></div>';

    console.log("Fetching from API...");
    fetch('/api/github/trending/')
        .then(response => {
            console.log("Raw API Response:", response);
            return response.json();
        })
        .then(data => {
            console.log("Parsed data:", data);
            console.log("Data type:", typeof data);
            console.log("Data.data type:", typeof data.data);
            console.log("Is data.data an array?", Array.isArray(data.data));

            // Ensure we have valid data
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }

            // Convert data to array if it's not already
            const repos = Array.isArray(data.data) ? data.data : [];
            console.log("Final repos array:", repos);

            if (repos.length === 0) {
                reposContainer.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-info">
                            No repositories found. Please try again later.
                        </div>
                    </div>`;
                return;
            }

            let reposHtml = '';
            repos.forEach(repo => {
                if (!repo) return;
                reposHtml += `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100 border-primary">
                            <div class="card-header bg-primary text-white d-flex justify-content-between">
                                <i class="fab fa-github"></i>
                                <span>${repo.stars || 0} ⭐</span>
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">${repo.name || 'Unnamed Repository'}</h5>
                                <p class="card-text">${repo.description || 'No description available'}</p>
                                ${repo.language ? `<span class="badge bg-secondary">${repo.language}</span>` : ''}
                            </div>
                            <div class="card-footer">
                                <a href="${repo.url}" class="btn btn-outline-primary btn-sm" target="_blank">View Repository</a>
                                <button onclick="saveResource({
                                    url: '${repo.url}',
                                    title: '${repo.name.replace(/'/g, "\\'")}',
                                    description: '${(repo.description || '').replace(/'/g, "\\'")}',
                                    source: 'GitHub'
                                })" class="btn btn-outline-success btn-sm">
                                    <i class="fas fa-bookmark"></i> Save
                                </button>
                            </div>
                        </div>
                    </div>`;
            });

            reposContainer.innerHTML = reposHtml || `
                <div class="col-12">
                    <div class="alert alert-info">
                        No repositories to display.
                    </div>
                </div>`;
        })
        .catch(error => {
            console.error('Detailed error:', error);
            console.error('Error stack:', error.stack);
            reposContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <p>Error loading repositories: ${error.message}</p>
                        <p>Please make sure:</p>
                        <ul>
                            <li>GitHub Access Token is properly configured</li>
                            <li>You have an active internet connection</li>
                            <li>The GitHub API is accessible</li>
                        </ul>
                    </div>
                </div>`;
        });
};

// Add event listener when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, setting up GitHub Explorer...");
    const trendingSection = document.getElementById('github-trending');
    
    // Only initialize if we're on a page with the trending section
    if (trendingSection) {
        console.log("Trending section found, loading repos...");
        loadTrendingRepos();
    } else {
        console.log("Not on GitHub Explorer page");
    }
});

function saveResource(resourceData) {
    // Create form data
    const formData = new FormData();
    for (const key in resourceData) {
        formData.append(key, resourceData[key]);
    }

    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    return fetch('/resources/save/', {  // Updated endpoint
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', 'Resource saved successfully!');
        } else {
            throw new Error(data.message || 'Failed to save resource');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Failed to save resource: ' + error.message);
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
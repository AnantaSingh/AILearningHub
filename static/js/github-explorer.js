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
            console.log("API Response:", response);
            return response.json();
        })
        .then(repos => {
            console.log("Repos received:", repos);
            reposContainer.innerHTML = repos.map(repo => `
                <div class="col-md-6 mb-4">
                    <div class="card h-100 border-primary">
                        <div class="card-header bg-primary text-white d-flex justify-content-between">
                            <i class="fab fa-github"></i>
                            <span>${repo.stars} ⭐</span>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${repo.name}</h5>
                            <p class="card-text">${repo.description || 'No description available'}</p>
                            ${repo.language ? `<span class="badge bg-secondary">${repo.language}</span>` : ''}
                        </div>
                        <div class="card-footer">
                            <a href="${repo.url}" class="btn btn-outline-primary btn-sm" target="_blank">View Repository</a>
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error:', error);
            reposContainer.innerHTML = '<div class="col-12"><div class="alert alert-danger">Error loading repositories</div></div>';
        });
};

// Add event listener when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, setting up GitHub Explorer...");
    const explorerBtn = document.getElementById('github-explorer-btn');
    if (explorerBtn) {
        console.log("Explorer button found, adding click listener");
        explorerBtn.addEventListener('click', loadTrendingRepos);
    } else {
        console.error("Explorer button not found!");
    }
}); 
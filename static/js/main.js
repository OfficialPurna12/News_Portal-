// static/js/main.js
// Frontend JavaScript for News Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initSearch();
    
    // Initialize social sharing
    initSocialSharing();
    
    // Initialize category filtering
    initCategoryFiltering();
});

// Search functionality
function initSearch() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const sidebarSearch = document.getElementById('sidebarSearch');
    const sidebarSearchBtn = document.getElementById('sidebarSearchBtn');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/all-news?q=${encodeURIComponent(query)}`;
            }
        });
    }
    
    if (sidebarSearchBtn && sidebarSearch) {
        sidebarSearchBtn.addEventListener('click', function() {
            const query = sidebarSearch.value.trim();
            if (query) {
                window.location.href = `/all-news?q=${encodeURIComponent(query)}`;
            }
        });
        
        sidebarSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = sidebarSearch.value.trim();
                if (query) {
                    window.location.href = `/all-news?q=${encodeURIComponent(query)}`;
                }
            }
        });
    }
    
    // Real-time search suggestions
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    fetchSearchSuggestions(query);
                }
            }, 300);
        });
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                hideSearchResults();
            }
        });
    }
}

// Fetch search suggestions from API
function fetchSearchSuggestions(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}

// Display search results
function displaySearchResults(results) {
    hideSearchResults();
    
    if (results.length === 0) return;
    
    const searchInput = document.getElementById('searchInput');
    const searchContainer = searchInput.closest('.search-container') || createSearchContainer(searchInput);
    
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'search-results';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.innerHTML = `
            <h6 class="mb-1">${result.title}</h6>
            <p class="small text-muted mb-0">${result.content.substring(0, 80)}...</p>
            <small class="text-primary">${result.category} • ${new Date(result.date_created).toLocaleDateString()}</small>
        `;
        
        resultItem.addEventListener('click', function() {
            window.location.href = `/news/${result._id}`;
        });
        
        resultsContainer.appendChild(resultItem);
    });
    
    searchContainer.appendChild(resultsContainer);
}

// Create search container if it doesn't exist
function createSearchContainer(searchInput) {
    const container = document.createElement('div');
    container.className = 'search-container position-relative';
    searchInput.parentNode.insertBefore(container, searchInput);
    container.appendChild(searchInput);
    return container;
}

// Hide search results
function hideSearchResults() {
    const existingResults = document.querySelector('.search-results');
    if (existingResults) {
        existingResults.remove();
    }
}

// Social sharing functionality
function initSocialSharing() {
    // Functions are defined in the news_detail.html template
    // This is just a placeholder for future enhancements
}

// Category filtering
function initCategoryFiltering() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const category = this.value;
            const currentUrl = new URL(window.location.href);
            
            if (category) {
                currentUrl.searchParams.set('category', category);
            } else {
                currentUrl.searchParams.delete('category');
            }
            
            // Reset to page 1 when changing category
            currentUrl.searchParams.delete('page');
            
            window.location.href = currentUrl.toString();
        });
    }
}

// Utility function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading state to buttons
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="loading"></span> Loading...';
    }
});
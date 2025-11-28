// static/js/admin.js
// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin functionality
    initAdminForms();
    initDataTables();
    initImageUpload();
    initRichTextEditor();
});

// Admin form handling
function initAdminForms() {
    // Confirm before delete
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
}

// Initialize data tables (for future enhancement)
function initDataTables() {
    // This would initialize DataTables if the library is included
    // For now, we'll just add basic sorting functionality
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, header.cellIndex, header.dataset.sort);
            });
        });
    });
}

// Basic table sorting
function sortTable(table, column, order) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();
        
        if (order === 'asc') {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    // Clear existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Append sorted rows
    sortedRows.forEach(row => tbody.appendChild(row));
    
    // Update sort order for next click
    const header = table.querySelectorAll('th')[column];
    header.dataset.sort = order === 'asc' ? 'desc' : 'asc';
}

// Image upload preview
function initImageUpload() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept^="image/"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create or update preview
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview mt-2';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Rich text editor initialization
function initRichTextEditor() {
    const textareas = document.querySelectorAll('textarea.rich-text-editor');
    textareas.forEach(textarea => {
        // This is a basic implementation
        // In production, you would integrate a proper rich text editor like TinyMCE or CKEditor
        textarea.addEventListener('input', function() {
            // Auto-resize
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Add basic formatting buttons
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar mb-2';
        toolbar.innerHTML = `
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="bold"><i class="fas fa-bold"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="italic"><i class="fas fa-italic"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="underline"><i class="fas fa-underline"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertUnorderedList"><i class="fas fa-list-ul"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertOrderedList"><i class="fas fa-list-ol"></i></button>
        `;
        
        textarea.parentNode.insertBefore(toolbar, textarea);
        
        // Add event listeners to toolbar buttons
        toolbar.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function() {
                const command = this.dataset.command;
                document.execCommand(command, false, null);
                textarea.focus();
            });
        });
    });
}

// Utility function to show notifications
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.main-content').insertBefore(alert, document.querySelector('.main-content').firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// AJAX helper function
function ajaxRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const config = { ...defaults, ...options };
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('show');
}

// Initialize chart (for future analytics)
function initChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    // This would initialize a chart using Chart.js or similar library
    // Placeholder for future implementation
}
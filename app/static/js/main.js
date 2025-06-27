// Project Manager - Main JavaScript

$(document).ready(function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
    
    // Task status update via AJAX
    $('.task-status-update').on('change', function() {
        const taskId = $(this).data('task-id');
        const newStatus = $(this).val();
        
        $.ajax({
            url: `/tasks/${taskId}/update-status`,
            method: 'POST',
            data: { status: newStatus },
            success: function(response) {
                if (response.success) {
                    // Show success message
                    const alertHtml = `
                        <div class="alert alert-success alert-dismissible fade show">
                            Task status updated successfully!
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    $('.container:first').prepend(alertHtml);
                    
                    // Auto-dismiss after 3 seconds
                    setTimeout(function() {
                        $('.alert-dismissible').alert('close');
                    }, 3000);
                }
            },
            error: function(xhr) {
                // Show error message
                let errorMessage = 'An error occurred while updating the task status.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                
                const alertHtml = `
                    <div class="alert alert-danger alert-dismissible fade show">
                        ${errorMessage}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                $('.container:first').prepend(alertHtml);
            }
        });
    });
    
    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Date range validation for project dates
    $('#end_date').on('change', function() {
        const startDate = new Date($('#start_date').val());
        const endDate = new Date($(this).val());
        
        if (endDate < startDate) {
            alert('End date cannot be earlier than start date!');
            $(this).val('');
        }
    });
    
    // Search functionality
    $('#search-input').on('keyup', function() {
        const searchTerm = $(this).val().toLowerCase();
        
        $('.searchable-item').each(function() {
            const text = $(this).text().toLowerCase();
            if (text.indexOf(searchTerm) > -1) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
}); 
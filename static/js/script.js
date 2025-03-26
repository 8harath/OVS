document.addEventListener('DOMContentLoaded', function() {
    // Add any client-side interactions here
    console.log('JavaScript loaded');

    // Example: Hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.display = 'none';
        }, 5000);
    });
});
// Go to Top button functionality
document.addEventListener('DOMContentLoaded', function() {
    let goToTopBtn = document.getElementById('goToTopBtn');

    if (goToTopBtn) { // Ensure the button exists before adding event listeners
        // Show or hide the button based on scroll position
        window.onscroll = function() {
            if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
                goToTopBtn.style.display = 'block';
            } else {
                goToTopBtn.style.display = 'none';
            }
        };

        // When the user clicks on the button, scroll to the top of the document smoothly
        goToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

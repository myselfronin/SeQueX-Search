  document.getElementById('search-form').onsubmit = function() {
        var query = document.getElementById('search-box').value.trim();
        if (query === '') {
            alert('Please enter a search query.');
            return false; // Prevent form submission
        }
        return true; // Allow form submission
    };
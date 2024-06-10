function like(postId) {
    const likeCount = document.getElementById('like-count-' + postId);
    const likeButton = document.getElementById('like-button-' + postId);

    fetch('/like-post/' + postId, { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
            likeCount.innerHTML = data.likes;
            if (data.liked) {
                likeButton.innerHTML = '<i class="material-symbols-outlined">thumb_up</i>';
            } else {
                likeButton.innerHTML = '<i class="material-symbols-outlined">thumb_up</i>';
            }
        })
        .catch((e) => alert("Could not like post."));
}

// Function to toggle the visibility of comments
function toggleComments(postId) {
    const commentsSection = document.getElementById('comments-' + postId);
    const toggleButton = document.querySelector('.toggle-comments-button[onclick="toggleComments(\'' + postId + '\')"]');

    // Toggle the display style
    if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
        commentsSection.style.display = 'block';
        toggleButton.textContent = 'Hide Comments';
    } else {
        commentsSection.style.display = 'none';
        toggleButton.textContent = 'Show Comments';
    }
}

// Ensure the page has fully loaded before executing JavaScript
document.addEventListener("DOMContentLoaded", function() {
    const commentButtons = document.querySelectorAll('.toggle-comments-button');
    commentButtons.forEach(button => {
        // Initialize all comment sections to be hidden
        const postId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        document.getElementById('comments-' + postId).style.display = 'none';
    });
});

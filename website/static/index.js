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
let postToDelete = null

document.addEventListener('click', function (e) {
    if (e.target.matches('.confirmDelete-btn')) {
        const deleteModal = document.getElementById('deletePostModal');
        postToDelete = e.target.getAttribute('data-post-id')
        console.log(postToDelete)
        deleteModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
});

function cancelDeletePost() {
    postToDelete = null;
    const deleteModal = document.getElementById('deletePostModal');
    deleteModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

//delete post
function deletePost() {
    if (postToDelete) {
        const postId = postToDelete;
        const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
        const headers = {};
        if (csrf) headers['X-CSRFToken'] = csrf.value;

        fetch(`/api/delete/${postId}/`, { method: 'POST', headers: headers })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById(`post-${postId}`);
                if (el) {

                    
                    el.style.transition = 'opacity 400ms ease, transform 400ms ease, height 400ms ease, margin 400ms ease, padding 400ms ease';
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(-12px)';
                    el.style.pointerEvents = 'none';
                    
                    el.style.height = el.offsetHeight + 'px';
                    
                    void el.offsetHeight;
                    el.style.height = '0px';
                    el.style.marginBottom = '0px';
                    el.style.paddingTop = '0px';
                    el.style.paddingBottom = '0px';
                    setTimeout(function () { el.remove(); }, 450);
                    
                }
                cancelDeletePost();
            } else {
                alert('Delete failed: ' + (data.error || 'unknown'));
            }
        }).catch(err => {
            alert('Error deleting post');
            console.error(err);
        });
    }
}


document.addEventListener('click', function (e) {
    var btn = e.target.closest('.like-btn');
    if (!btn) return;
    var postId = btn.getAttribute('data-post-id');
    var csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    var headers = {};
    if (csrf) headers['X-CSRFToken'] = csrf.value;

    fetch(`/api/like/${postId}/`, {
        method: 'POST',
        headers: headers
    }).then(r => r.json()).then(data => {
        if (data.success) {
            var icon = btn.querySelector('i');
            if (icon) {
                if (data.liked) {
                    icon.classList.remove('far');
                    icon.classList.add('fas', 'text-red-500');
                } else {
                    icon.classList.remove('fas', 'text-red-500');
                    icon.classList.add('far');
                }
            }
        } else {
            alert('Error liking post: ' + (data.error || 'unknown'));
        }
    });
});
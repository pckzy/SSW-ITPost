let postToDelete = null

document.addEventListener('click', function (e) {
    if (e.target.matches('.comment-btn')) {
        const postId = e.target.getAttribute('data-post-id');
        openCommentModal(postId);
    } else if (e.target.matches('.confirmDelete-btn')) {
        const deleteModal = document.getElementById('deletePostModal');
        postToDelete = e.target.getAttribute('data-post-id')
        console.log(postToDelete)
        deleteModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
});


function openCommentModal(postId) {
    fetch(`/api/comments/${postId}/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector('#commentModal .post-title').textContent = data.post_title;

            const commentList = document.querySelector('#commentModal .comments-list');
            commentList.innerHTML = '';

            if (data.comments.length === 0) {
                const commentHtml = `
                    <div id="none-comment" class="text-center py-2">
                        <p class="text-sm text-gray-500 font-medium">
                            ยังไม่มีความคิดเห็น
                        </p>
                    </div>
                `
                commentList.innerHTML += commentHtml;
            } else {
            data.comments.forEach(comment => {
                const commentHtml = `
                    <div class="mb-3">
                        <div class="flex items-center space-x-3">
                            <img class="w-10 h-10 rounded-full border-2 border-blue-100 object-cover" 
                                src="/media/${comment.image}" alt="User">
                            <div class="flex-1">
                                <div class="flex items-baseline gap-2 mb-1">
                                    <a href="/profile/${comment.username}"><span class="font-medium text-gray-800 text-sm">${comment.user_full_name}</span></a>
                                    <span class="text-xs text-gray-500">@${comment.username}</span>
                                    <span class="text-xs text-gray-500">${comment.created_at_human}</span>
                                </div>
                                <p class="text-gray-700 text-sm leading-relaxed">
                                    ${comment.content}
                                </p>
                            </div>
                        </div>
                    </div>
                `;
                commentList.innerHTML += commentHtml;
            });
            }
            document.getElementById('commentModal').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            

            const form = document.getElementById('commentForm');
            form.setAttribute("data-post-id", postId);
            
            form.replaceWith(form.cloneNode(true));
            const newForm = document.getElementById('commentForm');
            
            newForm.addEventListener("submit", function (e) {
                e.preventDefault();
                const csrfToken = document.getElementById('csrfToken').value;
                const formData = new FormData(this);
                
                fetch(`/api/comments/${postId}/`, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": csrfToken
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const none_comment = document.getElementById('none-comment')
                        const comment_count = document.getElementById(`comment-${postId}-count`)
                        if (none_comment) {
                            none_comment.classList.add('hidden')
                        }
                        if (comment_count) {
                            comment_count.innerText = Number(comment_count.innerText) + 1
                        }
                        const comments_list = document.getElementById('comments-list')
                        const newComment = document.createElement('div');
                        newComment.className = 'mb-3';
                        newComment.innerHTML = `
                            <div class="flex items-center space-x-3">
                                <img class="w-10 h-10 rounded-full border-2 border-blue-100 object-cover" 
                                    src="/media/${data.comment.image}" alt="User">
                                <div class="flex-1">
                                    <div class="flex items-baseline gap-2 mb-1">
                                        <a href="/profile/${data.comment.username}"><span class="font-medium text-gray-800 text-sm">${data.comment.user_full_name}</span></a>
                                        <span class="text-xs text-gray-500">@${data.comment.username}</span>
                                        <span class="text-xs text-gray-500">${data.comment.created_at_human}</span>
                                    </div>
                                    <p class="text-gray-700 text-sm leading-relaxed">
                                        ${data.comment.content}
                                    </p>
                                </div>
                            </div>
                        `;
                        comments_list.prepend(newComment)
                        this.reset();
                    } else {
                        alert("Error: " + JSON.stringify(data.errors));
                    }
                });
            });
        } else {
            alert('no post');
        }
    })
}


function closeCommentModal() {
    const modal = document.getElementById('commentModal');
    modal.classList.add('hidden');
    const form = document.getElementById('commentForm');
    form.reset()
    document.body.style.overflow = 'auto';
}

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

                    // fade out + slide up animation before removing
                    el.style.transition = 'opacity 400ms ease, transform 400ms ease, height 400ms ease, margin 400ms ease, padding 400ms ease';
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(-12px)';
                    el.style.pointerEvents = 'none';
                    // also collapse height to avoid gap
                    el.style.height = el.offsetHeight + 'px';
                    // trigger reflow then set height to 0
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

// Like button
document.addEventListener('click', function (e) {
    var btn = e.target.closest('.like-btn');
    if (!btn) return;
    var postId = btn.getAttribute('data-post-id');
    var csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    var headers = {};
    console.log(csrf)
    if (csrf) headers['X-CSRFToken'] = csrf.value;

    fetch(`/api/like/${postId}/`, {
        method: 'POST',
        headers: headers
    }).then(r => r.json()).then(data => {
        if (data.success) {
            var countEl = btn.querySelector('.like-count');
            if (countEl) countEl.textContent = data.count;
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
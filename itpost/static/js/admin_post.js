let typingTimer;
const doneTypingInterval = 500;

const search = document.getElementById('search');
const filter = document.getElementById('status-select');
const currentPath = window.location.pathname;

if (search && search.value !== '') {
  const endPosition = search.value.length;
  search.setSelectionRange(endPosition, endPosition);
  search.focus();
}

search.addEventListener('keyup', () => {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(doneTyping, doneTypingInterval);
});

filter.addEventListener('change', () => {
  doneTyping();
});

function doneTyping() {
  const searchValue = search.value.trim();
  const filterValue = filter.value;

  const query = new URLSearchParams();
  if (searchValue) query.append('search', searchValue);
  if (filterValue) query.append('status', filterValue);

  window.location.href = `${currentPath}?${query.toString()}`;
}

function updatePostStatus(btnElement, action) {
    const postId = btnElement.getAttribute('data-post-id')
    const url = action === 'approve'
        ? `/api/approve/${postId}/`
        : `/api/reject/${postId}/`;

    const csrf = document.getElementById('csrfToken').value;

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf,
            "Content-Type": "application/json",
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.success){
            const postRow = document.getElementById(`post-${postId}`);
            const countEl = document.getElementById('postRequestCount');
            const pendingCount = document.getElementById('post-pending-count');
            if (!postRow | !countEl) return;

            const el = document.getElementById(`pending-post-${postId}`);
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

            const statusContainer = postRow.querySelector(".post-status");
            
            
            if (action === "approve") {
                statusContainer.innerHTML = `
                    <span class="px-3 py-1 text-xs rounded-full bg-green-100 text-green-800 whitespace-nowrap">
                        อนุมัติแล้ว
                    </span>
                `;
            } else if (action === "reject") {
                statusContainer.innerHTML = `
                    <span class="px-3 py-1 text-xs rounded-full bg-red-100 text-red-800 whitespace-nowrap">
                        ถูกปฏิเสธ
                    </span>
                `;
            }

            
            let count = parseInt(countEl.textContent);
            count = count - 1;
            countEl.textContent = count;
            pendingCount.textContent = `โพสต์ที่รออนุมัติจำนวน ${count} โพสต์`;
        }
    })
    .catch(err => console.error(err));
}

function deletePost(btnElement) {
    const postId = btnElement.getAttribute('data-post-id')
    const csrf = document.getElementById('csrfToken').value;
    fetch(`/api/delete/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json'
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const postRow = document.getElementById(`post-${postId}`);
            const countEl = document.getElementById('allPostCount');
            if (!postRow | !countEl) return;

            // animation
            const rowHeight = postRow.offsetHeight;
            postRow.style.transition = 'opacity 0.5s ease, height 0.5s ease, padding 0.5s ease';
            postRow.style.height = rowHeight + 'px';
            postRow.style.opacity = '1';

            // trigger reflow (บังคับ browser register style ก่อนเปลี่ยน)
            postRow.offsetHeight;

            // เริ่ม animation
            postRow.style.opacity = '0';
            postRow.style.height = '0';
            postRow.style.paddingTop = '0';
            postRow.style.paddingBottom = '0';

            // ลบ element หลัง animation เสร็จ
            postRow.addEventListener('transitionend', () => {
                postRow.remove();
            }, { once: true });

            let count = parseInt(countEl.textContent);
            count = count - 1;
            countEl.textContent = count;
        }
    })
    .catch(err => console.error(err));
}


function togglePostApprove() {
    const postApproveDiv = document.getElementById('post-approve-div')
    if (postApproveDiv.classList.contains('max-h-0')) {
        postApproveDiv.classList.remove('max-h-0')
        postApproveDiv.classList.add('max-h-[2000px]')
    } else {
        postApproveDiv.classList.add('max-h-0')
        postApproveDiv.classList.remove('max-h-[2000px]')
    }
}
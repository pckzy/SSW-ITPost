let enrollToReject = null
let nameToReject = null

document.addEventListener('click', function (e) {
    if (e.target.matches('.rejectEnroll-btn')) {
        const rejectModal = document.getElementById('rejectEnrollModal');
        enrollToReject = e.target.getAttribute('data-enroll-id')
        nameToReject = e.target.getAttribute('data-name')
        console.log(enrollToReject)
        rejectModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        document.getElementById('nameToReject').innerText = nameToReject
    }
});


function cancelRejectEnroll() {
    enrollToReject = null;
    const rejectModal = document.getElementById('rejectEnrollModal');
    rejectModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}


function rejectEnrollment() {
    const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const headers = {};
    if (csrf) headers['X-CSRFToken'] = csrf.value;

    fetch(`/api/enroll_course/${enrollToReject}/`, { method: 'DELETE', headers: headers })
        .then(r => r.json())
        .then(data => {
            console.log('API response:', data);
            if (data.success) {
                const el = document.getElementById(`enroll-${enrollToReject}`);
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
                const std_count = document.getElementById('std-count')
                std_count.innerText = Number(std_count.innerText) - 1
                cancelRejectEnroll();
            } else {
                alert('Approve failed: ' + (data.error || 'unknown'));
            }
        }).catch(err => {
            alert('Error approve post');
            console.error(err);
        });
}
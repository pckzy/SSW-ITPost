function openModel(enrollId) {
        document.getElementById(`rejectModel-${enrollId}`).classList.remove("hidden");
    }

function closeModel(enrollId) {
        document.getElementById(`rejectModel-${enrollId}`).classList.add("hidden");
    }

function rejectEnrollment(enrollId) {
    console.log(enrollId)
    const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const headers = {};
    if (csrf) headers['X-CSRFToken'] = csrf.value;

    fetch(`/api/enroll_course/${enrollId}/`, { method: 'DELETE', headers: headers })
        .then(r => r.json())
        .then(data => {
            console.log('API response:', data);
            if (data.success) {
                const el = document.getElementById(`enroll-${enrollId}`);
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
                const std_count = document.getElementById('std-count')
                std_count.innerText = Number(std_count.innerText) - 1
                closeModel(enrollId);
            } else {
                alert('Approve failed: ' + (data.error || 'unknown'));
            }
        }).catch(err => {
            alert('Error approve post');
            console.error(err);
        });
}
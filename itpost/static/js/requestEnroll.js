let courseId = null

function openModal(btnElement) {
    const enrollModal = document.getElementById('enrollModal');
    courseId = btnElement.getAttribute('data-course-id')
    console.log(courseId)
    enrollModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}


function cancelEnrollCourse() {
    courseId = null;
    const enrollModal = document.getElementById('enrollModal');
    enrollModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

function enrollCourse() {
    if (courseId) {
        console.log(courseId)
        const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
        const headers = {};
        if (csrf)
            headers['X-CSRFToken'] = csrf.value;

        fetch(`/api/enroll_course/${courseId}/`, { method: 'POST', headers: headers })
            .then(r => r.json())
            .then(data => {
                console.log('API response:', data);
                if (data.success) {
                    const el = document.getElementById(`course-${courseId}`);
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
                    cancelEnrollCourse()
                } else {
                    alert('Enroll failed: ' + (data.error || 'unknown'));
                }
            }).catch(err => {
                alert('Error enroll course');
                console.error(err);
            });
        }
}
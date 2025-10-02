function approveEnrollment(btnElement) {
    const enrollId = btnElement.getAttribute('data-enroll-id')
    console.log(enrollId)
    const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const headers = {};
    if (csrf) headers['X-CSRFToken'] = csrf.value;

    fetch(`/api/enroll_course/${enrollId}/`, { method: 'PUT', headers: headers })
        .then(r => r.json())
        .then(data => {
            console.log('API response:', data);
            if (data.success) {
                document.querySelectorAll(`.enroll-${enrollId}`).forEach(el => {
                    el.innerText = 'อนุมัติแล้ว';
                    el.classList.remove('bg-red-100', 'text-red-800');
                    el.classList.add('bg-green-100', 'text-green-800');
                });
                document.querySelectorAll(`.enroll-${enrollId}-btn`).forEach(el => {
                    el.classList.add('hidden')
                });
                const std_count = document.getElementById('std-count')
                std_count.innerText = Number(std_count.innerText) + 1
            } else {
                alert('Approve failed: ' + (data.error || 'unknown'));
            }
        }).catch(err => {
            alert('Error approve post');
            console.error(err);
        });
}
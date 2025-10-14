let courseId = null
let courseName = null

function openModal(btnElement) {
    const enrollModal = document.getElementById('enrollModal');
    const setCourseName = document.getElementById('course-name');
    courseId = btnElement.getAttribute('data-course-id')
    courseName = btnElement.getAttribute('data-course-name')
    setCourseName.innerText = courseName
    console.log(courseId)
    enrollModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}


function cancelEnrollCourse() {
    courseId = null;
    courseName = null;
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
                    const divContainer = document.getElementById('enrolled-container');
                    const newEnrollCourse = document.createElement('div');
                    newEnrollCourse.className = 'bg-white rounded-xl shadow-lg hover:shadow-xl transition-all overflow-hidden border-t-4 border-blue-500';
                    newEnrollCourse.innerHTML = `
                        <div class="p-6">
                            <div class="flex justify-between items-start mb-3">
                                <span class="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full">${data.enrollment.course.course_code}</span>

                                <span class="bg-yellow-100 text-yellow-700 text-xs font-semibold px-2 py-1 rounded-full flex items-center">
                                    <i class="fa-solid fa-hourglass-half pr-1"></i>รออนุมัติ
                                </span>
                            </div>
                            <h3 class="text-lg font-semibold text-gray-800 mb-2">${data.enrollment.course.course_name}</h3>
                            <p class="text-gray-600 text-sm mb-4">${data.enrollment.course.description}</p>
                            <p class="text-gray-600 text-sm mb-4"><i class="fa-regular fa-user"></i> ${data.enrollment.course_professor}</p>
                        </div>
                    `;
                    divContainer.append(newEnrollCourse);
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
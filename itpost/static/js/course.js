function toggleCourseForm() {
    const formDiv = document.getElementById('course-form')
    if (formDiv.classList.contains('max-h-0')) {
        formDiv.classList.remove('max-h-0')
        formDiv.classList.add('max-h-[1000px]')
    } else {
        formDiv.classList.add('max-h-0')
        formDiv.classList.remove('max-h-[1000px]')
    }
}


document.getElementById('course-forms').addEventListener('submit', function (e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    payload.allowed_years = Array.from(form.allowed_years.selectedOptions).map(opt => opt.value);
    payload.allowed_majors = Array.from(form.allowed_majors.selectedOptions).map(opt => opt.value);
    payload.allowed_specializations = Array.from(form.allowed_specializations.selectedOptions).map(opt => opt.value);

    fetch('/api/courses/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                toggleCourseForm()
                const container = document.getElementById('coursesList');
                const newCourse = document.createElement('div');
                newCourse.className = 'bg-white rounded-xl shadow-lg hover:shadow-xl transition-all overflow-hidden border-t-4 border-blue-500';
                newCourse.id = `course-${data.course.id}-div`
                newCourse.innerHTML = `
                <div class="p-6">
                    <div class="flex justify-between items-start mb-4">
                        <span class="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full">${data.course.course_code}</span>
                        <button class="text-gray-400 hover:text-gray-600"></button>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">${data.course.title}</h3>
                    <p class="text-gray-600 text-sm mb-4">${data.course.description}</p>

                    <div class="flex items-center justify-between mb-4 text-sm text-gray-500">
                        <div class="flex items-center space-x-1">
                            <i class="fa-regular fa-circle-user"></i>
                            <span>${data.course.student_count} คน</span>
                        </div>
                        <div class="flex items-center space-x-1">
                            <i class="fa-solid fa-bullhorn"></i>
                            <span>${data.course.post_count} ประกาศ</span>
                        </div>
                    </div>

                    <div class="bg-blue-50 rounded-lg p-3 mb-4">
                        <div class="text-xs text-blue-700 mb-1">ประกาศล่าสุด</div>
                        <div class="text-sm font-medium text-blue-900">ยังไม่มีโพสต์</div>
                    </div>

                    <div class="flex space-x-2">
                        <a href="/course/${data.course.course_code}/" class="flex flex-1 justify-center items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all text-sm font-medium">
                            ดูรายละเอียด
                        </a>
                        <a href="/manage_course/edit_course/${data.course.id}/" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all">
                            <i class="fa-regular fa-pen-to-square text-gray-600"></i>
                        </a>
                        <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all">
                            <i data-course-id="${data.course.id}" data-course-name="${data.course.title}" class="confirmDelete-btn fa-regular fa-trash-can text-red-600"></i>
                        </button>
                    </div>
                </div>
            `;
                container.prepend(newCourse);
                form.reset();
            } else {
                if (data.errors.course_code) {
                    document.getElementById('error-course_code').textContent = data.errors.course_code[0];
                }
            }
        });
});



let courseToDelete = null
let nameToDelete = null

document.addEventListener('click', function (e) {
    if (e.target.matches('.confirmDelete-btn')) {
        const deleteModal = document.getElementById('deleteCourseModal');
        const putName = document.getElementById('course-delete-name');
        courseToDelete = e.target.getAttribute('data-course-id')
        nameToDelete = e.target.getAttribute('data-course-name')
        console.log(courseToDelete)
        deleteModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        putName.innerText = nameToDelete;
    }
});


function cancelDeleteCourse() {
    courseToDelete = null;
    nameToDelete = null;
    const deleteModal = document.getElementById('deleteCourseModal');
    deleteModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}


function deleteCourse() {
    fetch(`/api/course/${courseToDelete}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        },
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {

                const courseDiv = document.getElementById(`course-${courseToDelete}-div`);

                if (courseDiv) {
                    const divHeight = courseDiv.offsetHeight;
                    courseDiv.style.transition = 'opacity 0.5s ease, height 0.5s ease, padding 0.5s ease';
                    courseDiv.style.height = divHeight + 'px';
                    courseDiv.style.opacity = '1';

                    courseDiv.offsetHeight;

                    courseDiv.style.opacity = '0';
                    courseDiv.style.height = '0';
                    courseDiv.style.paddingTop = '0';
                    courseDiv.style.paddingBottom = '0';

                    courseDiv.addEventListener('transitionend', () => {
                        courseDiv.remove();
                    }, { once: true });
                }

                cancelDeleteCourse();
            }
        })
        .catch(err => console.error(err));
}
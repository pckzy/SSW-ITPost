let typingTimer;
const doneTypingInterval = 500;

const searchInput = document.getElementById('search');
const currentPath = window.location.pathname;

if (searchInput && searchInput.value !== '') {
    const endPosition = searchInput.value.length;
    searchInput.setSelectionRange(endPosition, endPosition);
    searchInput.focus();
}

searchInput.addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(doneTyping, doneTypingInterval);
});

function doneTyping() {
    const searchValue = searchInput.value.trim();

    const query = new URLSearchParams();
    if (searchValue) query.append('search', searchValue);

    window.location.href = `${currentPath}?${query.toString()}`;
}


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
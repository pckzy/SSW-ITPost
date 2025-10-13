let typingTimer;
const doneTypingInterval = 500;

const searchInput = document.getElementById('search');
const groupSelect = document.getElementById('group-select');
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

groupSelect.addEventListener('change', () => {
  doneTyping();
});

function doneTyping() {
  const searchValue = searchInput.value.trim();
  const groupValue = groupSelect.value;

  const query = new URLSearchParams();
  if (searchValue) query.append('search', searchValue);
  if (groupValue) query.append('group', groupValue);

  window.location.href = `${currentPath}?${query.toString()}`;
}


function toggleCreateUserForm() {
  const formDiv = document.getElementById('createuser-form')
  const form = document.getElementById('createuser-forms')
  if (formDiv.classList.contains('max-h-0')) {
    formDiv.classList.remove('max-h-0')
    formDiv.classList.add('max-h-[1000px]')
    form.style.display = 'block'
    formDiv.classList.remove('hidden')
  } else {
    formDiv.classList.add('max-h-0')
    formDiv.classList.remove('max-h-[1000px]')
    formDiv.classList.add('hidden')
  }
}


document.getElementById('createuser-forms').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = this;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  fetch('/api/user/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        toggleCreateUserForm()
        const u = data.user;
        const userCount = document.getElementById('userCount');
        userCount.innerText = u.count
        const newUser = document.createElement('tr');
        newUser.className = 'hover:bg-gray-50';
        newUser.id = `user-${u.id}-table`;
        newUser.innerHTML = `
                        <td class="pl-5 px-3 py-4">
                            <a href="/profile/${u.username}/">
                                <div class="flex items-center space-x-3">
                                    <img src="/media/profile/no-profile.png" class="w-10 h-10 rounded-full border border-gray-300" alt="">
                                    <div>
                                        <div class="font-medium text-gray-900">${u.first_name} ${u.last_name}</div>
                                        <div class="text-sm text-gray-500">@${u.username}</div>
                                    </div>
                                </div>
                            </a>
                        </td>
                        <td class="px-1 py-4 text-sm text-gray-600">${u.email}</td>
                        
                        <td class="px-3 py-4 text-sm text-gray-600">-</td>
                        
                        <td class="px-1 py-4">
                            ${u.group === 'Professor' ?
                              `<span class="px-3 py-1 text-xs rounded-full bg-purple-100 text-purple-800 whitespace-nowrap">อาจารย์</span>`
                              : `<span class="px-3 py-1 text-xs rounded-full bg-red-100 text-red-800 whitespace-nowrap">ผู้ดูแล</span>`
                            }
                        </td>
                        <td class="px-3 py-4">
                            <div class="flex items-center space-x-4">
                                <a href="/profile/edit/${u.username}/" class="text-slate-600 hover:text-slate-800 font-medium">
                                    <i class="fa-regular fa-pen-to-square text-yellow-500"></i>
                                </a>
                                <button class="text-red-600 hover:text-red-800 font-medium">
                                    <i data-user-id="${u.id}" class="confirmDelete-btn fa-solid fa-trash-can"></i>
                                </button>
                            </div>
                        </td>
            `;
        const newUserDiv = document.createElement('div');
        newUserDiv.className = 'p-4 hover:bg-gray-50';
        newUserDiv.id= `user-${u.id}-div`
        newUserDiv.innerHTML = `
                            <div class="flex items-start justify-between mb-3">
                              <div class="flex-1">
                                  <a href="/profile/${u.username}/">
                                  <div class="flex items-center space-x-3">
                                      <img src="/media/profile/no-profile.png" class="w-10 h-10 rounded-full border border-gray-300" alt="">
                                      <div>
                                          <div class="font-medium text-gray-900">${u.first_name} ${u.last_name}</div>
                                          <div class="text-sm text-gray-500">@${u.username}</div>
                                      </div>
                                  </div>
                              </a>
                              </div>
                              <div class="flex flex-col items-end space-y-2">
                                  ${u.group === 'Professor' ? 
                                    `<span class="px-3 py-1 text-xs rounded-full bg-purple-100 text-purple-800">${u.group}</span>`
                                    : `<span class="px-3 py-1 text-xs rounded-full bg-red-100 text-red-800">${u.group}</span>`
                                  }
                              </div>
                          </div>
                          <div class="flex space-x-2">
                              <a href="/profile/edit/${u.username}/" class="flex-1 px-4 py-2 bg-yellow-100 text-yellow-700 text-center rounded-lg hover:bg-yellow-200 transition-all text-sm font-medium"><i class="fa-regular fa-pen-to-square text-yellow-500"></i> แก้ไข</a>
                              <button data-user-id='${u.id}' class="confirmDelete-btn flex-1 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all text-sm font-medium"><i class="fa-solid fa-trash-can"></i> ลบ</button>
                          </div>
        `
        const container = document.getElementById('userTable');
        container.prepend(newUser);

        const containerList = document.getElementById('userList');
        containerList.prepend(newUserDiv);
        
        form.reset();
        document.getElementById('error-username').textContent = ''
        document.getElementById('error-email').textContent = ''
        document.getElementById('error-password').textContent = ''
      } else {
        if (data.errors.username) {
          document.getElementById('error-username').textContent = data.errors.username;
        } else {
          document.getElementById('error-username').textContent = ''
        }
        if (data.errors.email) {
          document.getElementById('error-email').textContent = data.errors.email[0];
        } else {
          document.getElementById('error-email').textContent = ''
        }
        if (data.errors.password) {
          document.getElementById('error-password').textContent = data.errors.password[0];
        } else {
          document.getElementById('error-password').textContent = ''
        }
      }
    });
});

let userToDelete = null
let nameToDelete = null

document.addEventListener('click', function (e) {
  if (e.target.matches('.confirmDelete-btn')) {
    const deleteModal = document.getElementById('deleteUserModal');
    const putName = document.getElementById('user-delete-name');
    userToDelete = e.target.getAttribute('data-user-id')
    nameToDelete = e.target.getAttribute('data-user-name')
    console.log(userToDelete)
    deleteModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    putName.innerText = nameToDelete;
  }
});


function cancelDeleteUser() {
  userToDelete = null;
  nameToDelete = null;
  const deleteModal = document.getElementById('deleteUserModal');
  deleteModal.classList.add('hidden');
  document.body.style.overflow = 'auto';
}


function deleteUser() {
  const csrf = document.getElementById('csrfToken').value;
  fetch(`/api/user/delete/${userToDelete}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json'
      },
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      
      const userRow = document.getElementById(`user-${userToDelete}-table`);
      const userDiv = document.getElementById(`user-${userToDelete}-div`);
      const countEl = document.getElementById('userCount');
      if (!userRow | !countEl) return;

      // animation
      const rowHeight = userRow.offsetHeight;
      userRow.style.transition = 'opacity 0.5s ease, height 0.5s ease, padding 0.5s ease';
      userRow.style.height = rowHeight + 'px';
      userRow.style.opacity = '1';

      userRow.offsetHeight;

      userRow.style.opacity = '0';
      userRow.style.height = '0';
      userRow.style.paddingTop = '0';
      userRow.style.paddingBottom = '0';

      if (userDiv) {
        const divHeight = userDiv.offsetHeight;
        userDiv.style.transition = 'opacity 0.5s ease, height 0.5s ease, padding 0.5s ease';
        userDiv.style.height = divHeight + 'px';
        userDiv.style.opacity = '1';

        userDiv.offsetHeight;

        userDiv.style.opacity = '0';
        userDiv.style.height = '0';
        userDiv.style.paddingTop = '0';
        userDiv.style.paddingBottom = '0';

        userDiv.addEventListener('transitionend', () => {
          userDiv.remove();
        }, { once: true });
      }
      
      userRow.addEventListener('transitionend', () => {
          userRow.remove();
      }, { once: true });

      let count = parseInt(countEl.textContent);
      count = count - 1;
      countEl.textContent = count;
      cancelDeleteUser();
    }
  })
  .catch(err => console.error(err));
}
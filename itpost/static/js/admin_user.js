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
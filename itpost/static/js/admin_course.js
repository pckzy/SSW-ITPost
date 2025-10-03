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
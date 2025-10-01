function toggleBar() {
    const barDiv = document.getElementById('bar')
    barDiv.classList.toggle('hidden')
}

function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('hidden');
}

window.addEventListener('resize', () => {
    const dropdown = document.getElementById('userDropdown');
    if (window.innerWidth < 768) {
        dropdown.classList.add('hidden');
    }
});
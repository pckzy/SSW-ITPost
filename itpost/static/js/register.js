document.addEventListener('DOMContentLoaded', function () {
    const yearSelect = document.getElementById(yearId);
    const majorSelect = document.getElementById(majorId);
    const specializationDiv = document.getElementById('specialization-div');
    const specializationSelect = document.getElementById(specializationId);

    const itChoices = [
        { value: '', text: '-- เลือกแขนง --' },
        { value: '1', text: 'Software Engineer' },
        { value: '2', text: 'Network' },
        { value: '3', text: 'Multimedia' }
    ];

    const dataChoices = [
        { value: '', text: '-- เลือกแขนง --' },
        { value: '4', text: 'Data Analyst' },
        { value: '5', text: 'Data Engineer' }
    ];

    function toggleSpecialization() {
        const selectedYear = parseInt(yearSelect.value, 10);
        const selectedMajor = majorSelect.value;

        if (selectedYear >= 2 && selectedMajor === '1') {
            specializationDiv.style.display = 'block';
            specializationSelect.innerHTML = '';
            itChoices.forEach(choice => {
                const option = document.createElement('option');
                option.value = choice.value;
                option.textContent = choice.text;
                specializationSelect.appendChild(option);
            });
        } else if (selectedYear >= 3 && selectedMajor === '2') {
            specializationDiv.style.display = 'block';
            specializationSelect.innerHTML = '';
            dataChoices.forEach(choice => {
                const option = document.createElement('option');
                option.value = choice.value;
                option.textContent = choice.text;
                specializationSelect.appendChild(option);
            });
        } else {
            specializationDiv.style.display = 'none';
            specializationSelect.value = '';
        }
    }

    yearSelect.addEventListener('change', toggleSpecialization);
    majorSelect.addEventListener('change', toggleSpecialization);

    toggleSpecialization();
});
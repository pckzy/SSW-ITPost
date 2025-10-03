const preview = document.getElementById('preview')
image.addEventListener('change', () => {
    const [file] = image.files
    if (file) {
        preview.src = URL.createObjectURL(file)
    } else {
        preview.src = `/media/${imageSrc}`
    }
})
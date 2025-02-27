async function parseScreen(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);

    try {
        const response = await fetch('http://localhost:8000/parse', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        return data.results;
    } catch (error) {
        console.error('Error parsing screen:', error);
        throw error;
    }
}

// Example usage:
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const results = await parseScreen(file);
    console.log('Parsing results:', results);
});

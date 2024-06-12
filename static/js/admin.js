document.addEventListener('DOMContentLoaded', () => {
    fetchPhotos();
});

async function fetchPhotos() {
    try {
        const response = await fetch('http://localhost:8000/photos');
        const photos = await response.json();
        displayPhotos(photos);
    } catch (error) {
        console.error('Error fetching photos:', error);
    }
}

function displayPhotos(photos) {
    const photosContainer = document.getElementById('photos-container');
    photosContainer.innerHTML = '';
    photos.forEach(photo => {
        const photoCard = document.createElement('div');
        photoCard.className = 'photo-card';
        photoCard.innerHTML = `
            <h2>${photo.name}</h2>
            <img src="${photo.url}" alt="${photo.name}" class="photo-img" />
            <button onclick="deletePhoto(${photo.id})">Delete</button>
        `;
        photosContainer.appendChild(photoCard);
    });
}

async function deletePhoto(id) {
    try {
        await fetch(`http://localhost:8000/photos/${id}`, {
            method: 'DELETE'
        });
        fetchPhotos();
    } catch (error) {
        console.error('Error deleting photo:', error);
    }
}

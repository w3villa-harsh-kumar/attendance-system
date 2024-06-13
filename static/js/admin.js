document.addEventListener('DOMContentLoaded', () => {
    fetchPhotos();
});

async function fetchPhotos() {
    try {
        const response = await fetch('http://localhost:8000/get_faces');
        const data = await response.json();
        displayPhotos(data);
    } catch (error) {
        console.error('Error fetching photos:', error);
    }
}

function displayPhotos(data) {
    const photosContainer = document.getElementById('photos-container');
    photosContainer.innerHTML = '';

    data.forEach(user => {
        const userCard = document.createElement('div');
        userCard.className = 'user-card';
        userCard.innerHTML = `<h2>${user.username}</h2>`;
        
        user.images.forEach(image => {
            const photoCard = document.createElement('div');
            photoCard.className = 'photo-card';
            photoCard.innerHTML = `
                <img src="${image}" alt="${user.username}" class="photo-img" />
                <button onclick="deletePhoto('${user.id}', '${image}')">Delete</button>
            `;
            userCard.appendChild(photoCard);
        });

        photosContainer.appendChild(userCard);
    });
}

async function deletePhoto(userId, image) {
    try {
        await fetch(`http://localhost:8000/photos/${userId}/${image}`, {
            method: 'DELETE'
        });
        fetchPhotos();
    } catch (error) {
        console.error('Error deleting photo:', error);
    }
}

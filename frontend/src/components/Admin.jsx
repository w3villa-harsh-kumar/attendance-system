import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Admin.css';

const Admin = () => {
  const [photos, setPhotos] = useState([]);


  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_faces');
      setPhotos(response.data);
      console.log(response.data)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/photos/${id}`); 
      setPhotos(prevPhotos => prevPhotos.filter(photo => photo.id !== id));
    } catch (error) {
      console.error('Error deleting photo:', error);
    }
  };



  return (
    <div className="admin-container">
      <h1>Admin Panel</h1>
      <div className="photos-container">
        {photos.map(photo => (
          <div key={photo.id} className="photo-card">
            <h2>{photo.name}</h2>
            <img src={photo.url} alt={photo.name} className="photo-img" />
            <button onClick={() => handleDelete(photo.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Admin;

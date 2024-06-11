import React, { useState, useEffect, useRef } from 'react';
import './Capture.css';

const Capture = () => {
  const videoRef = useRef(null);
  const [name, setName] = useState('');
  const [images, setImages] = useState([]);
  const [status, setStatus] = useState('');

  useEffect(() => {
    const getVideo = async () => {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = videoStream;
        }
      } catch (err) {
        console.error("Error accessing the webcam: ", err);
        setStatus("Failed to access webcam.");
      }
    };

    getVideo();
  }, []);

  const captureImage = () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
  };

  const handleCaptureClick = () => {
    if (images.length < 4) {
      const newImage = captureImage();
      setImages([...images, newImage]);
    }
  };

  const handleReset = () => {
    setImages([]);
    setStatus('');
  };

  const handleSubmit = async () => {
    if (!name) {
      setStatus('Please enter a name.');
      return;
    }
    setStatus('Sending images...');
    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images, username: name })
      });
      const data = await response.json();
      setStatus(`Images sent! Response: ${data.message}`);
      setImages([]);
    } catch (error) {
      setStatus(`Error sending images: ${error.message}`);
      console.error('Error sending images:', error);
    }
  };

  return (
    <div className="capture-container">
      <header className="capture-header">
        <h1>Face Registration System</h1>
        <video ref={videoRef} autoPlay playsInline className="video" />
        <div>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Enter your name"
          />
          <button onClick={handleCaptureClick} disabled={images.length >= 4}>
            Capture Face
          </button>
          <div className="images-container">
            {images.map((src, index) => (
              <img key={index} src={src} alt={`Face ${index + 1}`} className="captured-image" />
            ))}
          </div>
        </div>
        {images.length === 4 && (
          <>
            <button className="confirm-button" onClick={handleSubmit}>
              Confirm and Send
            </button>
            <button className="reset-button" onClick={handleReset}>
              Recapture Images
            </button>
          </>
        )}
        <p>{status}</p>
      </header>
    </div>
  );
}

export default Capture;
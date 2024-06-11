import React, { useState, useEffect } from 'react';
import './Recognizer.css';

const Recognizer = () => {
  const [faces, setFaces] = useState([]);
  const [imgSrc, setImgSrc] = useState('');

  useEffect(() => {
    const ws = new WebSocket('');

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'face_recognition') {
        setFaces(prevFaces => [...prevFaces, {
          id: faces.length + 1,
          face_id: message.face_id,
          timestamp: new Date(message.timestamp * 1000).toLocaleString()
        }]);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleError = () => {
    setImgSrc('https://cdn.osxdaily.com/wp-content/uploads/2013/12/there-is-no-connected-camera-mac.jpg');
  };

  return (
    <div className="recognizer-container">
      <h1>Face Recognition</h1>
      <img 
        src={imgSrc} 
        alt="Live Feed" 
        onError={handleError} 
        width="720" 
        height="480" 
      />
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Face ID</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {faces.map(face => (
              <tr key={face.id}>
                <td>{face.id}</td>
                <td>{face.face_id}</td>
                <td>{face.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Recognizer;

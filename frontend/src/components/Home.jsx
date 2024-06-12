import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
    const navigate = useNavigate();

    const handleButtonClick1 = () => {
        navigate('/capture');
        window.location.reload();

    };

    const handleButtonClick2 = () => {
        navigate('/admin');
        window.location.reload();
    
    };

    const handleButtonClick3 = () => {
        navigate('/recognizer');
        window.location.reload();
    
    };

    return (
        <div className="home-container">
            <button className="capture-button" onClick={handleButtonClick1}>
                Capture Your Face
            </button>
            <button className="Admin-button" onClick={handleButtonClick2}>
                Admin
            </button>
            <button className="Recognizer-button" onClick={handleButtonClick3}>
                Recognizer
            </button>
        </div>
    );
};


export default Home;

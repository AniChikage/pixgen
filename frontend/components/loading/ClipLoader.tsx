import React from 'react';
import RingLoader from "react-spinners/RingLoader";
import './ClipLoader.css'; 


const ClipLoaderComponent = () => {
  return (
    <div className="app-container">
        <div className="loader-container">
          <RingLoader color="#36D7B7" loading={true} size={150} />
        </div>
    </div>
  );
};

export default ClipLoaderComponent;
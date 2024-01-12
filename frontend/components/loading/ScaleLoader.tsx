import React from 'react';
import ScaleLoader from "react-spinners/ScaleLoader";
import './ClipLoader.css'; 


const ScaleLoaderComponent = () => {
  return (
    <div className="app-container">
        <div className="loader-container">
          <ScaleLoader color="#36D7B7" loading={true} />
        </div>
    </div>
  );
};

export default ScaleLoaderComponent;
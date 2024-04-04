import React from 'react';
import './ResponseComponent.css'; // Import CSS for styling

interface ResponseComponentProps {
    responseText: string;
  }

const ResponseComponent: React.FC<ResponseComponentProps> = ({ responseText }) => {
  return (
    <div className="responseContainer">
      <p dangerouslySetInnerHTML={{ __html: responseText }}></p>
    </div>
  );
};

export default ResponseComponent;

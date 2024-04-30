// App.tsx (or App.js if you're not using TypeScript)
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import PDFUploadPage from './Components/PDFUpload';
import Chat from './Components/Chat';
import DataUpload from './Components/DataUpload';

const App: React.FC = () => {
  return (
    <Router>
      <div>
        <nav>
          {/* Navigation links */}
          <Link to="/">Chat</Link> | <Link to="/upload-pdf">Upload PDF</Link> | <Link to="/data-upload">Data Upload</Link>
        </nav>
        {/* The `Routes` component replaces `Switch` and is responsible for selecting the first route that matches the location. */}
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/upload-pdf" element={<PDFUploadPage />} />
          <Route path="/data-upload" element={<DataUpload />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;

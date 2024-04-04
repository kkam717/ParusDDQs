// PDFUploadPage.js
import React, { useState } from 'react';

const PDFUpload = () => {
    const [file, setFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files ? event.target.files[0] : null;
        setFile(selectedFile);
    };

    const handleUpload = async () => {
        if (!file) {
            alert('Please select a PDF file first.');
            return;
        }

        setIsLoading(true); // Start loading

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('http://localhost:8000/api/upload-pdf/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle automatic download of the PDF
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', 'ddq_responses.pdf'); // Set the file name for the download
            document.body.appendChild(link);
            link.click();

            if (link.parentNode) {
                link.parentNode.removeChild(link);
            }

        } catch (error) {
            console.error('Upload failed:', error);
        } finally {
            setIsLoading(false); // Stop loading regardless of the outcome
        }
    };


    return (
        <div>
            {isLoading && <p>Loading...</p>}
            {<div>
                <h1>Upload a PDF</h1>
                <input type="file" accept="application/pdf" onChange={handleFileChange} />
                <button onClick={handleUpload}>Upload</button>
            </div>}
        </div>
    );

};

export default PDFUpload;

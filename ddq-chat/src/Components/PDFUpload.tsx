import React, { useState } from 'react';

const PDFUpload = () => {
    const [file, setFile] = useState<File | null>(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [downloadLink, setDownloadLink] = useState('');

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFile(event.target.files ? event.target.files[0] : null);
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        if (!file) {
            setUploadStatus('Please select a PDF file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/upload-pdf/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Error uploading PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            setDownloadLink(url);
            setUploadStatus('PDF processed successfully.');
        } catch (error) {
            setUploadStatus('Error processing PDF. Please try again.');
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h2>Upload PDF of Questions</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                />
                <button type="submit">Upload PDF</button>
            </form>
            {uploadStatus && <p>{uploadStatus}</p>}
            {downloadLink && (
                <a href={downloadLink} download="answered_ddq_responses.pdf">
                    Download Answered PDF
                </a>
            )}
        </div>
    );
};

export default PDFUpload;

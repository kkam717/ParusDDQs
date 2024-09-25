import React, { useState } from 'react';

const DataUpload = () => {
    const [files, setFiles] = useState<FileList | null>(null);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFiles(event.target.files);
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        if (!files || files.length === 0) {
            setUploadStatus('Please select at least one file to upload.');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch('http://localhost:8000/upload/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Error uploading files');
            }

            setUploadStatus('Files uploaded and processed successfully.');
        } catch (error) {
            setUploadStatus('Error uploading files. Please try again.');
            console.error('Error:', error);
        }
    };

    // Reset the backend data and clear the frontend file input
    const handleReset = async () => {
        try {
            const response = await fetch('http://localhost:8000/reset/', {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Error resetting data');
            }

            setUploadStatus('Training data has been reset successfully.');
            setFiles(null); // Clear the frontend file input

        } catch (error) {
            setUploadStatus('Error resetting data. Please try again.');
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h2>Upload Training Data (PDF/Excel)</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    accept=".pdf,.xlsx,.xls"
                    multiple
                    onChange={handleFileUpload}
                />
                <button type="submit">Upload Files</button>
            </form>
            <button onClick={handleReset}>Reset Data</button>
            {uploadStatus && <p>{uploadStatus}</p>}
        </div>
    );
};

export default DataUpload;

import React, { useState, ChangeEvent } from 'react';

const DataUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);

    const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setFile(event.target.files[0]);
        }
    };

    const onFileUpload = async () => {
        if (!file) {
            alert('Please select a file first!');
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                alert('File successfully uploaded');
            } else {
                alert('Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Upload failed with error');
        }
    };

    return (
        <div>
            <h2>Upload Training Data</h2>
            <input type="file" onChange={onFileChange} accept=".pdf, .xlsx, .xls" />
            <button onClick={onFileUpload}>Upload!</button>
        </div>
    );
};

export default DataUpload;

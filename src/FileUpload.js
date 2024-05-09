import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';
import './App.css'
import axios from 'axios'; 

function FileUpload() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const onDrop = useCallback(acceptedFiles => {
    setSelectedFiles(currentFiles => [...currentFiles, ...acceptedFiles]);
  }, []);

  const removeFile = fileName => {
    setSelectedFiles(currentFiles => currentFiles.filter(file => file.name !== fileName));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: '.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'
  });

  const handleMerge = () => {
    if (selectedFiles.length !== 2) {
      alert("Please upload exactly two files representing regular and high frequency sensor data.");
      return;
    }

    setIsLoading(true); // Start loading

    const formData = new FormData();
    for (let file of selectedFiles) {
      formData.append('files', file);
    }

    axios.post('http://localhost:5000/merge', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob'
    })
    .then((response) => {
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', 'sensor_merged.csv'); // any other extension
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch((error) => {
      if (error.response && error.response.status === 500) {
        alert("Error merging. Please make sure you're uploading sensor files.");
      } else {
        console.error('There was an error!', error);
      }
    })
    .finally(() => {
      setIsLoading(false); // Stop loading irrespective of success or failure
    });
  };

  return (
    <div className="file-upload-container">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {
          isDragActive ?
            <p>Drop the files here ...</p> :
            <p>Drag+drop sensor files here, or click to select files</p>
        }
      </div>
      <ul className="file-list">
        {selectedFiles.map(file => (
            <li key={file.path}>
              {file.path}
              <button onClick={() => removeFile(file.name)} className="remove-button">Remove</button>
            </li>
        ))}
      </ul>
      {isLoading && <div className="loader"></div>} {/* Loading icon */}
      <button onClick={handleMerge}>Merge</button>
    </div>
  );
}

export default FileUpload;


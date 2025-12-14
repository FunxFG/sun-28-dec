import React, { useState, useEffect } from 'react';
import { Download, FileText, Image, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function FileDownloadManager() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/files/list`);
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const getFileIcon = (filename) => {
    if (filename.endsWith('.pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    if (filename.endsWith('.png') || filename.endsWith('.jpg')) return <Image className="w-5 h-5 text-blue-500" />;
    return <FileText className="w-5 h-5" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Generated Files</h2>
        <Button onClick={fetchFiles} disabled={loading} size="sm">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {files.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No files found. Generate a TGS or TMP to see files here.
        </div>
      ) : (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
              <div className="flex items-center gap-3 flex-1">
                {getFileIcon(file.name)}
                <div className="flex-1">
                  <div className="font-medium">{file.name}</div>
                  <div className="text-sm text-gray-500">
                    {formatFileSize(file.size)} • {formatDate(file.modified)}
                  </div>
                </div>
              </div>
              <a
                href={`${API}/api/files/download/${encodeURIComponent(file.name)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-4"
              >
                <Button size="sm" variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </a>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
        <p className="text-sm text-blue-800">
          <strong>Tip:</strong> Click "Download" to open the file in a new tab. Your browser will download it automatically or you can right-click → "Save as..."
        </p>
      </div>
    </div>
  );
}

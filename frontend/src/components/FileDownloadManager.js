import React, { useState, useEffect, useCallback } from 'react';
import { Download, FileText, Image, RefreshCw, ExternalLink, FolderOpen, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function FileDownloadManager({ autoRefresh = false }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'pdf', 'png', 'recent'
  const [downloadStatus, setDownloadStatus] = useState({});

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/files/list`);
      if (!response.ok) throw new Error('Failed to fetch files');
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
    // Auto-refresh every 10 seconds if enabled
    if (autoRefresh) {
      const interval = setInterval(fetchFiles, 10000);
      return () => clearInterval(interval);
    }
  }, [fetchFiles, autoRefresh]);

  const getFileIcon = (filename) => {
    if (filename.endsWith('.pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    if (filename.endsWith('.png') || filename.endsWith('.jpg')) return <Image className="w-5 h-5 text-blue-500" />;
    if (filename.endsWith('.txt')) return <FileText className="w-5 h-5 text-gray-500" />;
    return <FileText className="w-5 h-5" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleDownload = (filename) => {
    const url = `${API}/api/files/download/${encodeURIComponent(filename)}`;
    console.log('📥 Opening download URL:', url);
    
    setDownloadStatus(prev => ({ ...prev, [filename]: 'downloading' }));
    
    // Use window.open to bypass iframe sandbox restrictions
    const newWindow = window.open(url, '_blank');
    
    if (newWindow) {
      setDownloadStatus(prev => ({ ...prev, [filename]: 'success' }));
      setTimeout(() => {
        setDownloadStatus(prev => ({ ...prev, [filename]: null }));
      }, 3000);
    } else {
      // Fallback: try with hidden anchor
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setDownloadStatus(prev => ({ ...prev, [filename]: 'success' }));
      setTimeout(() => {
        setDownloadStatus(prev => ({ ...prev, [filename]: null }));
      }, 3000);
    }
  };

  const copyDownloadUrl = (filename) => {
    const url = `${API}/api/files/download/${encodeURIComponent(filename)}`;
    navigator.clipboard.writeText(url).then(() => {
      setDownloadStatus(prev => ({ ...prev, [filename]: 'copied' }));
      setTimeout(() => {
        setDownloadStatus(prev => ({ ...prev, [filename]: null }));
      }, 2000);
    });
  };

  // Filter files
  const filteredFiles = files.filter(file => {
    if (filter === 'pdf') return file.name.endsWith('.pdf');
    if (filter === 'png') return file.name.endsWith('.png') || file.name.endsWith('.jpg');
    if (filter === 'recent') {
      const fileDate = new Date(file.modified);
      const now = new Date();
      return (now - fileDate) < 86400000; // Last 24 hours
    }
    return true;
  });

  const getFileTypeLabel = (filename) => {
    if (filename.includes('TMP') && filename.endsWith('.pdf')) return 'Traffic Management Plan';
    if (filename.includes('TGS') && filename.endsWith('.pdf')) return 'TGS Drawing (PDF)';
    if (filename.includes('TGS') && filename.endsWith('.png')) return 'TGS Drawing (Image)';
    if (filename.includes('StreetView')) return 'Street View Image';
    if (filename.includes('Signage')) return 'Signage Schedule';
    if (filename.includes('Specifications')) return 'TGS Specifications';
    if (filename.endsWith('.pdf')) return 'PDF Document';
    if (filename.endsWith('.png')) return 'PNG Image';
    return 'Document';
  };

  return (
    <Card className="border-2 border-green-500 shadow-lg">
      <CardHeader className="bg-green-50">
        <CardTitle className="text-green-800 flex items-center gap-2">
          <FolderOpen className="w-6 h-6" />
          📥 Download Generated Files
        </CardTitle>
        <CardDescription className="text-green-700 font-medium">
          All your generated TMP and TGS files are available here for download
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        {/* Success Banner */}
        <div className="p-3 bg-green-100 rounded-lg border-2 border-green-400">
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-green-800 font-semibold">✅ Downloads Work Here!</p>
              <p className="text-green-700 text-sm">
                Click any &quot;Download&quot; button → File opens in new tab → Downloads automatically to your device
              </p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-2 justify-between items-center">
          <div className="flex gap-1">
            {['all', 'pdf', 'png', 'recent'].map(f => (
              <Button
                key={f}
                size="sm"
                variant={filter === f ? 'default' : 'outline'}
                onClick={() => setFilter(f)}
                className={filter === f ? 'bg-green-600' : ''}
              >
                {f === 'all' ? 'All' : f === 'recent' ? 'Last 24h' : f.toUpperCase()}
              </Button>
            ))}
          </div>
          <Button onClick={fetchFiles} disabled={loading} size="sm" variant="outline">
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* File Count */}
        <div className="text-sm text-gray-600">
          Showing {filteredFiles.length} of {files.length} files
        </div>

        {/* File List */}
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
            <FolderOpen className="w-16 h-16 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 text-lg mb-2">📁 No files found</p>
            <p className="text-sm text-gray-400">Generate a TGS or TMP to see downloadable files here</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredFiles.map((file, index) => (
              <div 
                key={index} 
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 hover:border-green-300 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {getFileIcon(file.name)}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate text-sm" title={file.name}>
                      {file.name}
                    </div>
                    <div className="text-xs text-gray-500 flex gap-2">
                      <span className="bg-gray-100 px-1.5 py-0.5 rounded">{getFileTypeLabel(file.name)}</span>
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>{formatDate(file.modified)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 ml-2 flex-shrink-0">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => copyDownloadUrl(file.name)}
                    title="Copy download URL"
                  >
                    {downloadStatus[file.name] === 'copied' ? '✓' : <ExternalLink className="w-4 h-4" />}
                  </Button>
                  <Button 
                    size="sm" 
                    className={`${downloadStatus[file.name] === 'success' ? 'bg-green-600' : 'bg-blue-600'} hover:bg-blue-700 text-white`}
                    onClick={() => handleDownload(file.name)}
                  >
                    {downloadStatus[file.name] === 'success' ? (
                      <>
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Done
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Section */}
        <div className="p-3 bg-blue-50 rounded border border-blue-200">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-semibold">💡 If download doesn&apos;t start:</p>
              <ul className="list-disc ml-4 mt-1 space-y-0.5">
                <li>Allow popups for this site in your browser</li>
                <li>Click the link icon to copy URL, then paste in new tab</li>
                <li>Right-click &quot;Download&quot; and select &quot;Open in new tab&quot;</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Download, Map, Eye, Camera } from 'lucide-react';

const VisualTGSViewer = ({ planData, placedDevices, planId }) => {
  const [visualTGS, setVisualTGS] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('satellite'); // 'satellite' or 'streetview'
  const [selectedStreetView, setSelectedStreetView] = useState(0);
  const [downloadingCombined, setDownloadingCombined] = useState(false);

  const API = process.env.REACT_APP_BACKEND_URL || '';

  const generateVisualTGS = async () => {
    console.log('🎬 generateVisualTGS called');
    console.log('  planData:', planData);
    console.log('  placedDevices count:', placedDevices?.length);
    
    if (!planData || !placedDevices || placedDevices.length === 0) {
      console.error('❌ Missing required data');
      alert('Please place some devices first to generate visual TGS');
      return;
    }

    setLoading(true);
    try {
      const center_lat = planData.start_lat || planData.map_center_lat || -34.9285;
      const center_lng = planData.start_lng || planData.map_center_lng || 138.6007;
      
      console.log('📍 Center coordinates:', center_lat, center_lng);
      console.log('📦 Request payload:', {
        center_lat,
        center_lng,
        placed_devices: placedDevices,
        include_streetview: true
      });

      const url = `${API}/api/tgs/generate-visual`;
      console.log('🌐 Calling:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat,
          center_lng,
          placed_devices: placedDevices,
          include_streetview: true
        })
      });

      console.log('📨 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('✅ Visual TGS generated successfully:', data);
      setVisualTGS(data);
      alert('✅ Visual TGS generated! You can now download it.');
    } catch (error) {
      console.error('❌ Error generating visual TGS:', error);
      alert(`Failed to generate visual TGS: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };


  const downloadCombinedTmpWithTgs = async () => {
    if (!visualTGS?.satellite_tgs?.image_base64 || !planId) {
      alert('Save the plan and generate Visual TGS before downloading combined TMP + TGS PDF.');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please log in to download the combined TMP + TGS PDF.');
      return;
    }

    setDownloadingCombined(true);
    try {
      const response = await fetch(`${API}/api/plans/${planId}/pdf-with-tgs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tgs_image_base64: visualTGS.satellite_tgs.image_base64,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      const safeName = (planData?.plan_name || 'plan').replace(/\s+/g, '_');
      link.href = url;
      link.download = `${safeName}_TMP_TGS.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading combined TMP + TGS PDF:', error);
      alert(`Failed to download combined TMP + TGS PDF: ${error.message}`);
    } finally {
      setDownloadingCombined(false);
    }
  };

  const downloadTGSImage = () => {
    console.log('🔽 downloadTGSImage called');
    if (!visualTGS?.satellite_tgs?.image_base64) {
      console.error('❌ No image data available');
      alert('No TGS image available to download');
      return;
    }

    try {
      console.log('📥 Creating download link...');
      const link = document.createElement('a');
      link.href = `data:image/png;base64,${visualTGS.satellite_tgs.image_base64}`;
      link.download = `tgs_${planData?.plan_name || 'plan'}_${new Date().toISOString().split('T')[0]}.png`;
      
      // Add to document, click, and remove (required for some browsers)
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('✅ Download initiated');
      alert('✅ TGS image downloaded! Check your Downloads folder.');
    } catch (error) {
      console.error('❌ Download failed:', error);
      alert(`Download failed: ${error.message}`);
    }
  };

  const downloadStreetView = (index) => {
    console.log('🔽 downloadStreetView called for index:', index);
    const streetview = visualTGS?.streetview_images?.[index];
    if (!streetview?.image_base64) {
      console.error('❌ No streetview data available');
      return;
    }

    try {
      const link = document.createElement('a');
      link.href = `data:image/jpeg;base64,${streetview.image_base64}`;
      link.download = `streetview_${streetview.sign_code}_${new Date().toISOString().split('T')[0]}.jpg`;
      
      // Add to document, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('✅ Street view download initiated');
    } catch (error) {
      console.error('❌ Street view download failed:', error);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="border-l-4 border-l-blue-600">
        <CardHeader>
          <CardTitle className="text-blue-700 flex items-center gap-2">
            <Map className="w-5 h-5" />
            Visual Traffic Guidance Scheme (TGS)
          </CardTitle>
          <CardDescription>
            Generate professional TGS with sign overlays on satellite imagery and Street View perspectives
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!visualTGS ? (
            <div className="text-center py-8">
              <div className="mb-4">
                <Map className="w-16 h-16 mx-auto text-gray-400" />
              </div>
              <p className="text-gray-600 mb-4">
                Generate visual TGS to see your traffic signs overlaid on satellite imagery
              </p>
              <Button
                onClick={generateVisualTGS}
                disabled={loading || !placedDevices || placedDevices.length === 0}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>⏳ Generating...</>
                ) : (
                  <>
                    <Eye className="w-4 h-4 mr-2" />
                    Generate Visual TGS
                  </>
                )}
              </Button>
              {(!placedDevices || placedDevices.length === 0) && (
                <p className="text-sm text-orange-600 mt-2">
                  ⚠️ Place devices on the map first using &quot;Auto-Place Devices&quot; button
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {/* View Selector */}
              <div className="flex gap-2 border-b pb-2">
                <Button
                  variant={activeView === 'satellite' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveView('satellite')}
                  className="flex items-center gap-2"
                >
                  <Map className="w-4 h-4" />
                  Satellite View
                </Button>
                <Button
                  variant={activeView === 'streetview' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveView('streetview')}
                  className="flex items-center gap-2"
                  disabled={!visualTGS.streetview_images || visualTGS.streetview_images.length === 0}
                >
                  <Camera className="w-4 h-4" />
                  Street View ({visualTGS.streetview_images?.length || 0})
                </Button>
              </div>

              {/* Satellite View */}
              {activeView === 'satellite' && visualTGS.satellite_tgs?.success && (
                <div className="space-y-3">
                  <div className="bg-gray-100 rounded-lg p-2">
                    <img
                      src={`data:image/png;base64,${visualTGS.satellite_tgs.image_base64}`}
                      alt="Traffic Guidance Scheme with Sign Overlays"
                      className="w-full rounded shadow-lg"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="font-semibold text-blue-900">Total Signs</div>
                      <div className="text-2xl font-bold text-blue-700">
                        {visualTGS.satellite_tgs.total_signs}
                      </div>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <div className="font-semibold text-green-900">Zoom Level</div>
                      <div className="text-2xl font-bold text-green-700">
                        {visualTGS.satellite_tgs.zoom}
                      </div>
                    </div>
                  </div>

                  {visualTGS.satellite_tgs.sign_positions && (
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-semibold mb-2">Sign Positions:</div>
                      <div className="space-y-1 max-h-40 overflow-y-auto">
                        {visualTGS.satellite_tgs.sign_positions.map((sign, idx) => (
                          <div key={idx} className="text-xs flex justify-between bg-white p-2 rounded">
                            <span className="font-medium">{sign.device_code}</span>
                            <span className="text-gray-600">
                              {sign.distance_from_start}m | {sign.side}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Button
                      onClick={downloadTGSImage}
                      variant="outline"
                      className="w-full"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download TGS Image (PNG)
                    </Button>

                    <Button
                      onClick={downloadCombinedTmpWithTgs}
                      variant="default"
                      disabled={!planId || downloadingCombined}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      {downloadingCombined ? (
                        <>Preparing TMP + TGS PDF...</>
                      ) : (
                        <>
                          <Download className="w-4 h-4 mr-2" />
                          Download TMP + TGS (PDF)
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}

              {/* Street View */}
              {activeView === 'streetview' && visualTGS.streetview_images && visualTGS.streetview_images.length > 0 && (
                <div className="space-y-3">
                  <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                    <div className="flex items-center gap-2">
                      <Camera className="w-5 h-5 text-yellow-600" />
                      <div>
                        <div className="font-semibold text-yellow-900">
                          Driver&apos;s Perspective - Sign Position {selectedStreetView + 1}
                        </div>
                        <div className="text-sm text-yellow-700">
                          {visualTGS.streetview_images[selectedStreetView].sign_name}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-100 rounded-lg p-2">
                    <img
                      src={`data:image/jpeg;base64,${visualTGS.streetview_images[selectedStreetView].image_base64}`}
                      alt={`Street View - ${visualTGS.streetview_images[selectedStreetView].sign_code}`}
                      className="w-full rounded shadow-lg"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="bg-gray-50 p-2 rounded text-center">
                      <div className="text-xs text-gray-600">Sign Code</div>
                      <div className="font-bold">
                        {visualTGS.streetview_images[selectedStreetView].sign_code}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded text-center">
                      <div className="text-xs text-gray-600">Distance</div>
                      <div className="font-bold">
                        {visualTGS.streetview_images[selectedStreetView].distance}m
                      </div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded text-center">
                      <div className="text-xs text-gray-600">Heading</div>
                      <div className="font-bold">
                        {visualTGS.streetview_images[selectedStreetView].heading}°
                      </div>
                    </div>
                  </div>

                  {/* Street View Navigation */}
                  <div className="flex gap-2">
                    {visualTGS.streetview_images.map((_, idx) => (
                      <Button
                        key={idx}
                        variant={selectedStreetView === idx ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedStreetView(idx)}
                        className="flex-1"
                      >
                        View {idx + 1}
                      </Button>
                    ))}
                  </div>

                  <Button
                    onClick={() => downloadStreetView(selectedStreetView)}
                    variant="outline"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Street View (JPEG)
                  </Button>
                </div>
              )}

              {/* Regenerate Button */}
              <div className="pt-4 border-t">
                <Button
                  onClick={generateVisualTGS}
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                >
                  {loading ? '⏳ Regenerating...' : '🔄 Regenerate Visual TGS'}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VisualTGSViewer;

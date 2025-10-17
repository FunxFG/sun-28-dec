import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Save, 
  Download, 
  MapPin, 
  Plus,
  Trash2,
  Shield,
  Zap,
  RefreshCw,
  FileImage,
  Map,
  Ruler
} from 'lucide-react';
import austroadsRules from '../utils/austroadsRules';
import tgsDrawingGenerator from '../utils/tgsDrawingGenerator';
import RiskMatrixInteractive from './RiskMatrixInteractive';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://austromap.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

// Traffic device library based on Austroads standards
const TRAFFIC_DEVICES = {
  'Signs': [
    { type: 'warning', name: 'Road Work Ahead', icon: '🚧' },
    { type: 'warning', name: 'Detour', icon: '↪️' },
    { type: 'warning', name: 'Speed Reduction', icon: '🔢' },
    { type: 'regulatory', name: 'Stop', icon: '🛑' },
    { type: 'regulatory', name: 'Give Way', icon: '⚠️' },
    { type: 'regulatory', name: 'No Entry', icon: '🚫' },
    { type: 'regulatory', name: 'Speed Limit 40', icon: '4️⃣0️⃣' },
    { type: 'guide', name: 'Lane Closure', icon: '🚫' },
  ],
  'Cones': [
    { type: 'cone', name: 'Traffic Cone 700mm', icon: '🔶' },
    { type: 'cone', name: 'Traffic Cone 900mm', icon: '🔶' },
    { type: 'cone', name: 'Witches Hat', icon: '🔸' },
  ],
  'Barriers': [
    { type: 'barrier', name: 'Concrete Barrier', icon: '🛡️' },
    { type: 'barrier', name: 'Water Filled Barrier', icon: '💧' },
    { type: 'barrier', name: 'Plastic Barrier', icon: '🚧' },
  ],
  'Signals': [
    { type: 'signal', name: 'Portable Traffic Light', icon: '🚥' },
    { type: 'signal', name: 'Stop/Go Board', icon: '🔴' },
    { type: 'signal', name: 'Variable Message Sign', icon: '📟' },
  ]
};

export default function PlanEditor({ user, onLogout }) {
  const { planId } = useParams();
  const navigate = useNavigate();
  const mapRef = useRef(null);
  const googleMapRef = useRef(null);
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    plan_name: '',
    company_details: {
      name: '',
      address: '',
      abn: '',
      phone: '',
      liaison_name: '',
      liaison_phone: '',
      liaison_email: ''
    },
    traffic_company: {
      name: '',
      address: '',
      phone: '',
      liaison_name: '',
      liaison_phone: '',
      liaison_email: ''
    },
    work_details: {
      work_type: '',
      work_style: '',
      description: '',
      start_date: '',
      end_date: '',
      start_address: '',
      end_address: ''
    },
    road_occupancy: {
      footpath: false,
      left_shoulder: false,
      left_lane: false,
      center_lane: false,
      right_lane: false,
      right_shoulder: false,
      median_strip: false,
      complete_road_closure: false
    },
    control_measures: {
      twenty_min_rule: false,
      signage: false,
      speed_reduction: false,
      detour: false
    },
    road_data: {
      traffic_volume: null,
      road_classification: '',
      road_type: '',
      governing_body: '',
      workzone_size: null
    },
    devices: [],
    risk_assessment: {},
    map_center_lat: -27.4698,
    map_center_lng: 153.0251,
    map_zoom: 15
  });

  useEffect(() => {
    if (planId) {
      fetchPlan();
    }
    
    // Load Google Maps script
    const loadGoogleMaps = () => {
      if (window.google) {
        initializeMap();
        return;
      }

      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = () => {
        setTimeout(initializeMap, 100);
      };
      document.head.appendChild(script);
    };

    loadGoogleMaps();
  }, [planId]);

  const fetchPlan = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/plans/${planId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFormData(response.data);
    } catch (error) {
      toast.error('Failed to load plan');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const initializeMap = () => {
    if (!mapRef.current || !window.google?.maps) {
      setTimeout(initializeMap, 100);
      return;
    }

    const map = new window.google.maps.Map(mapRef.current, {
      center: { lat: formData.map_center_lat, lng: formData.map_center_lng },
      zoom: formData.map_zoom,
      mapTypeId: 'roadmap'
    });

    googleMapRef.current = map;

    // Add click listener for placing devices
    map.addListener('click', (event) => {
      const lat = event.latLng.lat();
      const lng = event.latLng.lng();
      
      // For now, just add a default traffic cone
      const newDevice = {
        id: Date.now().toString(),
        device_type: 'cone',
        device_name: 'Traffic Cone 700mm',
        position_lat: lat,
        position_lng: lng,
        properties: {}
      };
      
      setFormData(prev => ({
        ...prev,
        devices: [...prev.devices, newDevice]
      }));
      
      addDeviceMarker(map, newDevice);
    });

    // Add existing device markers
    formData.devices.forEach(device => {
      addDeviceMarker(map, device);
    });
  };

  const addDeviceMarker = (map, device) => {
    const isAutoPlaced = device.properties?.auto_placed;
    const deviceTypeIcon = getDeviceIcon(device.device_type);
    const markerColor = isAutoPlaced ? '#3B82F6' : '#F97316'; // Blue for auto, orange for manual
    
    const marker = new window.google.maps.Marker({
      position: { lat: device.position_lat, lng: device.position_lng },
      map: map,
      title: `${device.device_name}${isAutoPlaced ? ' (Auto-placed)' : ' (Manual)'}`,
      icon: {
        url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
          <svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="14" fill="${markerColor}" stroke="white" stroke-width="2"/>
            <text x="16" y="22" text-anchor="middle" fill="white" font-size="16">${deviceTypeIcon}</text>
            ${isAutoPlaced ? '<circle cx="24" cy="8" r="4" fill="#10B981"/>' : ''}
          </svg>
        `),
        scaledSize: new window.google.maps.Size(32, 32)
      }
    });

    // Add info window with device details
    const infoWindow = new window.google.maps.InfoWindow({
      content: `
        <div class="p-2">
          <h3 class="font-semibold text-sm">${device.device_name}</h3>
          <p class="text-xs text-gray-600">${device.device_type}</p>
          ${isAutoPlaced ? `
            <p class="text-xs text-blue-600 mt-1">Auto-placed</p>
            <p class="text-xs text-gray-500">${device.properties.austroads_rule || ''}</p>
          ` : '<p class="text-xs text-orange-600 mt-1">Manually placed</p>'}
          ${device.properties?.distance ? `<p class="text-xs">Distance: ${device.properties.distance}</p>` : ''}
        </div>
      `
    });

    marker.addListener('click', () => {
      infoWindow.open(map, marker);
    });

    marker.addListener('rightclick', () => {
      if (window.confirm(`Remove ${device.device_name}?`)) {
        removeDevice(device.id);
        marker.setMap(null);
      }
    });

    // Store marker reference for cleanup
    if (!window.deviceMarkers) window.deviceMarkers = [];
    window.deviceMarkers.push(marker);
  };

  const getDeviceIcon = (deviceType) => {
    const icons = {
      'warning': '⚠️',
      'regulatory': '🛑',
      'guide': '➡️',
      'cone': '🔶',
      'barrier': '🛡️',
      'signal': '🚥',
      'guidance': '📟'
    };
    return icons[deviceType] || '🚧';
  };

  const removeDevice = (deviceId) => {
    setFormData(prev => ({
      ...prev,
      devices: prev.devices.filter(d => d.id !== deviceId)
    }));
  };

  const handleInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleAddressGeocode = async (address, isStart = true) => {
    try {
      const response = await fetch(`${API}/geocode?address=${encodeURIComponent(address)}`);
      if (!response.ok) throw new Error('Geocoding failed');
      const data = await response.json();
      const { lat, lng } = data;
      
      if (isStart) {
        setFormData(prev => ({
          ...prev,
          map_center_lat: lat,
          map_center_lng: lng
        }));
        
        if (googleMapRef.current) {
          googleMapRef.current.setCenter({ lat, lng });
        }
      }
      
      // Update road data
      if (formData.work_details.start_address && formData.work_details.end_address) {
        fetchRoadData();
      }
      
      toast.success('Address geocoded successfully');
    } catch (error) {
      toast.error('Failed to geocode address');
    }
  };

  const handleAutoPlaceDevices = async () => {
    if (!formData.work_details.start_address || !formData.work_details.end_address) {
      toast.error('Please enter start and end addresses first');
      return;
    }

    try {
      toast.info('Calculating device placement...');
      
      // Get coordinates for start and end addresses
      const startCoords = await geocodeAddress(formData.work_details.start_address);
      const endCoords = await geocodeAddress(formData.work_details.end_address);
      
      // Get road data
      const roadDataResponse = await fetch(`${API}/road-data?start_address=${encodeURIComponent(formData.work_details.start_address)}&end_address=${encodeURIComponent(formData.work_details.end_address)}`);
      const roadData = await roadDataResponse.json();

      // Google Maps API key for road snapping
      const GOOGLE_MAPS_API_KEY = 'AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs';

      // Calculate automatic device placement using AGTTM-compliant rules
      // NOW with road snapping to place devices on road/curb, NOT on property
      const workZoneData = {
        start_lat: startCoords.lat,
        start_lng: startCoords.lng,
        end_lat: endCoords.lat,
        end_lng: endCoords.lng,
        work_details: formData.work_details,
        road_occupancy: formData.road_occupancy,
        control_measures: formData.control_measures
      };

      const roadGeometry = {
        ...roadData,
        speed_limit: roadData.speed_limit || 60 // Use actual or default
      };

      // Import and use AGTTM placement with road snapping
      console.log('Starting auto-placement with road snapping...');
      const agttmRules = await import('../utils/agttmCompliantRules.js');
      
      console.log('Work zone data:', workZoneData);
      console.log('Road geometry:', roadGeometry);
      
      const autoDevices = await agttmRules.default.calculateAGTTMCompliantPlacement(
        workZoneData,
        roadGeometry,
        GOOGLE_MAPS_API_KEY
      );

      console.log('Auto-placement complete. Devices returned:', autoDevices);
      console.log('Device count:', autoDevices?.length || 0);

      // Update form data with automatically placed devices
      setFormData(prev => ({
        ...prev,
        devices: autoDevices || [],
        map_center_lat: startCoords.lat,
        map_center_lng: startCoords.lng,
        road_data: roadData
      }));

      // Re-initialize map with new devices
      if (googleMapRef.current) {
        // Clear existing markers
        if (window.deviceMarkers) {
          window.deviceMarkers.forEach(marker => marker.setMap(null));
        }
        window.deviceMarkers = [];
        
        // Add new device markers
        autoDevices.forEach(device => {
          addDeviceMarker(googleMapRef.current, device);
        });
        
        // Center map on work zone
        googleMapRef.current.setCenter({ lat: startCoords.lat, lng: startCoords.lng });
      }

      toast.success(`Placed ${autoDevices.length} devices on road (not property) according to AGTTM standards`);
      
    } catch (error) {
      console.error('Auto-placement error:', error);
      toast.error(`Failed to auto-place devices: ${error.message}`);
    }
  };

  const geocodeAddress = async (address) => {
    const response = await fetch(`${API}/geocode?address=${encodeURIComponent(address)}`);
    if (!response.ok) throw new Error('Geocoding failed');
    return response.json();
  };

  const fetchRoadData = async () => {
    try {
      const response = await axios.get(`${API}/road-data`, {
        params: {
          start_address: formData.work_details.start_address,
          end_address: formData.work_details.end_address
        }
      });
      
      setFormData(prev => ({
        ...prev,
        road_data: {
          ...prev.road_data,
          ...response.data
        }
      }));
      
      toast.success('Road data updated');
    } catch (error) {
      toast.error('Failed to fetch road data');
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      
      if (planId) {
        await axios.put(`${API}/plans/${planId}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Plan updated successfully');
      } else {
        const response = await axios.post(`${API}/plans`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        navigate(`/plan/${response.data.id}`);
        toast.success('Plan created successfully');
      }
    } catch (error) {
      toast.error('Failed to save plan');
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!planId) {
      toast.error('Please save the plan first');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/plans/${planId}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${formData.plan_name.replace(/\s+/g, '_')}_traffic_plan.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
                className="border-slate-300"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-500 rounded-lg">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-800">
                    {planId ? 'Edit Plan' : 'New Plan'}
                  </h1>
                  <p className="text-sm text-slate-600">{formData.plan_name || 'Untitled Plan'}</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={handleSave}
                disabled={saving}
                className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white"
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save'}
              </Button>
              {planId && (
                <Button
                  variant="outline"
                  onClick={handleDownloadPdf}
                  className="border-slate-300 text-slate-700 hover:bg-slate-50"
                >
                  <Download className="w-4 h-4 mr-2" />
                  PDF
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Panel - Forms */}
          <div className="space-y-6">
            {/* Plan Details */}
            <Card>
              <CardHeader>
                <CardTitle>Plan Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="plan_name">Plan Name</Label>
                  <Input
                    id="plan_name"
                    value={formData.plan_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, plan_name: e.target.value }))}
                    placeholder="Enter plan name"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Company Details */}
            <Card>
              <CardHeader>
                <CardTitle>Primary Company Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Company Name</Label>
                    <Input
                      value={formData.company_details.name}
                      onChange={(e) => handleInputChange('company_details', 'name', e.target.value)}
                      placeholder="Company name"
                    />
                  </div>
                  <div>
                    <Label>ABN</Label>
                    <Input
                      value={formData.company_details.abn}
                      onChange={(e) => handleInputChange('company_details', 'abn', e.target.value)}
                      placeholder="ABN number"
                    />
                  </div>
                </div>
                <div>
                  <Label>Address</Label>
                  <Input
                    value={formData.company_details.address}
                    onChange={(e) => handleInputChange('company_details', 'address', e.target.value)}
                    placeholder="Company address"
                  />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Phone</Label>
                    <Input
                      value={formData.company_details.phone}
                      onChange={(e) => handleInputChange('company_details', 'phone', e.target.value)}
                      placeholder="Phone number"
                    />
                  </div>
                  <div>
                    <Label>Liaison Name</Label>
                    <Input
                      value={formData.company_details.liaison_name}
                      onChange={(e) => handleInputChange('company_details', 'liaison_name', e.target.value)}
                      placeholder="Liaison person name"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Work Details */}
            <Card>
              <CardHeader>
                <CardTitle>Work Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Work Type</Label>
                    <Select
                      value={formData.work_details.work_type}
                      onValueChange={(value) => handleInputChange('work_details', 'work_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select work type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="emergency">Emergency</SelectItem>
                        <SelectItem value="maintenance">Maintenance</SelectItem>
                        <SelectItem value="construction">Construction</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Work Style</Label>
                    <Select
                      value={formData.work_details.work_style}
                      onValueChange={(value) => handleInputChange('work_details', 'work_style', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select work style" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="static">Static</SelectItem>
                        <SelectItem value="mobile">Mobile</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={formData.work_details.description}
                    onChange={(e) => handleInputChange('work_details', 'description', e.target.value)}
                    placeholder="Describe the work to be completed"
                    rows={3}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Start Date</Label>
                    <Input
                      type="date"
                      value={formData.work_details.start_date}
                      onChange={(e) => handleInputChange('work_details', 'start_date', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>End Date</Label>
                    <Input
                      type="date"
                      value={formData.work_details.end_date}
                      onChange={(e) => handleInputChange('work_details', 'end_date', e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <Label>Start Address</Label>
                  <div className="flex gap-2">
                    <Input
                      value={formData.work_details.start_address}
                      onChange={(e) => handleInputChange('work_details', 'start_address', e.target.value)}
                      placeholder="Work zone start address"
                    />
                    <Button
                      variant="outline"
                      onClick={() => handleAddressGeocode(formData.work_details.start_address, true)}
                      disabled={!formData.work_details.start_address}
                    >
                      <MapPin className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div>
                  <Label>End Address</Label>
                  <div className="flex gap-2">
                    <Input
                      value={formData.work_details.end_address}
                      onChange={(e) => handleInputChange('work_details', 'end_address', e.target.value)}
                      placeholder="Work zone end address"
                    />
                    <Button
                      variant="outline"
                      onClick={() => handleAddressGeocode(formData.work_details.end_address, false)}
                      disabled={!formData.work_details.end_address}
                    >
                      <MapPin className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Road Occupancy */}
            <Card>
              <CardHeader>
                <CardTitle>Road Occupancy</CardTitle>
                <CardDescription>Select which areas of the road will be occupied</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(formData.road_occupancy).map(([key, value]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <Checkbox
                        id={key}
                        checked={value}
                        onCheckedChange={(checked) => handleInputChange('road_occupancy', key, checked)}
                      />
                      <Label htmlFor={key} className="text-sm">
                        {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Control Measures */}
            <Card>
              <CardHeader>
                <CardTitle>Control Measures</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(formData.control_measures).map(([key, value]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <Checkbox
                        id={key}
                        checked={value}
                        onCheckedChange={(checked) => handleInputChange('control_measures', key, checked)}
                      />
                      <Label htmlFor={key} className="text-sm">
                        {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Map and Devices */}
          <div className="space-y-6">
            {/* Map */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Traffic Management Plan</CardTitle>
                    <CardDescription>Click on the map to manually place devices, or use auto-placement</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleAutoPlaceDevices}
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white"
                      disabled={!formData.work_details.start_address || !formData.work_details.end_address}
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Auto-Place Devices
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setFormData(prev => ({ ...prev, devices: [] }))}
                      disabled={formData.devices.length === 0}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Clear All
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div 
                  ref={mapRef}
                  className="w-full h-96 bg-slate-100 rounded-lg border border-slate-200"
                >
                  <div className="flex items-center justify-center h-full text-slate-500">
                    Loading Google Maps...
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Device Library */}
            <Card>
              <CardHeader>
                <CardTitle>Traffic Control Devices</CardTitle>
                <CardDescription>Available Austroads-approved devices</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(TRAFFIC_DEVICES).map(([category, devices]) => (
                    <div key={category}>
                      <h4 className="font-medium text-slate-800 mb-2">{category}</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {devices.map((device, index) => (
                          <div
                            key={index}
                            className="p-3 border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer flex items-center gap-2"
                          >
                            <span className="text-lg">{device.icon}</span>
                            <div>
                              <div className="text-sm font-medium">{device.name}</div>
                              <Badge variant="outline" className="text-xs">
                                {device.type}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-orange-600" />
                  Risk Assessment
                </CardTitle>
                <CardDescription>
                  Identify and mitigate roadwork risks according to AS 1742.3 and AGTTM standards
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RiskMatrixInteractive 
                  formData={formData} 
                  setFormData={setFormData}
                />
              </CardContent>
            </Card>

            {/* Placed Devices */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Placed Devices ({formData.devices.length})</CardTitle>
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      <span>Auto-placed</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                      <span>Manual</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {formData.devices.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="p-4 bg-slate-50 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                      <MapPin className="w-8 h-8 text-slate-400" />
                    </div>
                    <p className="text-slate-500 mb-2">No devices placed yet</p>
                    <p className="text-xs text-slate-400 mb-4">
                      Use "Auto-Place Devices" or click on the map to add devices
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {formData.devices.map((device, index) => {
                      const isAutoPlaced = device.properties?.auto_placed;
                      return (
                        <div
                          key={device.id}
                          className="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50"
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${isAutoPlaced ? 'bg-blue-500' : 'bg-orange-500'}`}></div>
                            <span className="text-lg">{getDeviceIcon(device.device_type)}</span>
                            <div className="flex-1">
                              <div className="text-sm font-medium">{device.device_name}</div>
                              <div className="text-xs text-slate-500 flex items-center gap-2">
                                <span>{device.position_lat.toFixed(4)}, {device.position_lng.toFixed(4)}</span>
                                {isAutoPlaced && (
                                  <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                                    Auto
                                  </Badge>
                                )}
                                {device.properties?.distance && (
                                  <Badge variant="outline" className="text-xs">
                                    {device.properties.distance}
                                  </Badge>
                                )}
                              </div>
                              {isAutoPlaced && device.properties?.austroads_rule && (
                                <div className="text-xs text-blue-600 mt-1">
                                  {device.properties.austroads_rule}
                                </div>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => removeDevice(device.id)}
                            className="text-red-600 hover:bg-red-50 border-red-200"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
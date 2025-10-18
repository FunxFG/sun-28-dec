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
  Ruler,
  AlertCircle,
  Users,
  Cloud,
  AlertTriangle,
  CheckCircle,
  FileText
} from 'lucide-react';
import austroadsRules from '../utils/austroadsRules';
import tgsDrawingGenerator from '../utils/tgsDrawingGenerator';
import RiskMatrixInteractive from './RiskMatrixInteractive';
import { 
  ProjectOverviewSection,
  TrafficAssessmentSection,
  SiteAssessmentSection,
  SafetyPlanSection,
  ImplementationSection,
  MonitoringSection,
  ManagementReviewSection
} from './TMPFormSections';
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
    
    // Section 1: Company Information
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
    
    // Section 2: Project Overview (NEW - from template 2.1-2.5)
    project_overview: {
      location_description: '',
      project_purpose: '',
      site_constraints: '',
      special_requirements: '',
      coordinated_by: ''
    },
    
    // Section 3: Work Details
    work_details: {
      work_type: '',
      work_style: '',
      description: '',
      start_date: '',
      end_date: '',
      start_address: '',
      end_address: '',
      work_hours_start: '',
      work_hours_end: '',
      night_work: false,
      weekend_work: false
    },
    
    // Section 4: Traffic Assessment (NEW - from template 4.1)
    traffic_assessment: {
      aadt: '',  // Annual Average Daily Traffic
      peak_hour_volume: '',
      85th_percentile_speed: '',
      crash_history: '',
      heavy_vehicle_percentage: '',
      assessment_method: ''
    },
    
    // Section 5: Site Assessment (NEW - from template 5.0)
    site_assessment: {
      road_geometry: '',
      sight_distances: '',
      parking_restrictions: '',
      pedestrian_facilities: '',
      cyclist_facilities: '',
      public_transport: '',
      utility_services: '',
      environmental_factors: ''
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
    
    // Section 6: Safety Plan (NEW - from template 6.0)
    safety_plan: {
      whs_manager: '',
      site_safety_officer: '',
      safety_responsibilities: '',
      hazard_identification: '',
      risk_controls: '',
      emergency_procedures: '',
      incident_reporting: '',
      safety_induction_required: false
    },
    
    emergency_contacts: {
      primary_contact_name: '',
      primary_contact_phone: '',
      secondary_contact_name: '',
      secondary_contact_phone: '',
      emergency_services_notified: false,
      police_station: '',
      ambulance_service: '',
      incident_response_plan: ''
    },
    personnel: {
      site_supervisor_name: '',
      site_supervisor_phone: '',
      site_supervisor_qualifications: '',
      traffic_controller_1_name: '',
      traffic_controller_1_cert: '',
      traffic_controller_2_name: '',
      traffic_controller_2_cert: '',
      number_of_workers: '',
      all_personnel_inducted: false
    },
    permits_insurance: {
      road_occupation_permit_number: '',
      permit_issuing_authority: '',
      permit_issue_date: '',
      permit_expiry_date: '',
      public_liability_insurance: '',
      insurance_amount: '',
      insurance_expiry: '',
      workers_compensation_policy: ''
    },
    
    // Section 7: Implementation (NEW - from template 7.0)
    implementation: {
      installation_sequence: '',
      staging_requirements: '',
      tgs_drawing_numbers: '',
      device_setup_time: '',
      removal_sequence: '',
      handover_procedures: ''
    },
    
    approvals: {
      prepared_by_name: '',
      prepared_by_position: '',
      prepared_by_date: '',
      approved_by_name: '',
      approved_by_position: '',
      approved_by_signature: '',
      approved_by_date: '',
      declaration_accepted: false
    },
    environmental_conditions: {
      weather_considerations: '',
      visibility_requirements: '',
      rain_contingency: '',
      wind_speed_limit: '',
      temperature_considerations: ''
    },
    safety_communications: {
      worker_protection_measures: '',
      ppe_requirements: '',
      public_notification_method: '',
      advance_warning_days: '',
      media_release_required: false,
      resident_consultation: '',
      emergency_vehicle_access: ''
    },
    contingency_plans: {
      breakdown_procedure: '',
      accident_procedure: '',
      weather_delay_plan: '',
      traffic_buildup_response: '',
      alternative_routes: ''
    },
    
    // Section 9: Monitoring (NEW - from template 9.0)
    monitoring: {
      daily_inspection_required: false,
      inspection_frequency: '',
      inspection_checklist: '',
      defect_rectification: '',
      audit_schedule: '',
      responsible_person: ''
    },
    
    // Section 10: Management Review (NEW - from template 10.0)
    management_review: {
      review_frequency: '',
      review_process: '',
      variation_procedures: '',
      approval_authority: '',
      record_keeping: ''
    },
    
    devices: [],
    risk_assessment: {},
    detour_data: null,
    tgs_data: null,
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
      toast.info('Auto-populating TMP and calculating device placement...');
      
      // Get coordinates for start and end addresses
      const startCoords = await geocodeAddress(formData.work_details.start_address);
      const endCoords = await geocodeAddress(formData.work_details.end_address);
      
      // Get road data
      const roadDataResponse = await fetch(`${API}/road-data?start_address=${encodeURIComponent(formData.work_details.start_address)}&end_address=${encodeURIComponent(formData.work_details.end_address)}`);
      const roadData = await roadDataResponse.json();

      // AUTO-POPULATE TMP FORM
      const TMPAutoPopulator = (await import('../utils/tmpAutoPopulator.js')).default;
      const autoPopulator = new TMPAutoPopulator();
      
      const userProfile = JSON.parse(localStorage.getItem('user') || '{}');
      
      const minimalInputs = {
        work_type: formData.work_details.work_type,
        work_style: formData.work_details.work_style,
        start_address: formData.work_details.start_address,
        end_address: formData.work_details.end_address,
        start_date: formData.work_details.start_date,
        end_date: formData.work_details.end_date,
        road_occupancy: formData.road_occupancy
      };
      
      const autoPopulatedData = await autoPopulator.autoPopulateTMP(minimalInputs, userProfile, roadData);
      console.log('Auto-populated TMP data:', autoPopulatedData);
      
      // Merge auto-populated data with existing form data
      setFormData(prev => ({
        ...prev,
        ...autoPopulatedData,
        work_details: {
          ...prev.work_details,
          ...autoPopulatedData.work_details
        },
        road_data: roadData
      }));
      
      toast.success('TMP form auto-populated from minimal inputs!');

      // Google Maps API key for road snapping and detours
      const GOOGLE_MAPS_API_KEY = 'AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs';

      // Check if road closure requires detour routing
      const isRoadClosure = formData.road_occupancy?.complete_road_closure || 
                           formData.control_measures?.detour;
      
      let detourData = null;
      if (isRoadClosure) {
        toast.info('Road closure detected - calculating detour routes...');
        
        // Calculate detour routes
        const DetourRouter = (await import('../utils/detourRouter.js')).default;
        const detourRouter = new DetourRouter(GOOGLE_MAPS_API_KEY);
        
        const closureData = {
          start_lat: startCoords.lat,
          start_lng: startCoords.lng,
          end_lat: endCoords.lat,
          end_lng: endCoords.lng,
          closure_point: {
            lat: (startCoords.lat + endCoords.lat) / 2,
            lng: (startCoords.lng + endCoords.lng) / 2
          }
        };
        
        try {
          detourData = await detourRouter.calculateDetourRoutes(closureData);
          console.log('Detour routes calculated:', detourData);
          toast.success(`Detour routes: Vehicle ${detourData.vehicle_detour.distance}, Pedestrian ${detourData.pedestrian_detour.distance}`);
        } catch (error) {
          console.error('Detour calculation failed:', error);
          toast.warning('Could not calculate detours - continuing with standard placement');
        }
      }

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

      // Add detour signs if road closure
      let allDevices = autoDevices || [];
      if (detourData && detourData.detour_signs) {
        console.log(`Adding ${detourData.detour_signs.length} detour signs`);
        allDevices = [...allDevices, ...detourData.detour_signs];
      }

      // Generate TGS with precise measurements
      const mapDataForTGS = {
        start_lat: startCoords.lat,
        start_lng: startCoords.lng,
        end_lat: endCoords.lat,
        end_lng: endCoords.lng,
        center_lat: startCoords.lat,
        center_lng: startCoords.lng,
        workzone_size: roadData.workzone_size,
        speed_limit: roadData.speed_limit,
        road_classification: roadData.road_classification,
        project_name: formData.plan_name || 'Traffic Management Plan'
      };
      
      const tgsGenerator = await import('../utils/tgsDrawingGenerator.js');
      const tgsData = tgsGenerator.default.generateTGSPackage(formData, allDevices, mapDataForTGS);
      console.log('TGS Package generated:', tgsData);
      
      // Use devices with precise measurements
      const devicesWithMeasurements = tgsData.detailed_schedule?.devices?.map((scheduleItem, idx) => ({
        ...allDevices[idx],
        measurements: {
          gps_coordinates: {
            latitude: scheduleItem.gps_lat,
            longitude: scheduleItem.gps_lng,
            format: 'WGS84'
          },
          distance_from_workzone_start: scheduleItem.distance_from_start,
          distance_from_workzone_end: 'Calculated',
          lateral_offset_from_centerline: scheduleItem.lateral_offset,
          side_of_road: scheduleItem.side,
          position_description: scheduleItem.position_description,
          mounting_height: scheduleItem.mounting_height,
          clearance_from_carriageway: scheduleItem.clearance_from_edge
        }
      })) || allDevices;

      // Update form data with automatically placed devices
      setFormData(prev => ({
        ...prev,
        devices: devicesWithMeasurements,
        map_center_lat: startCoords.lat,
        map_center_lng: startCoords.lng,
        road_data: roadData,
        tgs_data: tgsData, // Store TGS package for PDF generation
        detour_data: detourData // Store detour information
      }));

      // Re-initialize map with new devices
      if (googleMapRef.current) {
        // Clear existing markers
        if (window.deviceMarkers) {
          window.deviceMarkers.forEach(marker => marker.setMap(null));
        }
        window.deviceMarkers = [];
        
        // Add new device markers
        devicesWithMeasurements.forEach(device => {
          addDeviceMarker(googleMapRef.current, device);
        });
        
        // Draw detour routes if available
        if (detourData) {
          const DetourRouter = (await import('../utils/detourRouter.js')).default;
          const detourRouter = new DetourRouter(GOOGLE_MAPS_API_KEY);
          const polylines = detourRouter.createDetourPolylines(
            detourData.vehicle_detour,
            detourData.pedestrian_detour
          );
          
          // Draw polylines on map
          polylines.forEach(polylineData => {
            const polyline = new window.google.maps.Polyline({
              path: polylineData.path,
              geodesic: true,
              strokeColor: polylineData.strokeColor,
              strokeOpacity: polylineData.strokeOpacity,
              strokeWeight: polylineData.strokeWeight,
              map: googleMapRef.current
            });
            
            // Add legend info window
            const infoContent = `
              <div style="padding: 8px;">
                <strong>${polylineData.type === 'vehicle' ? '🚗 Vehicle' : '🚶 Pedestrian'} Detour</strong><br>
                Distance: ${polylineData.distance}<br>
                Duration: ${polylineData.duration}
              </div>
            `;
            
            polyline.addListener('click', () => {
              if (!window.detourInfoWindow) {
                window.detourInfoWindow = new window.google.maps.InfoWindow();
              }
              window.detourInfoWindow.setContent(infoContent);
              window.detourInfoWindow.setPosition(polylineData.path[Math.floor(polylineData.path.length / 2)]);
              window.detourInfoWindow.open(googleMapRef.current);
            });
            
            if (!window.detourPolylines) window.detourPolylines = [];
            window.detourPolylines.push(polyline);
          });
          
          // Draw directional arrows
          if (detourData.directional_arrows) {
            detourData.directional_arrows.forEach(arrow => {
              const arrowMarker = new window.google.maps.Marker({
                position: arrow.location,
                map: googleMapRef.current,
                icon: {
                  path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                  scale: arrow.size === 'large' ? 6 : 4,
                  fillColor: arrow.color,
                  fillOpacity: 0.8,
                  strokeWeight: 2,
                  strokeColor: '#ffffff',
                  rotation: arrow.angle
                },
                title: arrow.instruction
              });
              
              if (!window.detourArrows) window.detourArrows = [];
              window.detourArrows.push(arrowMarker);
            });
          }
        }
        
        // Center map on work zone
        googleMapRef.current.setCenter({ lat: startCoords.lat, lng: startCoords.lng });
      }

      const totalDevices = devicesWithMeasurements.length;
      const detourInfo = detourData ? ` | Detours: Vehicle (${detourData.vehicle_detour.distance}), Pedestrian (${detourData.pedestrian_detour.distance})` : '';
      toast.success(`Placed ${totalDevices} devices with precise measurements${detourInfo}`);
      
      // Log TGS data for debugging
      if (tgsData.detailed_schedule) {
        console.log('📋 Detailed Device Schedule:', tgsData.detailed_schedule);
      }
      if (tgsData.taper_calculations) {
        console.log('📐 Taper Calculations:', tgsData.taper_calculations);
      }
      if (detourData) {
        const detourReport = new (await import('../utils/detourRouter.js')).default(GOOGLE_MAPS_API_KEY);
        const report = detourReport.generateDetourReport(detourData.vehicle_detour, detourData.pedestrian_detour);
        console.log('🚧 Detour Report:', report);
      }
      
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

            {/* Traffic Company Details */}
            <Card>
              <CardHeader>
                <CardTitle>Traffic Control Company Details</CardTitle>
                <CardDescription>
                  Details of the company providing traffic management services (if different from primary company)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Traffic Company Name</Label>
                    <Input
                      value={formData.traffic_company.name}
                      onChange={(e) => handleInputChange('traffic_company', 'name', e.target.value)}
                      placeholder="Traffic control company name"
                    />
                  </div>
                  <div>
                    <Label>Phone</Label>
                    <Input
                      value={formData.traffic_company.phone}
                      onChange={(e) => handleInputChange('traffic_company', 'phone', e.target.value)}
                      placeholder="Phone number"
                    />
                  </div>
                </div>
                <div>
                  <Label>Address</Label>
                  <Input
                    value={formData.traffic_company.address}
                    onChange={(e) => handleInputChange('traffic_company', 'address', e.target.value)}
                    placeholder="Traffic company address"
                  />
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Liaison Name</Label>
                    <Input
                      value={formData.traffic_company.liaison_name}
                      onChange={(e) => handleInputChange('traffic_company', 'liaison_name', e.target.value)}
                      placeholder="Contact person name"
                    />
                  </div>
                  <div>
                    <Label>Liaison Phone</Label>
                    <Input
                      value={formData.traffic_company.liaison_phone}
                      onChange={(e) => handleInputChange('traffic_company', 'liaison_phone', e.target.value)}
                      placeholder="Contact phone"
                    />
                  </div>
                  <div>
                    <Label>Liaison Email</Label>
                    <Input
                      value={formData.traffic_company.liaison_email}
                      onChange={(e) => handleInputChange('traffic_company', 'liaison_email', e.target.value)}
                      placeholder="Contact email"
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
                    <Label>Work Hours Start</Label>
                    <Input
                      type="time"
                      value={formData.work_details.work_hours_start}
                      onChange={(e) => handleInputChange('work_details', 'work_hours_start', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Work Hours End</Label>
                    <Input
                      type="time"
                      value={formData.work_details.work_hours_end}
                      onChange={(e) => handleInputChange('work_details', 'work_hours_end', e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex gap-6">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="night_work"
                      checked={formData.work_details.night_work}
                      onChange={(e) => handleInputChange('work_details', 'night_work', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="night_work">Night Work (6pm-7am)</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="weekend_work"
                      checked={formData.work_details.weekend_work}
                      onChange={(e) => handleInputChange('work_details', 'weekend_work', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="weekend_work">Weekend Work</Label>
                  </div>
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

            {/* Emergency Contacts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  Emergency Contacts & Response
                </CardTitle>
                <CardDescription>24/7 emergency contact information and incident response procedures</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Primary Emergency Contact Name</Label>
                    <Input
                      value={formData.emergency_contacts.primary_contact_name}
                      onChange={(e) => handleInputChange('emergency_contacts', 'primary_contact_name', e.target.value)}
                      placeholder="24/7 contact person"
                    />
                  </div>
                  <div>
                    <Label>Primary Emergency Contact Phone</Label>
                    <Input
                      value={formData.emergency_contacts.primary_contact_phone}
                      onChange={(e) => handleInputChange('emergency_contacts', 'primary_contact_phone', e.target.value)}
                      placeholder="Mobile number"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Secondary Emergency Contact Name</Label>
                    <Input
                      value={formData.emergency_contacts.secondary_contact_name}
                      onChange={(e) => handleInputChange('emergency_contacts', 'secondary_contact_name', e.target.value)}
                      placeholder="Backup contact"
                    />
                  </div>
                  <div>
                    <Label>Secondary Emergency Contact Phone</Label>
                    <Input
                      value={formData.emergency_contacts.secondary_contact_phone}
                      onChange={(e) => handleInputChange('emergency_contacts', 'secondary_contact_phone', e.target.value)}
                      placeholder="Mobile number"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Local Police Station</Label>
                    <Input
                      value={formData.emergency_contacts.police_station}
                      onChange={(e) => handleInputChange('emergency_contacts', 'police_station', e.target.value)}
                      placeholder="Station name and phone"
                    />
                  </div>
                  <div>
                    <Label>Ambulance Service</Label>
                    <Input
                      value={formData.emergency_contacts.ambulance_service}
                      onChange={(e) => handleInputChange('emergency_contacts', 'ambulance_service', e.target.value)}
                      placeholder="Nearest ambulance station"
                    />
                  </div>
                </div>
                <div>
                  <Label>Incident Response Procedure</Label>
                  <Textarea
                    value={formData.emergency_contacts.incident_response_plan}
                    onChange={(e) => handleInputChange('emergency_contacts', 'incident_response_plan', e.target.value)}
                    placeholder="Step-by-step incident response procedure"
                    rows={3}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="emergency_services_notified"
                    checked={formData.emergency_contacts.emergency_services_notified}
                    onChange={(e) => handleInputChange('emergency_contacts', 'emergency_services_notified', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="emergency_services_notified">Emergency Services Pre-Notified of Works</Label>
                </div>
              </CardContent>
            </Card>

            {/* Personnel & Qualifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  Personnel & Qualifications
                </CardTitle>
                <CardDescription>Site personnel details and certification verification</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Site Supervisor Name</Label>
                    <Input
                      value={formData.personnel.site_supervisor_name}
                      onChange={(e) => handleInputChange('personnel', 'site_supervisor_name', e.target.value)}
                      placeholder="Supervisor name"
                    />
                  </div>
                  <div>
                    <Label>Supervisor Phone</Label>
                    <Input
                      value={formData.personnel.site_supervisor_phone}
                      onChange={(e) => handleInputChange('personnel', 'site_supervisor_phone', e.target.value)}
                      placeholder="Contact number"
                    />
                  </div>
                  <div>
                    <Label>Qualifications / Cert Numbers</Label>
                    <Input
                      value={formData.personnel.site_supervisor_qualifications}
                      onChange={(e) => handleInputChange('personnel', 'site_supervisor_qualifications', e.target.value)}
                      placeholder="e.g., RIIWHS205D"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Traffic Controller 1 Name</Label>
                    <Input
                      value={formData.personnel.traffic_controller_1_name}
                      onChange={(e) => handleInputChange('personnel', 'traffic_controller_1_name', e.target.value)}
                      placeholder="Controller name"
                    />
                  </div>
                  <div>
                    <Label>Certification Number</Label>
                    <Input
                      value={formData.personnel.traffic_controller_1_cert}
                      onChange={(e) => handleInputChange('personnel', 'traffic_controller_1_cert', e.target.value)}
                      placeholder="Cert number"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Traffic Controller 2 Name</Label>
                    <Input
                      value={formData.personnel.traffic_controller_2_name}
                      onChange={(e) => handleInputChange('personnel', 'traffic_controller_2_name', e.target.value)}
                      placeholder="Controller name"
                    />
                  </div>
                  <div>
                    <Label>Certification Number</Label>
                    <Input
                      value={formData.personnel.traffic_controller_2_cert}
                      onChange={(e) => handleInputChange('personnel', 'traffic_controller_2_cert', e.target.value)}
                      placeholder="Cert number"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Total Number of Workers on Site</Label>
                    <Input
                      type="number"
                      value={formData.personnel.number_of_workers}
                      onChange={(e) => handleInputChange('personnel', 'number_of_workers', e.target.value)}
                      placeholder="Number"
                    />
                  </div>
                  <div className="flex items-center gap-2 pt-6">
                    <input
                      type="checkbox"
                      id="all_inducted"
                      checked={formData.personnel.all_personnel_inducted}
                      onChange={(e) => handleInputChange('personnel', 'all_personnel_inducted', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="all_inducted">All Personnel Site Inducted</Label>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Permits & Insurance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-green-600" />
                  Permits, Insurance & Compliance
                </CardTitle>
                <CardDescription>Legal documentation and insurance coverage</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Road Occupation Permit Number</Label>
                    <Input
                      value={formData.permits_insurance.road_occupation_permit_number}
                      onChange={(e) => handleInputChange('permits_insurance', 'road_occupation_permit_number', e.target.value)}
                      placeholder="Permit number"
                    />
                  </div>
                  <div>
                    <Label>Permit Issuing Authority</Label>
                    <Input
                      value={formData.permits_insurance.permit_issuing_authority}
                      onChange={(e) => handleInputChange('permits_insurance', 'permit_issuing_authority', e.target.value)}
                      placeholder="e.g., Main Roads, Local Council"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Permit Issue Date</Label>
                    <Input
                      type="date"
                      value={formData.permits_insurance.permit_issue_date}
                      onChange={(e) => handleInputChange('permits_insurance', 'permit_issue_date', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Permit Expiry Date</Label>
                    <Input
                      type="date"
                      value={formData.permits_insurance.permit_expiry_date}
                      onChange={(e) => handleInputChange('permits_insurance', 'permit_expiry_date', e.target.value)}
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Public Liability Insurance Policy Number</Label>
                    <Input
                      value={formData.permits_insurance.public_liability_insurance}
                      onChange={(e) => handleInputChange('permits_insurance', 'public_liability_insurance', e.target.value)}
                      placeholder="Policy number"
                    />
                  </div>
                  <div>
                    <Label>Coverage Amount</Label>
                    <Input
                      value={formData.permits_insurance.insurance_amount}
                      onChange={(e) => handleInputChange('permits_insurance', 'insurance_amount', e.target.value)}
                      placeholder="e.g., $20,000,000"
                    />
                  </div>
                  <div>
                    <Label>Insurance Expiry</Label>
                    <Input
                      type="date"
                      value={formData.permits_insurance.insurance_expiry}
                      onChange={(e) => handleInputChange('permits_insurance', 'insurance_expiry', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <Label>Workers Compensation Policy Number</Label>
                  <Input
                    value={formData.permits_insurance.workers_compensation_policy}
                    onChange={(e) => handleInputChange('permits_insurance', 'workers_compensation_policy', e.target.value)}
                    placeholder="Policy number"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Environmental Conditions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-gray-600" />
                  Environmental Conditions & Contingencies
                </CardTitle>
                <CardDescription>Weather considerations and environmental management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Weather Considerations</Label>
                  <Textarea
                    value={formData.environmental_conditions.weather_considerations}
                    onChange={(e) => handleInputChange('environmental_conditions', 'weather_considerations', e.target.value)}
                    placeholder="Expected weather conditions and limitations"
                    rows={2}
                  />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Minimum Visibility Requirements</Label>
                    <Input
                      value={formData.environmental_conditions.visibility_requirements}
                      onChange={(e) => handleInputChange('environmental_conditions', 'visibility_requirements', e.target.value)}
                      placeholder="e.g., 100m minimum, additional lighting required"
                    />
                  </div>
                  <div>
                    <Label>Maximum Wind Speed</Label>
                    <Input
                      value={formData.environmental_conditions.wind_speed_limit}
                      onChange={(e) => handleInputChange('environmental_conditions', 'wind_speed_limit', e.target.value)}
                      placeholder="e.g., 50 km/h"
                    />
                  </div>
                </div>
                <div>
                  <Label>Rain Contingency Plan</Label>
                  <Textarea
                    value={formData.environmental_conditions.rain_contingency}
                    onChange={(e) => handleInputChange('environmental_conditions', 'rain_contingency', e.target.value)}
                    placeholder="Actions if heavy rain occurs"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Temperature Considerations</Label>
                  <Input
                    value={formData.environmental_conditions.temperature_considerations}
                    onChange={(e) => handleInputChange('environmental_conditions', 'temperature_considerations', e.target.value)}
                    placeholder="Heat/cold management for workers"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Safety & Communications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-purple-600" />
                  Safety Measures & Public Communications
                </CardTitle>
                <CardDescription>Worker protection and stakeholder communication</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Worker Protection Measures</Label>
                  <Textarea
                    value={formData.safety_communications.worker_protection_measures}
                    onChange={(e) => handleInputChange('safety_communications', 'worker_protection_measures', e.target.value)}
                    placeholder="Barriers, signage, safety zones, etc."
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Required PPE (Personal Protective Equipment)</Label>
                  <Input
                    value={formData.safety_communications.ppe_requirements}
                    onChange={(e) => handleInputChange('safety_communications', 'ppe_requirements', e.target.value)}
                    placeholder="e.g., High-vis, hard hat, safety boots, hearing protection"
                  />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Public Notification Method</Label>
                    <Input
                      value={formData.safety_communications.public_notification_method}
                      onChange={(e) => handleInputChange('safety_communications', 'public_notification_method', e.target.value)}
                      placeholder="e.g., Letterbox drop, website, VMS signs"
                    />
                  </div>
                  <div>
                    <Label>Advance Warning (Days)</Label>
                    <Input
                      type="number"
                      value={formData.safety_communications.advance_warning_days}
                      onChange={(e) => handleInputChange('safety_communications', 'advance_warning_days', e.target.value)}
                      placeholder="Days before work starts"
                    />
                  </div>
                </div>
                <div>
                  <Label>Resident Consultation Records</Label>
                  <Textarea
                    value={formData.safety_communications.resident_consultation}
                    onChange={(e) => handleInputChange('safety_communications', 'resident_consultation', e.target.value)}
                    placeholder="Summary of consultation with affected residents/businesses"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Emergency Vehicle Access Plan</Label>
                  <Input
                    value={formData.safety_communications.emergency_vehicle_access}
                    onChange={(e) => handleInputChange('safety_communications', 'emergency_vehicle_access', e.target.value)}
                    placeholder="How emergency vehicles will access the area"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="media_release"
                    checked={formData.safety_communications.media_release_required}
                    onChange={(e) => handleInputChange('safety_communications', 'media_release_required', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="media_release">Media Release Required</Label>
                </div>
              </CardContent>
            </Card>

            {/* Contingency Plans */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                  Contingency Plans
                </CardTitle>
                <CardDescription>Emergency procedures and backup plans</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Equipment Breakdown Procedure</Label>
                  <Textarea
                    value={formData.contingency_plans.breakdown_procedure}
                    onChange={(e) => handleInputChange('contingency_plans', 'breakdown_procedure', e.target.value)}
                    placeholder="Steps if equipment breaks down during works"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Accident/Incident Procedure</Label>
                  <Textarea
                    value={formData.contingency_plans.accident_procedure}
                    onChange={(e) => handleInputChange('contingency_plans', 'accident_procedure', e.target.value)}
                    placeholder="Immediate response to accidents"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Weather Delay Management</Label>
                  <Textarea
                    value={formData.contingency_plans.weather_delay_plan}
                    onChange={(e) => handleInputChange('contingency_plans', 'weather_delay_plan', e.target.value)}
                    placeholder="Actions if weather delays works"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Traffic Buildup Response</Label>
                  <Textarea
                    value={formData.contingency_plans.traffic_buildup_response}
                    onChange={(e) => handleInputChange('contingency_plans', 'traffic_buildup_response', e.target.value)}
                    placeholder="Actions if excessive traffic queuing occurs"
                    rows={2}
                  />
                </div>
                <div>
                  <Label>Alternative Routes</Label>
                  <Textarea
                    value={formData.contingency_plans.alternative_routes}
                    onChange={(e) => handleInputChange('contingency_plans', 'alternative_routes', e.target.value)}
                    placeholder="Backup routes if primary detour fails"
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Approvals & Declaration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Approvals & Declaration
                </CardTitle>
                <CardDescription>Plan preparation and approval signatures</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Prepared By (Name)</Label>
                    <Input
                      value={formData.approvals.prepared_by_name}
                      onChange={(e) => handleInputChange('approvals', 'prepared_by_name', e.target.value)}
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <Label>Position</Label>
                    <Input
                      value={formData.approvals.prepared_by_position}
                      onChange={(e) => handleInputChange('approvals', 'prepared_by_position', e.target.value)}
                      placeholder="e.g., Traffic Manager"
                    />
                  </div>
                  <div>
                    <Label>Date</Label>
                    <Input
                      type="date"
                      value={formData.approvals.prepared_by_date}
                      onChange={(e) => handleInputChange('approvals', 'prepared_by_date', e.target.value)}
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Approved By (Name)</Label>
                    <Input
                      value={formData.approvals.approved_by_name}
                      onChange={(e) => handleInputChange('approvals', 'approved_by_name', e.target.value)}
                      placeholder="Approver name"
                    />
                  </div>
                  <div>
                    <Label>Position</Label>
                    <Input
                      value={formData.approvals.approved_by_position}
                      onChange={(e) => handleInputChange('approvals', 'approved_by_position', e.target.value)}
                      placeholder="e.g., Project Manager"
                    />
                  </div>
                  <div>
                    <Label>Approval Date</Label>
                    <Input
                      type="date"
                      value={formData.approvals.approved_by_date}
                      onChange={(e) => handleInputChange('approvals', 'approved_by_date', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <Label>Signature (Type Full Name)</Label>
                  <Input
                    value={formData.approvals.approved_by_signature}
                    onChange={(e) => handleInputChange('approvals', 'approved_by_signature', e.target.value)}
                    placeholder="Full name as signature"
                  />
                </div>
                <div className="bg-blue-50 p-4 rounded-lg space-y-2">
                  <p className="text-sm font-medium">Declaration</p>
                  <p className="text-xs text-gray-700">
                    I declare that this Traffic Management Plan has been prepared in accordance with AS 1742.3 
                    and the Austroads Guide to Temporary Traffic Management (AGTTM). All information provided 
                    is accurate and complete to the best of my knowledge. All personnel are appropriately 
                    qualified and all necessary permits and insurance are in place.
                  </p>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="declaration"
                      checked={formData.approvals.declaration_accepted}
                      onChange={(e) => handleInputChange('approvals', 'declaration_accepted', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="declaration" className="font-medium">I accept this declaration</Label>
                  </div>
                </div>
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
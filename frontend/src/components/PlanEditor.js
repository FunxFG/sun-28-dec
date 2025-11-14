import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import VisualTGSViewer from './VisualTGSViewer';
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
  FileText,
  Eye
} from 'lucide-react';
import austroadsRules from '../utils/austroadsRules';
import tgsDrawingGenerator from '../utils/tgsDrawingGenerator';
import { ProfessionalTGSGenerator } from '../utils/professionalTGSGenerator';
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://tmp-generator.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

// Download helper functions
const downloadCSV = (data, filename) => {
  const blob = new Blob([data], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const downloadJSON = (data, filename) => {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const downloadText = (data, filename) => {
  const blob = new Blob([data], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

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
  
  // State for auto-population tracking
  const [autoPopulationComplete, setAutoPopulationComplete] = useState(false);
  const [showAutoPopulatedData, setShowAutoPopulatedData] = useState(false);
  const [autoPopulationWarnings, setAutoPopulationWarnings] = useState([]);
  
  // State for comprehensive auto-population data
  const [comprehensiveData, setComprehensiveData] = useState({
    side_streets: [],
    intersections: [],
    signage_plan: null,
    pedestrian_control_measures: null,
    public_facilities: null,
    governing_body_details: null,
    staging_recommendations: null,
    crash_statistics: null,  // NEW
    historical_traffic: null,  // NEW
    location_history: null,  // NEW
    current_roadworks: null,  // NEW - Traffic SA data
    traffic_signals: null,  // NEW
    parking_restrictions: null,  // NEW
    school_zones: null,  // NEW
    public_transport_detailed: null,  // NEW
    utility_infrastructure: null,  // NEW
    location_metadata_system: null,  // NEW: LMS
    dit_infrastructure_assets: null,  // NEW: DIT Assets
    dilapidation_report: null,  // NEW: Professional TMP
    traffic_volumes: null,  // NEW: Professional TMP
    comprehensive_risk_assessment: null,  // NEW: Professional TMP
    permit_application: null,  // NEW: Professional TMP
    field_guide_zones: null  // NEW: Professional TMP
  });

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
      '85th_percentile_speed': '',
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
      detour: false,
      pedestrian_control: false
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
      
      // Validate required data before attempting placement
      if (!workZoneData.start_lat || !workZoneData.end_lat) {
        throw new Error('Invalid coordinates for auto-placement');
      }
      
      // Ensure road geometry has minimum required data
      if (!roadGeometry || !roadGeometry.road_name) {
        console.warn('Limited road geometry data, using defaults');
        roadGeometry = {
          ...roadGeometry,
          road_name: formData.work_details.start_address || 'Unknown Road',
          lanes: roadGeometry?.lanes || 2,
          speed_limit: workZoneData.speed_limit || 60
        };
      }
      
      const autoDevices = await agttmRules.default.calculateAGTTMCompliantPlacement(
        workZoneData,
        roadGeometry,
        GOOGLE_MAPS_API_KEY
      );

      console.log('Auto-placement complete. Devices returned:', autoDevices);
      console.log('Device count:', autoDevices?.length || 0);

      // Check if auto-placement returned devices
      if (!autoDevices || autoDevices.length === 0) {
        console.warn('⚠️ Auto-placement returned no devices');
        toast.warning('Auto-placement completed but no devices were generated. This might be due to insufficient road data. Try manual placement or a different location.');
      }

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
      console.error('❌ Auto-placement error:', error);
      console.error('Error stack:', error.stack);
      
      // Provide helpful error messages based on error type
      let errorMessage = 'Failed to auto-place devices';
      if (error.message.includes('geocode')) {
        errorMessage = 'Failed to geocode addresses. Please check your addresses and try again.';
      } else if (error.message.includes('coordinates')) {
        errorMessage = 'Invalid location coordinates. Please enter valid addresses.';
      } else if (error.message.includes('road')) {
        errorMessage = 'Could not retrieve road data. The location might not have sufficient mapping data.';
      } else {
        errorMessage = `Auto-placement failed: ${error.message}`;
      }
      
      toast.error(errorMessage);
      
      // Show detailed error in console for debugging
      console.log('📋 Debug Info:');
      console.log('- Start Address:', formData.work_details.start_address);
      console.log('- End Address:', formData.work_details.end_address);
      console.log('- Work Type:', formData.work_type);
      console.log('- Error:', error);
    }
  };

  const geocodeAddress = async (address) => {
    const response = await fetch(`${API}/geocode?address=${encodeURIComponent(address)}`);
    if (!response.ok) throw new Error('Geocoding failed');
    return response.json();
  };

  // NEW: Fetch Professional TMP data from new modules
  const fetchProfessionalTMPData = async (roadData, trafficData) => {
    try {
      // Fetch Dilapidation Report
      try {
        const dilapidationResponse = await axios.post(`${API}/dilapidation/generate`, {
          location: formData?.work_details?.start_address || 'TBC',
          report_type: 'pre-construction',
          inspector_name: formData?.company_details?.name || 'TBC'
        });
        setComprehensiveData(prev => ({
          ...prev,
          dilapidation_report: dilapidationResponse.data.report
        }));
      } catch (error) {
        console.log('Dilapidation report generation skipped:', error.message);
      }

      // Fetch Traffic Volumes
      try {
        const volumesResponse = await axios.post(`${API}/traffic-volume/calculate`, {
          road_type: roadData?.road_classification?.toLowerCase() || 'arterial',
          location_type: 'urban',
          existing_aadt: trafficData?.aadt || 10000
        });
        setComprehensiveData(prev => ({
          ...prev,
          traffic_volumes: volumesResponse.data.traffic_volumes
        }));
      } catch (error) {
        console.log('Traffic volumes calculation skipped:', error.message);
      }

      // Fetch Comprehensive Risk Assessment
      try {
        const riskResponse = await axios.post(`${API}/risk-assessment/generate`, {
          work_type: formData?.work_details?.work_type || 'construction',
          road_classification: roadData?.road_classification || 'arterial',
          speed_limit: roadData?.speed_limit || 60,
          traffic_volume: trafficData?.aadt || 10000,
          clearance: 3.0,
          weather_conditions: 'normal'
        });
        setComprehensiveData(prev => ({
          ...prev,
          comprehensive_risk_assessment: riskResponse.data.risk_assessment
        }));
      } catch (error) {
        console.log('Risk assessment generation skipped:', error.message);
      }

      // Fetch Permit Application
      try {
        const permitResponse = await axios.post(`${API}/permit/application`, {
          location: formData?.work_details?.start_address || 'TBC',
          work_type: formData?.work_details?.work_type || 'Lane Closure',
          start_date: formData?.work_details?.start_date || '01/01/2025',
          end_date: formData?.work_details?.end_date || '31/12/2025',
          work_hours: '7am-5pm',
          applicant_details: {
            company_name: formData?.company_details?.name || 'TBC',
            abn: formData?.company_details?.abn || 'TBC',
            contact_person: formData?.company_details?.liaison_name || 'TBC',
            phone: formData?.company_details?.phone || 'TBC',
            email: formData?.company_details?.liaison_email || 'TBC'
          }
        });
        setComprehensiveData(prev => ({
          ...prev,
          permit_application: permitResponse.data.permit_application
        }));
      } catch (error) {
        console.log('Permit application generation skipped:', error.message);
      }

      // Fetch Field Guide Zones
      try {
        const zonesResponse = await axios.post(`${API}/field-guide/calculate-zones`, {
          speed_limit: roadData?.speed_limit || 60,
          work_length: roadData?.workzone_size || 100,
          lane_closure: formData?.road_occupancy?.lane_closure === true
        });
        setComprehensiveData(prev => ({
          ...prev,
          field_guide_zones: zonesResponse.data.zones
        }));
      } catch (error) {
        console.log('Field guide zones calculation skipped:', error.message);
      }

      toast.success('Professional TMP data loaded successfully!');
    } catch (error) {
      console.error('Error fetching professional TMP data:', error);
    }
  };

  const fetchRoadData = async () => {
    try {
      // Fetch road data
      const roadResponse = await axios.get(`${API}/road-data`, {
        params: {
          start_address: formData.work_details.start_address,
          end_address: formData.work_details.end_address
        }
      });
      
      const roadData = roadResponse.data;
      
      // Fetch traffic assessment data (includes SA Government official traffic volumes)
      const trafficResponse = await axios.get(`${API}/traffic-assessment`, {
        params: {
          lat: roadData.start_coords.lat,
          lng: roadData.start_coords.lng,
          address: formData.work_details.start_address
        }
      });
      
      const trafficData = trafficResponse.data;
      
      // Fetch site assessment data (road geometry, facilities, utilities)
      const siteResponse = await axios.get(`${API}/site-assessment`, {
        params: {
          lat: roadData.start_coords.lat,
          lng: roadData.start_coords.lng,
          address: formData.work_details.start_address
        }
      });
      
      const siteData = siteResponse.data;
      
      // Fetch comprehensive auto-population (NEW - includes pedestrian control, signage plan, side streets)
      let comprehensiveDataResponse = null;
      try {
        const comprehensiveResponse = await axios.get(`${API}/comprehensive-auto-populate`, {
          params: {
            lat: roadData.start_coords.lat,
            lng: roadData.start_coords.lng,
            start_address: formData.work_details.start_address,
            end_address: formData.work_details.end_address,
            work_type: formData.work_details.work_type
          }
        });
        comprehensiveDataResponse = comprehensiveResponse.data;
        
        // Store comprehensive data in state for UI display
        setComprehensiveData({
          side_streets: comprehensiveDataResponse.side_streets || [],
          intersections: comprehensiveDataResponse.intersections || [],
          signage_plan: comprehensiveDataResponse.signage_plan || null,
          pedestrian_control_measures: comprehensiveDataResponse.pedestrian_control_measures || null,
          public_facilities: comprehensiveDataResponse.public_facilities || null,
          governing_body_details: comprehensiveDataResponse.governing_body_details || null,
          staging_recommendations: comprehensiveDataResponse.staging_recommendations || null,
          crash_statistics: comprehensiveDataResponse.crash_statistics || null,
          historical_traffic: comprehensiveDataResponse.historical_traffic || null,
          location_history: comprehensiveDataResponse.location_history || null,
          current_roadworks: comprehensiveDataResponse.current_roadworks || null,
          traffic_signals: comprehensiveDataResponse.traffic_signals || null,  // NEW
          parking_restrictions: comprehensiveDataResponse.parking_restrictions || null,  // NEW
          school_zones: comprehensiveDataResponse.school_zones || null,  // NEW
          public_transport_detailed: comprehensiveDataResponse.public_transport_detailed || null,  // NEW
          utility_infrastructure: comprehensiveDataResponse.utility_infrastructure || null,  // NEW
          location_metadata_system: comprehensiveDataResponse.location_metadata_system || null,  // NEW: LMS
          dit_infrastructure_assets: comprehensiveDataResponse.dit_infrastructure_assets || null,  // NEW: DIT Assets
          sa_traffic_intelligence: comprehensiveDataResponse.sa_traffic_intelligence || null,  // NEW: Top 40 Roads/Intersections/Travel Speeds
          dilapidation_report: null,  // Will be fetched separately
          traffic_volumes: null,  // Will be fetched separately
          comprehensive_risk_assessment: null,  // Will be fetched separately
          permit_application: null,  // Will be fetched separately
          field_guide_zones: null  // Will be fetched separately
        });
        
        // Fetch professional TMP data (NEW modules)
        await fetchProfessionalTMPData(roadData, trafficData);
        
      } catch (error) {
        console.log('Comprehensive auto-populate not available, continuing with basic data');
      }
      
      // Update form data with road, traffic, site AND comprehensive auto-population data
      setFormData(prev => ({
        ...prev,
        road_data: {
          ...prev.road_data,
          ...roadData,
          // Merge traffic assessment data
          aadt: trafficData.aadt,
          peak_hour_volume: trafficData.peak_hour_volume,
          traffic_data_source: trafficData.data_source,
          traffic_assessment_method: trafficData.assessment_method,
          heavy_vehicle_percentage: trafficData.heavy_vehicle_percentage
        },
        // Update traffic assessment section
        traffic_assessment: {
          ...prev.traffic_assessment,
          aadt: trafficData.aadt,
          peak_hour_volume: trafficData.peak_hour_volume,
          percentile_85_speed: trafficData['85th_percentile_speed'],
          heavy_vehicle_percentage: trafficData.heavy_vehicle_percentage,
          crash_history: trafficData.crash_history,
          data_source: trafficData.data_source
        },
        // Update site assessment section
        site_assessment: {
          ...prev.site_assessment,
          road_geometry: siteData.road_geometry,
          sight_distances: siteData.sight_distances,
          parking_restrictions: siteData.parking_restrictions,
          pedestrian_facilities: siteData.pedestrian_facilities,
          cyclist_facilities: siteData.cyclist_facilities,
          public_transport: siteData.public_transport,
          utility_services: siteData.utility_services,
          environmental_factors: siteData.environmental_factors
        },
        // Update control measures with pedestrian control if comprehensive data available
        control_measures: {
          ...prev.control_measures,
          // Auto-check pedestrian_control if pedestrian facilities detected or comprehensive data suggests it
          pedestrian_control: comprehensiveDataResponse?.pedestrian_control_measures?.barriers_required?.length > 0 ||
                            siteData.pedestrian_facilities?.includes('sidewalk') ||
                            siteData.pedestrian_facilities?.includes('footpath') ||
                            false
        }
      }));
      
      // Check for auto-population warnings (zero/missing data)
      const warnings = [];
      if (!trafficData.aadt || trafficData.aadt === 0) {
        warnings.push('⚠️ Traffic Assessment: No AADT data - manual input may be required');
      }
      if (!siteData.road_geometry || !siteData.road_geometry.includes('lane')) {
        warnings.push('⚠️ Site Assessment: Limited road geometry data - manual input may be required');
      }
      if (!comprehensiveDataResponse?.sa_traffic_intelligence?.top_40_road_analysis?.is_top_40_road 
          && !comprehensiveDataResponse?.sa_traffic_intelligence?.top_40_intersection_analysis?.is_top_40_intersection) {
        // This is informational, not a warning
      }
      
      setAutoPopulationWarnings(warnings);
      setAutoPopulationComplete(true);
      
      // Show warnings if any
      if (warnings.length > 0) {
        warnings.forEach(warning => toast.warning(warning, { duration: 6000 }));
      }
      
      // Show comprehensive success message
      let message = '✅ Auto-population complete! Review data before generating TMP.';
      if (trafficData.data_source.includes('SA Government')) {
        message = '✅ Complete assessment: SA Gov traffic data + OSM site facilities!';
      }
      if (comprehensiveDataResponse?.sa_traffic_intelligence?.top_40_road_analysis?.is_top_40_road) {
        message += ' Top 40 Road detected!';
      }
      if (comprehensiveDataResponse?.pedestrian_control_measures?.barriers_required?.length > 0) {
        message += ' Pedestrian control measures detected!';
      }
      if (comprehensiveDataResponse?.side_streets?.length > 0) {
        message += ` ${comprehensiveDataResponse.side_streets.length} side streets detected!`;
      }
      toast.success(message);
      
    } catch (error) {
      console.error('Error fetching road/traffic/site data:', error);
      toast.error('Failed to fetch complete assessment data');
      setAutoPopulationComplete(false);
    }
  };


  // Export Functions for Comprehensive Data
  const exportSideStreetsCSV = () => {
    if (!comprehensiveData.side_streets || comprehensiveData.side_streets.length === 0) {
      toast.error('No side streets data to export');
      return;
    }

    let csv = 'Street Name,Type,Reference\n';
    comprehensiveData.side_streets.forEach(street => {
      csv += `"${street.name}","${street.type}","${street.ref || 'N/A'}"\n`;
    });

    downloadCSV(csv, `side_streets_${formData.plan_name || 'plan'}.csv`);
    toast.success('Side streets exported to CSV');
  };

  const exportSignagePlanText = () => {
    if (!comprehensiveData.signage_plan) {
      toast.error('No signage plan data to export');
      return;
    }

    const plan = comprehensiveData.signage_plan;
    let text = '═══════════════════════════════════════════════════\n';
    text += '   AUSTROADS TMP SIGNAGE PLAN (AS 1742.3)\n';
    text += '═══════════════════════════════════════════════════\n\n';

    // Distances
    if (plan.distances_documented) {
      text += '📏 DOCUMENTED DISTANCES\n';
      text += '─────────────────────────────────────────────────\n';
      text += `Speed Limit: ${plan.distances_documented.speed_limit}\n`;
      text += `Advance Warning Distance: ${plan.distances_documented.advance_warning_distance}\n`;
      text += `Taper Length: ${plan.distances_documented.taper_length}\n`;
      text += `Buffer Zone: ${plan.distances_documented.buffer_zone}\n`;
      text += `Standard: ${plan.distances_documented.standard_reference}\n\n`;
    }

    // Advance Warning Signs
    if (plan.advance_warning_signs && plan.advance_warning_signs.length > 0) {
      text += '⚠️  ADVANCE WARNING SIGNS\n';
      text += '─────────────────────────────────────────────────\n';
      plan.advance_warning_signs.forEach((sign, idx) => {
        text += `${idx + 1}. ${sign.sign_code}: ${sign.name}\n`;
        text += `   Position: ${sign.position}\n`;
        text += `   Placement: ${sign.placement}\n`;
        text += `   Quantity: ${sign.quantity}\n`;
        text += `   Mounting Height: ${sign.mounting_height || 'N/A'}\n\n`;
      });
    }

    // Side Street Signs
    if (plan.side_street_signs && plan.side_street_signs.length > 0) {
      text += '🔄 SIDE STREET SIGNS (DOUBLE GATING)\n';
      text += '─────────────────────────────────────────────────\n';
      plan.side_street_signs.forEach((sideStreet, idx) => {
        text += `${idx + 1}. ${sideStreet.side_street_name || sideStreet.intersection_name}\n`;
        text += `   ${sideStreet.requirement}\n`;
        if (sideStreet.signs) {
          sideStreet.signs.forEach(sign => {
            text += `   - ${sign.sign_code}: ${sign.name}\n`;
            text += `     Placement: ${sign.placement}\n`;
          });
        }
        text += '\n';
      });
    }

    // Bilateral Requirements
    if (plan.bilateral_requirements) {
      text += '↔️  BILATERAL SIGNAGE REQUIREMENTS\n';
      text += '─────────────────────────────────────────────────\n';
      text += `Applies to: ${plan.bilateral_requirements.applies_to}\n`;
      text += `Standard: ${plan.bilateral_requirements.standard}\n`;
      text += `Note: ${plan.bilateral_requirements.compliance_note}\n\n`;
    }

    downloadText(text, `signage_plan_${formData.plan_name || 'plan'}.txt`);
    toast.success('Signage plan exported');
  };

  const exportPedestrianControlsText = () => {
    if (!comprehensiveData.pedestrian_control_measures) {
      toast.error('No pedestrian control data to export');
      return;
    }

    const ped = comprehensiveData.pedestrian_control_measures;
    let text = '═══════════════════════════════════════════════════\n';
    text += '   PEDESTRIAN CONTROL MEASURES\n';
    text += '   (DDA Compliant - AS 1742.3)\n';
    text += '═══════════════════════════════════════════════════\n\n';

    // Barriers
    if (ped.barriers_required && ped.barriers_required.length > 0) {
      text += '🚧 BARRIERS REQUIRED\n';
      text += '─────────────────────────────────────────────────\n';
      ped.barriers_required.forEach((barrier, idx) => {
        text += `${idx + 1}. ${barrier.type}\n`;
        text += `   Location: ${barrier.location}\n`;
        text += `   Specification: ${barrier.specification}\n\n`;
      });
    }

    // Pedestrian Detours
    if (ped.pedestrian_detours && ped.pedestrian_detours.length > 0) {
      text += '🔀 PEDESTRIAN DETOUR ROUTES\n';
      text += '─────────────────────────────────────────────────\n';
      ped.pedestrian_detours.forEach((detour, idx) => {
        text += `${idx + 1}. ${detour.type}\n`;
        text += `   ${detour.description}\n`;
        if (detour.requirements) {
          text += '   Requirements:\n';
          detour.requirements.forEach(req => {
            text += `   - ${req}\n`;
          });
        }
        text += '\n';
      });
    }

    // Safety Measures
    if (ped.safety_measures && ped.safety_measures.length > 0) {
      text += '✅ SAFETY REQUIREMENTS\n';
      text += '─────────────────────────────────────────────────\n';
      ped.safety_measures.forEach((measure, idx) => {
        text += `${idx + 1}. ${measure.measure}\n`;
        text += `   Requirement: ${measure.requirement}\n`;
        text += `   Standard: ${measure.standard || measure.specification}\n\n`;
      });
    }

    // DDA Compliance
    if (ped.access_requirements && ped.access_requirements.length > 0) {
      text += '♿ DDA ACCESS REQUIREMENTS\n';
      text += '─────────────────────────────────────────────────\n';
      ped.access_requirements.forEach((access, idx) => {
        text += `${idx + 1}. ${access.facility || access.compliance}\n`;
        if (access.requirement) text += `   ${access.requirement}\n`;
        if (access.requirements) {
          access.requirements.forEach(req => {
            text += `   - ${req}\n`;
          });
        }
        text += '\n';
      });
    }

    downloadText(text, `pedestrian_controls_${formData.plan_name || 'plan'}.txt`);
    toast.success('Pedestrian controls exported');
  };

  const exportPublicFacilitiesCSV = () => {
    if (!comprehensiveData.public_facilities) {
      toast.error('No public facilities data to export');
      return;
    }

    const facilities = comprehensiveData.public_facilities;
    let csv = 'Facility Type,Name,Special Requirements,Peak Times\n';

    if (facilities.schools && facilities.schools.length > 0) {
      facilities.schools.forEach(school => {
        csv += `"School","${school.name}","Notification required","${school.peak_times}"\n`;
      });
    }

    if (facilities.hospitals && facilities.hospitals.length > 0) {
      facilities.hospitals.forEach(hospital => {
        csv += `"Hospital","${hospital.name}","24/7 Emergency access required","N/A"\n`;
      });
    }

    downloadCSV(csv, `public_facilities_${formData.plan_name || 'plan'}.csv`);
    toast.success('Public facilities exported to CSV');
  };

  const exportComprehensiveReport = () => {
    if (!comprehensiveData.signage_plan && !comprehensiveData.pedestrian_control_measures && 
        comprehensiveData.side_streets.length === 0) {
      toast.error('No comprehensive data to export');
      return;
    }

    let report = '═══════════════════════════════════════════════════════════\n';
    report += '        COMPREHENSIVE TMP AUTO-POPULATION REPORT\n';
    report += '═══════════════════════════════════════════════════════════\n\n';
    report += `Plan Name: ${formData.plan_name || 'Untitled Plan'}\n`;
    report += `Generated: ${new Date().toLocaleString()}\n`;
    report += `Location: ${formData.work_details.start_address} to ${formData.work_details.end_address}\n`;
    report += `Work Type: ${formData.work_details.work_type || 'N/A'}\n\n`;

    // Side Streets
    if (comprehensiveData.side_streets.length > 0) {
      report += '\n📍 SIDE STREETS DETECTED\n';
      report += '───────────────────────────────────────────────────────\n';
      comprehensiveData.side_streets.forEach((street, idx) => {
        report += `${idx + 1}. ${street.name} (${street.type})\n`;
      });
    }

    // Signage Plan
    if (comprehensiveData.signage_plan) {
      const plan = comprehensiveData.signage_plan;
      report += '\n\n🚦 SIGNAGE PLAN (AS 1742.3 COMPLIANT)\n';
      report += '───────────────────────────────────────────────────────\n';
      
      if (plan.distances_documented) {
        report += '\nDocumented Distances:\n';
        report += `- Speed Limit: ${plan.distances_documented.speed_limit}\n`;
        report += `- Advance Warning: ${plan.distances_documented.advance_warning_distance}\n`;
        report += `- Taper Length: ${plan.distances_documented.taper_length}\n`;
        report += `- Buffer Zone: ${plan.distances_documented.buffer_zone}\n`;
      }

      if (plan.advance_warning_signs && plan.advance_warning_signs.length > 0) {
        report += '\nAdvance Warning Signs:\n';
        plan.advance_warning_signs.forEach(sign => {
          report += `- ${sign.sign_code}: ${sign.name} at ${sign.position} (${sign.placement})\n`;
        });
      }

      if (plan.bilateral_requirements) {
        report += '\nBilateral Signage: ' + plan.bilateral_requirements.standard + '\n';
      }
    }

    // Pedestrian Controls
    if (comprehensiveData.pedestrian_control_measures) {
      const ped = comprehensiveData.pedestrian_control_measures;
      report += '\n\n🚶 PEDESTRIAN CONTROL MEASURES\n';
      report += '───────────────────────────────────────────────────────\n';
      
      if (ped.barriers_required && ped.barriers_required.length > 0) {
        report += '\nBarriers Required:\n';
        ped.barriers_required.forEach(barrier => {
          report += `- ${barrier.type} at ${barrier.location}\n`;
        });
      }

      if (ped.pedestrian_detours && ped.pedestrian_detours.length > 0) {
        report += '\nPedestrian Detours: ' + ped.pedestrian_detours.length + ' route(s) with DDA compliance\n';
      }
    }

    // Public Facilities
    if (comprehensiveData.public_facilities) {
      const facilities = comprehensiveData.public_facilities;
      report += '\n\n🏫 PUBLIC FACILITIES\n';
      report += '───────────────────────────────────────────────────────\n';
      
      if (facilities.schools && facilities.schools.length > 0) {
        report += `\nSchools: ${facilities.schools.length}\n`;
        facilities.schools.forEach(school => {
          report += `- ${school.name} (Peak: ${school.peak_times})\n`;
        });
      }

      if (facilities.hospitals && facilities.hospitals.length > 0) {
        report += `\nHospitals: ${facilities.hospitals.length}\n`;
        facilities.hospitals.forEach(hospital => {
          report += `- ${hospital.name} (24/7 emergency access required)\n`;
        });
      }
    }

    // Road Authority
    if (comprehensiveData.governing_body_details) {
      const authority = comprehensiveData.governing_body_details;
      report += '\n\n📞 ROAD AUTHORITY CONTACTS\n';
      report += '───────────────────────────────────────────────────────\n';
      report += `Authority: ${authority.authority_name}\n`;
      report += `Phone: ${authority.main_phone}\n`;
      report += `Email: ${authority.email}\n`;
      report += `Emergency: ${authority.emergency_phone}\n`;
    }

    report += '\n\n═══════════════════════════════════════════════════════════\n';
    report += '              END OF COMPREHENSIVE REPORT\n';
    report += '═══════════════════════════════════════════════════════════\n';

    downloadText(report, `comprehensive_report_${formData.plan_name || 'plan'}.txt`);
    toast.success('✅ Comprehensive report exported successfully!');
  };

  const exportAllDataJSON = () => {
    const exportData = {
      plan_name: formData.plan_name,
      generated: new Date().toISOString(),
      work_details: formData.work_details,
      comprehensive_data: comprehensiveData
    };

    downloadJSON(exportData, `comprehensive_data_${formData.plan_name || 'plan'}.json`);
    toast.success('All data exported to JSON');
  };


  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      
      // Include comprehensive data (hidden from form but needed for PDF generation)
      const planDataWithComprehensive = {
        ...formData,
        comprehensive_data: comprehensiveData  // Add all 26 auto-populated datasets
      };
      
      if (planId) {
        await axios.put(`${API}/plans/${planId}`, planDataWithComprehensive, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Plan updated successfully');
      } else {
        const response = await axios.post(`${API}/plans`, planDataWithComprehensive, {
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
    // Try backend generation first if plan is saved, otherwise use client-side
    if (planId) {
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
        return;
      } catch (error) {
        console.error('Backend PDF generation failed, falling back to client-side:', error);
      }
    }
    
    // Client-side PDF generation (if backend fails or no planId)
    toast.info('Generating PDF from current form data...');
    
    try {
      // Use the same TGS generator to create a basic PDF
      const tgsGenerator = new ProfessionalTGSGenerator();
      
      const roadData = {
        workzone_size: formData.road_data?.workzone_size || 0,
        speed_limit: formData.road_data?.speed_limit || 60,
        road_classification: formData.road_data?.road_classification || 'Urban Road',
        lanes: 2,
        governing_body: formData.road_data?.governing_body || 'Local Council'
      };

      const companyInfo = {
        name: formData.company_details?.name || 'Company Name',
        address: formData.company_details?.address || '',
        phone: formData.company_details?.phone || '',
        abn: formData.company_details?.abn || ''
      };

      const pdfBlob = tgsGenerator.generateProfessionalPDF(formData, formData.devices || [], roadData, companyInfo);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${(formData.plan_name || 'TMP').replace(/\s+/g, '_')}_traffic_plan.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('✅ PDF generated successfully (client-side)');
    } catch (error) {
      console.error('Client-side PDF generation failed:', error);
      toast.error('Failed to generate PDF. Please save the plan first.');
    }
  };

  const handleDownloadProfessionalTGS = async () => {
    if (!formData.devices || formData.devices.length === 0) {
      toast.error('Please place devices on the map first using "Auto-Place Devices" button');
      return;
    }

    toast.info('Generating professional TGS drawing with device images...');

    try {
      const tgsGenerator = new ProfessionalTGSGenerator();
      
      // Prepare road data
      const roadData = {
        workzone_size: formData.road_data?.workzone_size || formData.road_occupancy?.workzone_length || 0,
        speed_limit: formData.road_data?.speed_limit || 60,
        road_classification: formData.road_data?.road_classification || 'Urban Road',
        lanes: formData.road_data?.lanes || 2,
        governing_body: formData.road_data?.governing_body || 'Local Council',
        road_name: formData.road_data?.road_name || formData.work_details?.start_address || 'Road'
      };

      // Prepare company info
      const companyInfo = {
        name: formData.company_details?.name || 'Company Name',
        address: formData.company_details?.address || '',
        phone: formData.company_details?.phone || '',
        abn: formData.company_details?.abn || ''
      };

      // Prepare work details
      const workDetails = {
        work_type: formData.work_details?.work_type || 'Construction',
        start_date: formData.work_details?.start_date || new Date().toISOString().split('T')[0],
        end_date: formData.work_details?.end_date || new Date().toISOString().split('T')[0],
        start_address: formData.work_details?.start_address || '',
        end_address: formData.work_details?.end_address || ''
      };

      // Generate professional TGS PDF with device images
      const pdfBlob = tgsGenerator.generateProfessionalPDF(
        {...formData, work_details: workDetails}, 
        formData.devices, 
        roadData, 
        companyInfo
      );
      
      // Download the PDF
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${(formData.plan_name || 'TGS').replace(/\s+/g, '_')}_TGS_Drawing.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`✅ Professional TGS Drawing downloaded with ${formData.devices.length} devices!`);
    } catch (error) {
      console.error('Error generating TGS PDF:', error);
      toast.error(`Failed to generate TGS Drawing: ${error.message}`);
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
              <Button
                variant="outline"
                onClick={handleDownloadPdf}
                className="border-slate-300 text-slate-700 hover:bg-slate-50"
                title={planId ? "Download from server" : "Generate PDF from current form"}
              >
                <Download className="w-4 h-4 mr-2" />
                PDF
              </Button>
              {formData.devices && formData.devices.length > 0 && (
                <Button
                  variant="outline"
                  onClick={handleDownloadProfessionalTGS}
                  className="border-blue-300 text-blue-700 hover:bg-blue-50"
                  title={`Download TGS with ${formData.devices.length} devices`}
                >
                  <FileImage className="w-4 h-4 mr-2" />
                  TGS Drawing
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

            {/* Section 2: Project Overview */}
            <ProjectOverviewSection 
              formData={formData} 
              handleInputChange={handleInputChange} 
            />

            {/* Section 3: Work Details */}
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

            {/* Section 4: Traffic Assessment - HIDDEN (Auto-populated) */}
            {/* Only show if auto-population failed or user explicitly wants to see it */}
            {(!autoPopulationComplete || showAutoPopulatedData) && (
              <TrafficAssessmentSection 
                formData={formData} 
                handleInputChange={handleInputChange} 
              />
            )}

            {/* Section 5: Site Assessment - HIDDEN (Auto-populated) */}
            {/* Only show if auto-population failed or user explicitly wants to see it */}
            {(!autoPopulationComplete || showAutoPopulatedData) && (
              <SiteAssessmentSection 
                formData={formData} 
                handleInputChange={handleInputChange} 
              />
            )}
            
            {/* Review Auto-Populated Data Button */}
            {autoPopulationComplete && !showAutoPopulatedData && (
              <Card className="border-2 border-blue-500 bg-blue-50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-blue-900 mb-1">✅ Auto-Population Complete</h3>
                      <p className="text-sm text-blue-700">
                        {autoPopulationWarnings.length === 0 
                          ? '26 datasets successfully retrieved. Click to review before generating TMP.'
                          : `${autoPopulationWarnings.length} warnings detected. Click to review and add manual inputs if needed.`
                        }
                      </p>
                    </div>
                    <Button
                      onClick={() => setShowAutoPopulatedData(true)}
                      variant="default"
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Review Auto-Populated Data
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

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

            {/* Comprehensive Auto-Population Data Display */}
            {(comprehensiveData.side_streets.length > 0 || 
              comprehensiveData.signage_plan || 
              comprehensiveData.pedestrian_control_measures || 
              comprehensiveData.public_facilities) && (
              <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-blue-900">📊 Comprehensive Auto-Population Data</CardTitle>
                      <CardDescription>Download all auto-generated compliance data</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        onClick={exportComprehensiveReport}
                        variant="default"
                        className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Complete Report
                      </Button>
                      <Button 
                        onClick={exportAllDataJSON}
                        variant="outline"
                        className="flex items-center gap-2"
                      >
                        <FileText className="h-4 w-4" />
                        JSON
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            )}

            {comprehensiveData.side_streets.length > 0 && (
              <Card className="border-l-4 border-l-blue-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-blue-700">📍 Side Streets Detected</CardTitle>
                      <CardDescription>Streets requiring signage within workzone</CardDescription>
                    </div>
                    <Button 
                      onClick={exportSideStreetsCSV}
                      size="sm"
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      CSV
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {comprehensiveData.side_streets.slice(0, 10).map((street, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-blue-50 rounded">
                        <span className="font-medium">{street.name}</span>
                        <span className="text-sm text-gray-600 capitalize">{street.type}</span>
                      </div>
                    ))}
                  </div>
                  {comprehensiveData.side_streets.length > 10 && (
                    <p className="text-xs text-gray-500 mt-2">
                      Showing 10 of {comprehensiveData.side_streets.length} streets. Download CSV for complete list.
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {comprehensiveData.signage_plan && (
              <Card className="border-l-4 border-l-green-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-green-700">🚦 Signage Plan (AS 1742.3 Compliant)</CardTitle>
                      <CardDescription>Bilateral signage & side street requirements</CardDescription>
                    </div>
                    <Button 
                      onClick={exportSignagePlanText}
                      size="sm"
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      TXT
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Distances */}
                  {comprehensiveData.signage_plan.distances_documented && (
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold mb-2">📏 Documented Distances</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><strong>Speed Limit:</strong> {comprehensiveData.signage_plan.distances_documented.speed_limit}</div>
                        <div><strong>Advance Warning:</strong> {comprehensiveData.signage_plan.distances_documented.advance_warning_distance}</div>
                        <div><strong>Taper Length:</strong> {comprehensiveData.signage_plan.distances_documented.taper_length}</div>
                        <div><strong>Buffer Zone:</strong> {comprehensiveData.signage_plan.distances_documented.buffer_zone}</div>
                      </div>
                      <div className="text-xs text-gray-600 mt-2">
                        {comprehensiveData.signage_plan.distances_documented.standard_reference}
                      </div>
                    </div>
                  )}

                  {/* Advance Warning Signs */}
                  {comprehensiveData.signage_plan.advance_warning_signs?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">⚠️ Advance Warning Signs</h4>
                      {comprehensiveData.signage_plan.advance_warning_signs.map((sign, idx) => (
                        <div key={idx} className="bg-yellow-50 p-3 rounded mb-2">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{sign.sign_code}: {sign.name}</div>
                              <div className="text-sm text-gray-600">{sign.position}</div>
                            </div>
                            <span className="bg-green-600 text-white px-2 py-1 rounded text-xs">
                              {sign.placement}
                            </span>
                          </div>
                          <div className="text-xs mt-1 text-gray-500">Qty: {sign.quantity} | Height: {sign.mounting_height}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Side Street Signs (DOUBLE GATING) */}
                  {comprehensiveData.signage_plan.side_street_signs?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">🔄 Side Street Signs (DOUBLE GATING)</h4>
                      {comprehensiveData.signage_plan.side_street_signs.slice(0, 3).map((sideStreet, idx) => (
                        <div key={idx} className="bg-orange-50 p-3 rounded mb-2 border-l-4 border-orange-500">
                          <div className="font-medium">{sideStreet.side_street_name || sideStreet.intersection_name}</div>
                          <div className="text-sm text-orange-700 font-semibold">{sideStreet.requirement}</div>
                          {sideStreet.signs && sideStreet.signs.map((sign, sidx) => (
                            <div key={sidx} className="text-xs mt-1 ml-4">
                              • {sign.sign_code}: {sign.name} - {sign.placement}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Bilateral Requirements */}
                  {comprehensiveData.signage_plan.bilateral_requirements && (
                    <div className="bg-blue-50 p-3 rounded">
                      <h4 className="font-semibold mb-2">↔️ Bilateral Signage Requirements</h4>
                      <div className="text-sm space-y-1">
                        <div><strong>Applies to:</strong> {comprehensiveData.signage_plan.bilateral_requirements.applies_to}</div>
                        <div><strong>Standard:</strong> {comprehensiveData.signage_plan.bilateral_requirements.standard}</div>
                        <div className="text-xs text-gray-600 mt-2">{comprehensiveData.signage_plan.bilateral_requirements.compliance_note}</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {comprehensiveData.pedestrian_control_measures && (
              <Card className="border-l-4 border-l-purple-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-purple-700">🚶 Pedestrian Control Measures</CardTitle>
                      <CardDescription>DDA compliant pedestrian safety requirements</CardDescription>
                    </div>
                    <Button 
                      onClick={exportPedestrianControlsText}
                      size="sm"
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      TXT
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Barriers */}
                  {comprehensiveData.pedestrian_control_measures.barriers_required?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">🚧 Barriers Required</h4>
                      {comprehensiveData.pedestrian_control_measures.barriers_required.map((barrier, idx) => (
                        <div key={idx} className="bg-purple-50 p-3 rounded mb-2">
                          <div className="font-medium">{barrier.type}</div>
                          <div className="text-sm text-gray-600">{barrier.location}</div>
                          <div className="text-xs text-gray-500 mt-1">{barrier.specification}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Pedestrian Detours */}
                  {comprehensiveData.pedestrian_control_measures.pedestrian_detours?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">🔀 Pedestrian Detour Routes</h4>
                      {comprehensiveData.pedestrian_control_measures.pedestrian_detours.map((detour, idx) => (
                        <div key={idx} className="bg-blue-50 p-3 rounded mb-2">
                          <div className="font-medium">{detour.type}</div>
                          <div className="text-sm mt-1">{detour.description}</div>
                          {detour.requirements && (
                            <ul className="text-xs text-gray-600 mt-2 ml-4 space-y-1">
                              {detour.requirements.map((req, ridx) => (
                                <li key={ridx}>• {req}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Safety Measures */}
                  {comprehensiveData.pedestrian_control_measures.safety_measures?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">✅ Safety Requirements</h4>
                      <div className="space-y-2">
                        {comprehensiveData.pedestrian_control_measures.safety_measures.map((measure, idx) => (
                          <div key={idx} className="bg-green-50 p-2 rounded text-sm">
                            <strong>{measure.measure}:</strong> {measure.requirement}
                            <div className="text-xs text-gray-500">{measure.standard || measure.specification}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Access Requirements */}
                  {comprehensiveData.pedestrian_control_measures.access_requirements?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">♿ DDA Access Requirements</h4>
                      {comprehensiveData.pedestrian_control_measures.access_requirements.map((access, idx) => (
                        <div key={idx} className="bg-indigo-50 p-3 rounded mb-2">
                          <div className="font-medium">{access.facility || access.compliance}</div>
                          {access.requirement && <div className="text-sm text-gray-600 mt-1">{access.requirement}</div>}
                          {access.requirements && (
                            <ul className="text-xs text-gray-600 mt-2 ml-4 space-y-1">
                              {access.requirements.map((req, ridx) => (
                                <li key={ridx}>• {req}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {comprehensiveData.public_facilities && (
              <Card className="border-l-4 border-l-red-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-red-700">🏫 Public Facilities Detected</CardTitle>
                      <CardDescription>Facilities requiring special consideration</CardDescription>
                    </div>
                    <Button 
                      onClick={exportPublicFacilitiesCSV}
                      size="sm"
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      CSV
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {comprehensiveData.public_facilities.schools?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-orange-600">Schools Nearby</h4>
                      {comprehensiveData.public_facilities.schools.map((school, idx) => (
                        <div key={idx} className="bg-orange-50 p-2 rounded mt-2">
                          <div className="font-medium">{school.name}</div>
                          <div className="text-sm text-gray-600">Peak times: {school.peak_times}</div>
                          <div className="text-xs text-orange-700">Notification required: Yes</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {comprehensiveData.public_facilities.hospitals?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-red-600">Hospitals Nearby</h4>
                      {comprehensiveData.public_facilities.hospitals.map((hospital, idx) => (
                        <div key={idx} className="bg-red-50 p-2 rounded mt-2">
                          <div className="font-medium">{hospital.name}</div>
                          <div className="text-sm text-red-700">⚠️ Emergency access MUST be maintained 24/7</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {comprehensiveData.public_facilities.special_zones?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-purple-600">Special Zones</h4>
                      {comprehensiveData.public_facilities.special_zones.map((zone, idx) => (
                        <div key={idx} className="bg-purple-50 p-2 rounded mt-2">
                          <div className="font-medium">{zone.type}</div>
                          <div className="text-sm text-gray-600">{zone.restrictions}</div>
                          <div className="text-xs text-purple-700">{zone.additional_signage}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {comprehensiveData.governing_body_details && (
              <Card className="border-l-4 border-l-gray-500">
                <CardHeader>
                  <CardTitle>📞 Road Authority Contacts</CardTitle>
                  <CardDescription>Governing body for approval & notifications</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div><strong>Authority:</strong> {comprehensiveData.governing_body_details.authority_name}</div>
                    <div><strong>Phone:</strong> {comprehensiveData.governing_body_details.main_phone}</div>
                    <div><strong>Email:</strong> {comprehensiveData.governing_body_details.email}</div>
                    <div><strong>Website:</strong> {comprehensiveData.governing_body_details.website}</div>
                    <div><strong>Emergency:</strong> {comprehensiveData.governing_body_details.emergency_phone}</div>
                    <div className="text-xs text-gray-500 pt-2">{comprehensiveData.governing_body_details.office_hours}</div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AUTO-POPULATED DATA SECTION - Hidden by default, shown after review button clicked */}
            {showAutoPopulatedData && (
              <Card className="border-4 border-blue-500 bg-blue-50 mb-6">
                <CardHeader className="bg-blue-100 border-b-2 border-blue-300">
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-blue-900 text-xl">📊 Auto-Populated Data Review</CardTitle>
                      <CardDescription className="text-blue-700 font-medium">
                        26 datasets automatically fetched - Review before generating TMP
                      </CardDescription>
                    </div>
                    <Button
                      onClick={() => setShowAutoPopulatedData(false)}
                      variant="outline"
                      size="sm"
                      className="border-blue-600 text-blue-700 hover:bg-blue-200"
                    >
                      Hide Data
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6 p-6">

            {/* NEW: Enhanced Crash Statistics with Risk Assessment */}
            {comprehensiveData.crash_statistics && (comprehensiveData.crash_statistics.total_crashes > 0 || comprehensiveData.crash_statistics.total_crashes_5yr > 0) && (
              <Card className="border-l-4 border-l-red-600">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-red-700">⚠️ Road Crash Statistics</CardTitle>
                      <CardDescription>
                        SA Government crash data within 1km radius ({comprehensiveData.crash_statistics.years_analyzed || 5} years)
                      </CardDescription>
                    </div>
                    {comprehensiveData.crash_statistics.risk_assessment && (
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                        comprehensiveData.crash_statistics.risk_assessment.risk_level === 'HIGH' ? 'bg-red-600 text-white' :
                        comprehensiveData.crash_statistics.risk_assessment.risk_level === 'MEDIUM' ? 'bg-orange-600 text-white' :
                        comprehensiveData.crash_statistics.risk_assessment.risk_level === 'LOW-MEDIUM' ? 'bg-yellow-600 text-white' :
                        'bg-green-600 text-white'
                      }`}>
                        RISK: {comprehensiveData.crash_statistics.risk_assessment.risk_level}
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Risk Assessment Banner */}
                  {comprehensiveData.crash_statistics.risk_assessment && (
                    <div className={`border-2 p-3 rounded-lg ${
                      comprehensiveData.crash_statistics.risk_assessment.risk_level === 'HIGH' ? 'bg-red-50 border-red-500' :
                      comprehensiveData.crash_statistics.risk_assessment.risk_level === 'MEDIUM' ? 'bg-orange-50 border-orange-500' :
                      comprehensiveData.crash_statistics.risk_assessment.risk_level === 'LOW-MEDIUM' ? 'bg-yellow-50 border-yellow-500' :
                      'bg-green-50 border-green-500'
                    }`}>
                      <div className="font-bold text-sm mb-1">
                        {comprehensiveData.crash_statistics.risk_assessment.risk_description}
                      </div>
                      <div className="text-xs">
                        Annual crash rate: <strong>{comprehensiveData.crash_statistics.risk_assessment.annual_crash_rate}</strong> crashes/year
                      </div>
                      {comprehensiveData.crash_statistics.risk_assessment.fatal_crash_risk === 'YES' && (
                        <div className="text-xs text-red-700 font-bold mt-1">
                          ⚠️ FATAL CRASH HISTORY DETECTED
                        </div>
                      )}
                    </div>
                  )}

                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-red-50 p-3 rounded">
                      <div className="text-2xl font-bold text-red-700">
                        {comprehensiveData.crash_statistics.total_crashes || comprehensiveData.crash_statistics.total_crashes_5yr || 0}
                      </div>
                      <div className="text-xs text-gray-600">Total Crashes</div>
                    </div>
                    <div className="bg-orange-50 p-3 rounded">
                      <div className="text-2xl font-bold text-orange-700">
                        {comprehensiveData.crash_statistics.fatal_crashes || 0}
                      </div>
                      <div className="text-xs text-gray-600">Fatal</div>
                    </div>
                    <div className="bg-yellow-50 p-3 rounded">
                      <div className="text-2xl font-bold text-yellow-700">
                        {comprehensiveData.crash_statistics.serious_injury || comprehensiveData.crash_statistics.serious_injury_crashes || 0}
                      </div>
                      <div className="text-xs text-gray-600">Serious Injury</div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="text-2xl font-bold text-blue-700">
                        {comprehensiveData.crash_statistics.minor_injury || comprehensiveData.crash_statistics.minor_injury_crashes || 0}
                      </div>
                      <div className="text-xs text-gray-600">Minor Injury</div>
                    </div>
                  </div>

                  {/* Crashes by Year */}
                  {comprehensiveData.crash_statistics.crashes_by_year && Object.keys(comprehensiveData.crash_statistics.crashes_by_year).length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">📈 Crashes by Year</h4>
                      <div className="bg-gray-50 p-3 rounded">
                        {Object.entries(comprehensiveData.crash_statistics.crashes_by_year).map(([year, count]) => (
                          <div key={year} className="flex justify-between text-xs mb-1">
                            <span className="text-gray-700">{year}</span>
                            <span className="font-medium">{count} crashes</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recent Crashes */}
                  {comprehensiveData.crash_statistics.recent_crashes && comprehensiveData.crash_statistics.recent_crashes.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Recent Crashes ({comprehensiveData.crash_statistics.recent_crashes.length})</h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {comprehensiveData.crash_statistics.recent_crashes.map((crash, idx) => (
                          <div key={idx} className="bg-red-50 p-2 rounded text-xs border-l-2 border-red-400">
                            <div className="font-medium">{crash.date} - {crash.severity}</div>
                            <div className="text-gray-600">
                              {crash.type && `${crash.type} • `}
                              {crash.distance_km ? `${crash.distance_km}km away` : crash.distance}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Peak Times */}
                  {comprehensiveData.crash_statistics.peak_times && comprehensiveData.crash_statistics.peak_times.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">⏰ Crash Peak Times</h4>
                      <div className="space-y-1">
                        {comprehensiveData.crash_statistics.peak_times.map((period, idx) => (
                          <div key={idx} className="bg-orange-50 p-2 rounded text-xs flex justify-between">
                            <span><strong>{period.period}:</strong> {period.time}</span>
                            <span className="font-bold">{period.percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Common Factors */}
                  {comprehensiveData.crash_statistics.common_factors && comprehensiveData.crash_statistics.common_factors.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">📊 Common Contributing Factors</h4>
                      <ul className="text-xs space-y-1 ml-4">
                        {comprehensiveData.crash_statistics.common_factors.map((factor, idx) => (
                          <li key={idx} className="text-gray-700">• {factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Safety Recommendations */}
                  {comprehensiveData.crash_statistics.risk_assessment?.recommendations && (
                    <div className="bg-yellow-50 border-2 border-yellow-400 p-3 rounded-lg">
                      <div className="text-xs font-semibold text-yellow-900 mb-2">⚠️ TMP Safety Recommendations</div>
                      <ul className="text-xs space-y-1">
                        {comprehensiveData.crash_statistics.risk_assessment.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-gray-700">• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Warning Message */}
                  {comprehensiveData.crash_statistics.warning && (
                    <div className="bg-blue-50 border border-blue-200 p-2 rounded text-xs text-blue-800">
                      ℹ️ {comprehensiveData.crash_statistics.warning}
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.crash_statistics, 'crash_statistics.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Crash Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.crash_statistics.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {comprehensiveData.historical_traffic && (
              <Card className="border-l-4 border-l-indigo-500">
                <CardHeader>
                  <CardTitle className="text-indigo-700">📈 Historical Traffic Data</CardTitle>
                  <CardDescription>5-year traffic volume trends and patterns</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Traffic Growth */}
                  {comprehensiveData.historical_traffic.traffic_growth_rate !== 0 && (
                    <div className="bg-indigo-50 p-4 rounded-lg">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-indigo-700">
                          {comprehensiveData.historical_traffic.traffic_growth_rate > 0 ? '+' : ''}
                          {comprehensiveData.historical_traffic.traffic_growth_rate}%
                        </div>
                        <div className="text-sm text-gray-600">Annual Traffic Growth Rate</div>
                      </div>
                    </div>
                  )}

                  {/* AADT History */}
                  {comprehensiveData.historical_traffic.aadt_history && comprehensiveData.historical_traffic.aadt_history.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">📊 AADT History</h4>
                      <div className="space-y-1">
                        {comprehensiveData.historical_traffic.aadt_history.map((record, idx) => (
                          <div key={idx} className="flex justify-between items-center bg-gray-50 p-2 rounded text-xs">
                            <span className="font-medium">{record.year}</span>
                            <span className="text-gray-700">{record.aadt.toLocaleString()} vehicles/day</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Peak Hour Trends */}
                  {comprehensiveData.historical_traffic.peak_hour_trends && comprehensiveData.historical_traffic.peak_hour_trends.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">⏰ Peak Hour Patterns</h4>
                      <div className="space-y-2">
                        {comprehensiveData.historical_traffic.peak_hour_trends.map((trend, idx) => (
                          <div key={idx} className="bg-blue-50 p-2 rounded text-xs">
                            <div className="font-medium">{trend.period}</div>
                            <div className="text-gray-600">{trend.volume_increase || trend.volume_decrease}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Seasonal Variations */}
                  {comprehensiveData.historical_traffic.seasonal_variations && comprehensiveData.historical_traffic.seasonal_variations.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">📅 Seasonal Variations</h4>
                      <div className="space-y-1">
                        {comprehensiveData.historical_traffic.seasonal_variations.map((season, idx) => (
                          <div key={idx} className="flex justify-between text-xs bg-gray-50 p-2 rounded">
                            <span className="font-medium">{season.season}</span>
                            <span className="text-gray-600">{season.variation}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500 italic">
                    {comprehensiveData.historical_traffic.reliability}
                  </div>
                </CardContent>
              </Card>
            )}

            {comprehensiveData.location_history && (
              <Card className="border-l-4 border-l-green-600">
                <CardHeader>
                  <CardTitle className="text-green-700">🏘️ Location History & Context</CardTitle>
                  <CardDescription>Demographics, land use, and area characteristics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Area Type */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-green-50 p-3 rounded">
                      <div className="text-sm font-semibold text-green-700">Area Type</div>
                      <div className="text-lg font-bold">{comprehensiveData.location_history.area_type}</div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="text-sm font-semibold text-blue-700">Population Density</div>
                      <div className="text-lg font-bold">{comprehensiveData.location_history.population_density}</div>
                    </div>
                  </div>

                  {/* Sensitive Areas */}
                  {(comprehensiveData.location_history.school_zones || 
                    comprehensiveData.location_history.hospital_zones || 
                    comprehensiveData.location_history.noise_sensitive_areas) && (
                    <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                      <div className="font-semibold text-yellow-900 mb-2 text-sm">⚠️ Sensitive Areas Detected</div>
                      <div className="space-y-1 text-xs">
                        {comprehensiveData.location_history.school_zones && (
                          <div className="flex items-center gap-2">
                            <span className="text-orange-600">🏫</span>
                            <span>School Zone - Peak hour restrictions apply</span>
                          </div>
                        )}
                        {comprehensiveData.location_history.hospital_zones && (
                          <div className="flex items-center gap-2">
                            <span className="text-red-600">🏥</span>
                            <span>Hospital Zone - Emergency access critical</span>
                          </div>
                        )}
                        {comprehensiveData.location_history.noise_sensitive_areas && (
                          <div className="flex items-center gap-2">
                            <span className="text-blue-600">🔇</span>
                            <span>Noise Sensitive - Restrictions may apply</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Land Use */}
                  {comprehensiveData.location_history.land_use && comprehensiveData.location_history.land_use.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🏗️ Land Use</h4>
                      <div className="flex flex-wrap gap-2">
                        {comprehensiveData.location_history.land_use.map((use, idx) => (
                          <span key={idx} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs capitalize">
                            {use}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Heritage Status */}
                  {comprehensiveData.location_history.heritage_status && (
                    <div className="bg-purple-50 border border-purple-200 p-3 rounded">
                      <div className="font-semibold text-purple-900 mb-1 text-sm">🏛️ Heritage Area</div>
                      <div className="text-xs text-gray-700">{comprehensiveData.location_history.heritage_status}</div>
                      <div className="text-xs text-purple-700 mt-1">Additional approvals may be required</div>
                    </div>
                  )}

                  {/* Previous Roadworks */}
                  {comprehensiveData.location_history.previous_roadworks && comprehensiveData.location_history.previous_roadworks.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🔧 Previous Roadworks</h4>
                      <div className="space-y-2">
                        {comprehensiveData.location_history.previous_roadworks.map((work, idx) => (
                          <div key={idx} className="bg-gray-50 p-2 rounded text-xs">
                            <div className="flex justify-between">
                              <span className="font-medium">{work.year} - {work.type}</span>
                              <span className="text-gray-600">{work.duration}</span>
                            </div>
                            <div className="text-gray-600 text-xs">{work.impact}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Environmental Factors */}
                  {comprehensiveData.location_history.environmental_factors && comprehensiveData.location_history.environmental_factors.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🌿 Environmental Considerations</h4>
                      <div className="space-y-2">
                        {comprehensiveData.location_history.environmental_factors.map((factor, idx) => (
                          <div key={idx} className="bg-green-50 p-2 rounded text-xs">
                            <div className="font-medium">{factor.factor}</div>
                            <div className="text-gray-600">{factor.consideration}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}





            {comprehensiveData.current_roadworks && (comprehensiveData.current_roadworks.current_roadworks?.length > 0 || comprehensiveData.current_roadworks.planned_roadworks?.length > 0) && (
              <Card className="border-l-4 border-l-amber-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-amber-700">🚧 Current & Planned Roadworks (Traffic SA)</CardTitle>
                      <CardDescription>Existing roadworks within 5km radius</CardDescription>
                    </div>
                    {comprehensiveData.current_roadworks.conflict_detected && (
                      <span className="bg-red-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">
                        ⚠️ CONFLICT
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Conflict Warning */}
                  {comprehensiveData.current_roadworks.conflict_detected && (
                    <div className="bg-red-50 border-2 border-red-500 p-3 rounded-lg">
                      <div className="font-bold text-red-900 mb-1">⚠️ COORDINATION REQUIRED</div>
                      <div className="text-sm text-red-800">{comprehensiveData.current_roadworks.conflict_warning}</div>
                    </div>
                  )}

                  {/* Current Roadworks */}
                  {comprehensiveData.current_roadworks.current_roadworks?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm flex items-center gap-2">
                        <span className="bg-orange-500 text-white px-2 py-1 rounded text-xs">ACTIVE</span>
                        Current Roadworks
                      </h4>
                      <div className="space-y-2">
                        {comprehensiveData.current_roadworks.current_roadworks.map((work, idx) => (
                          <div key={idx} className="bg-orange-50 border border-orange-200 p-3 rounded">
                            <div className="flex justify-between items-start mb-2">
                              <div className="font-medium text-orange-900">{work.location}</div>
                              <span className="text-xs text-gray-600">{work.distance}</span>
                            </div>
                            <div className="text-sm text-gray-700">{work.description}</div>
                            <div className="flex gap-4 mt-2 text-xs text-gray-600">
                              {work.start_date && <div>Start: {work.start_date}</div>}
                              {work.end_date && <div>End: {work.end_date}</div>}
                            </div>
                            {work.impact && (
                              <div className="mt-2 text-xs">
                                <span className="font-semibold">Impact:</span> {work.impact}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Planned Roadworks */}
                  {comprehensiveData.current_roadworks.planned_roadworks?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm flex items-center gap-2">
                        <span className="bg-blue-500 text-white px-2 py-1 rounded text-xs">PLANNED</span>
                        Future Roadworks
                      </h4>
                      <div className="space-y-2">
                        {comprehensiveData.current_roadworks.planned_roadworks.map((work, idx) => (
                          <div key={idx} className="bg-blue-50 border border-blue-200 p-3 rounded">
                            <div className="flex justify-between items-start mb-2">
                              <div className="font-medium text-blue-900">{work.location}</div>
                              <span className="text-xs text-gray-600">{work.distance}</span>
                            </div>
                            <div className="text-sm text-gray-700">{work.description}</div>
                            <div className="flex gap-4 mt-2 text-xs text-gray-600">
                              {work.start_date && <div>Planned: {work.start_date}</div>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Nearby Closures */}
                  {comprehensiveData.current_roadworks.nearby_closures?.length > 0 && (
                    <div className="bg-red-50 border border-red-300 p-3 rounded">
                      <h4 className="font-semibold mb-2 text-sm text-red-900">🚫 Road Closures Nearby</h4>
                      <div className="text-xs text-red-800">
                        {comprehensiveData.current_roadworks.nearby_closures.length} closure(s) detected within 5km.
                        Detour routes may be affected.
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.current_roadworks.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: Traffic Signals Card */}
            {comprehensiveData.traffic_signals && comprehensiveData.traffic_signals.nearby_signals?.length > 0 && (
              <Card className="border-l-4 border-l-purple-500">
                <CardHeader>
                  <CardTitle className="text-purple-700">🚦 Traffic Signals</CardTitle>
                  <CardDescription>Signal coordination requirements</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.traffic_signals.signal_coordination_required && (
                    <div className="bg-purple-50 border-2 border-purple-500 p-3 rounded-lg">
                      <div className="font-bold text-purple-900 mb-1">⚠️ SIGNAL COORDINATION REQUIRED</div>
                      <div className="text-sm text-purple-800">
                        Contact: {comprehensiveData.traffic_signals.signal_timing_contact}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    {comprehensiveData.traffic_signals.nearby_signals.map((signal, idx) => (
                      <div key={idx} className="bg-gray-50 border border-gray-200 p-3 rounded">
                        <div className="flex justify-between items-start">
                          <div className="font-medium">{signal.location}</div>
                          <span className="text-xs text-gray-600">{signal.distance}</span>
                        </div>
                        {signal.crossing !== 'unknown' && (
                          <div className="text-sm text-gray-600 mt-1">Crossing: {signal.crossing}</div>
                        )}
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.traffic_signals, 'traffic_signals.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Signals Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.traffic_signals.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: School Zones Card */}
            {comprehensiveData.school_zones && comprehensiveData.school_zones.school_zones?.length > 0 && (
              <Card className="border-l-4 border-l-yellow-500">
                <CardHeader>
                  <CardTitle className="text-yellow-700">🏫 School Zones</CardTitle>
                  <CardDescription>Enhanced restrictions and school hours</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.school_zones.enhanced_restrictions && (
                    <div className="bg-yellow-50 border-2 border-yellow-500 p-3 rounded-lg">
                      <div className="font-bold text-yellow-900 mb-1">⚠️ SCHOOL ZONE - ENHANCED RESTRICTIONS</div>
                      <div className="text-sm text-yellow-800">
                        40 km/h speed limit applies during school times
                      </div>
                    </div>
                  )}

                  <div>
                    <h4 className="font-semibold mb-2 text-sm">Nearby Schools</h4>
                    <div className="space-y-2">
                      {comprehensiveData.school_zones.school_zones.map((school, idx) => (
                        <div key={idx} className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                          <div className="flex justify-between items-start">
                            <div className="font-medium">{school.name}</div>
                            <span className="text-xs text-gray-600">{school.distance}</span>
                          </div>
                          <div className="text-sm text-gray-600 capitalize">{school.type}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {comprehensiveData.school_zones.school_times?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">School Hours Restrictions</h4>
                      <div className="space-y-2">
                        {comprehensiveData.school_zones.school_times.map((time, idx) => (
                          <div key={idx} className="bg-white border border-gray-200 p-2 rounded text-sm">
                            <div className="font-semibold">{time.period}</div>
                            <div className="text-gray-600">{time.time}</div>
                            <div className="text-xs text-gray-500 mt-1">{time.restrictions}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.school_zones, 'school_zones.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download School Zones Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.school_zones.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: Parking Restrictions Card */}
            {comprehensiveData.parking_restrictions && (comprehensiveData.parking_restrictions.restrictions?.length > 0 || comprehensiveData.parking_restrictions.permit_required) && (
              <Card className="border-l-4 border-l-indigo-500">
                <CardHeader>
                  <CardTitle className="text-indigo-700">🅿️ Parking Restrictions</CardTitle>
                  <CardDescription>Parking, loading zones, and permits</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.parking_restrictions.permit_required && (
                    <div className="bg-indigo-50 border border-indigo-300 p-3 rounded">
                      <div className="font-semibold mb-1">Permit Required</div>
                      <div className="text-sm text-gray-700">
                        Authority: {comprehensiveData.parking_restrictions.permit_authority}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.parking_restrictions.restrictions?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Parking Regulations</h4>
                      <div className="space-y-2">
                        {comprehensiveData.parking_restrictions.restrictions.slice(0, 5).map((restriction, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 p-2 rounded text-sm">
                            <div className="font-medium capitalize">{restriction.type}</div>
                            <div className="text-gray-600 text-xs">{restriction.restriction || restriction.access}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.parking_restrictions, 'parking_restrictions.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Parking Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.parking_restrictions.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: Public Transport Detailed Card */}
            {comprehensiveData.public_transport_detailed && (
              (comprehensiveData.public_transport_detailed.bus_stops?.length > 0 || 
               comprehensiveData.public_transport_detailed.tram_stops?.length > 0 || 
               comprehensiveData.public_transport_detailed.train_stations?.length > 0)) && (
              <Card className="border-l-4 border-l-cyan-500">
                <CardHeader>
                  <CardTitle className="text-cyan-700">🚌 Public Transport Facilities</CardTitle>
                  <CardDescription>Bus, tram, and train services</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.public_transport_detailed.access_impact !== 'none' && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.public_transport_detailed.access_impact === 'high' 
                        ? 'bg-red-50 border-red-300' 
                        : 'bg-yellow-50 border-yellow-300'
                    }`}>
                      <div className="font-semibold mb-1">
                        {comprehensiveData.public_transport_detailed.access_impact === 'high' ? '⚠️ HIGH' : '⚡'} Impact Level
                      </div>
                      <div className="text-sm text-gray-700">
                        {comprehensiveData.public_transport_detailed.access_requirements}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.public_transport_detailed.bus_stops?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🚌 Bus Stops ({comprehensiveData.public_transport_detailed.bus_stops.length})</h4>
                      <div className="space-y-1">
                        {comprehensiveData.public_transport_detailed.bus_stops.slice(0, 3).map((stop, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 p-2 rounded text-sm flex justify-between">
                            <span>{stop.name}</span>
                            <span className="text-gray-600">{stop.distance}</span>
                          </div>
                        ))}
                        {comprehensiveData.public_transport_detailed.bus_stops.length > 3 && (
                          <div className="text-xs text-gray-500 pl-2">
                            +{comprehensiveData.public_transport_detailed.bus_stops.length - 3} more stops
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.public_transport_detailed.tram_stops?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🚊 Tram Stops ({comprehensiveData.public_transport_detailed.tram_stops.length})</h4>
                      <div className="space-y-1">
                        {comprehensiveData.public_transport_detailed.tram_stops.map((stop, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 p-2 rounded text-sm flex justify-between">
                            <span>{stop.name}</span>
                            <span className="text-gray-600">{stop.distance}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.public_transport_detailed.train_stations?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🚆 Train Stations ({comprehensiveData.public_transport_detailed.train_stations.length})</h4>
                      <div className="space-y-1">
                        {comprehensiveData.public_transport_detailed.train_stations.map((stop, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 p-2 rounded text-sm flex justify-between">
                            <span>{stop.name}</span>
                            <span className="text-gray-600">{stop.distance}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.public_transport_detailed, 'public_transport.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Transport Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.public_transport_detailed.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: Utility Infrastructure Card */}
            {comprehensiveData.utility_infrastructure && (
              <Card className="border-l-4 border-l-red-500">
                <CardHeader>
                  <CardTitle className="text-red-700">⚡ Utility Infrastructure</CardTitle>
                  <CardDescription>Underground and overhead utilities</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-red-50 border-2 border-red-500 p-3 rounded-lg">
                    <div className="font-bold text-red-900 mb-1">⚠️ DIAL BEFORE YOU DIG - MANDATORY</div>
                    <div className="text-sm text-red-800">
                      Call 1100 at least 3 business days before commencing work
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2 text-sm">Utility Contacts</h4>
                    <div className="space-y-2">
                      {comprehensiveData.utility_infrastructure.utility_contacts?.slice(0, 5).map((contact, idx) => (
                        <div key={idx} className="bg-white border border-gray-200 p-2 rounded">
                          <div className="font-medium text-sm">{contact.utility}</div>
                          <div className="text-xs text-gray-600">📞 {contact.phone}</div>
                          <div className="text-xs text-gray-500">{contact.service}</div>
                          <div className="text-xs text-blue-600 mt-1">Notice: {contact.notice}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {comprehensiveData.utility_infrastructure.overhead_utilities?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm text-orange-700">⚡ Overhead Utilities Detected</h4>
                      <div className="bg-orange-50 border border-orange-300 p-2 rounded text-sm">
                        {comprehensiveData.utility_infrastructure.overhead_utilities.length} overhead utility/utilities detected.
                        Minimum clearance requirements apply.
                      </div>
                    </div>
                  )}

                  {comprehensiveData.utility_infrastructure.underground_utilities?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">🔽 Expected Underground Utilities</h4>
                      <div className="text-xs text-gray-600 space-y-1">
                        {comprehensiveData.utility_infrastructure.underground_utilities.slice(0, 3).map((utility, idx) => (
                          <div key={idx} className="bg-gray-50 p-2 rounded">
                            <span className="font-medium">{utility.type}</span> - {utility.provider}
                            <div className="text-gray-500">Depth: {utility.depth}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.utility_infrastructure, 'utility_infrastructure.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Utilities Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.utility_infrastructure.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: Location Metadata System Card */}
            {comprehensiveData.location_metadata_system && comprehensiveData.location_metadata_system.road_classification_official && (
              <Card className="border-l-4 border-l-blue-600">
                <CardHeader>
                  <CardTitle className="text-blue-700">📍 Location Metadata System (LMS)</CardTitle>
                  <CardDescription>Official SA Government Road Classification</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-blue-50 border border-blue-300 p-3 rounded-lg">
                    <div className="font-bold text-blue-900 mb-2">Official Road Data - DIT/DEW</div>
                    <div className="text-sm space-y-1">
                      <div><span className="font-semibold">Road Name:</span> {comprehensiveData.location_metadata_system.road_name}</div>
                      <div><span className="font-semibold">Official Classification:</span> {comprehensiveData.location_metadata_system.road_classification_official}</div>
                      <div><span className="font-semibold">Functional Hierarchy:</span> {comprehensiveData.location_metadata_system.functional_hierarchy}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white border border-gray-200 p-3 rounded">
                      <div className="text-xs text-gray-600 mb-1">Maintenance Authority</div>
                      <div className="font-semibold text-sm">{comprehensiveData.location_metadata_system.maintenance_authority}</div>
                    </div>
                    <div className="bg-white border border-gray-200 p-3 rounded">
                      <div className="text-xs text-gray-600 mb-1">Speed Limit (Official)</div>
                      <div className="font-semibold text-sm">{comprehensiveData.location_metadata_system.speed_limit_official}</div>
                    </div>
                    <div className="bg-white border border-gray-200 p-3 rounded">
                      <div className="text-xs text-gray-600 mb-1">CRRS Code</div>
                      <div className="font-semibold text-sm">{comprehensiveData.location_metadata_system.crrs_code}</div>
                    </div>
                    <div className="bg-white border border-gray-200 p-3 rounded">
                      <div className="text-xs text-gray-600 mb-1">Road Status</div>
                      <div className="font-semibold text-sm">{comprehensiveData.location_metadata_system.sealed_status}</div>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 p-3 rounded">
                    <div className="text-xs font-semibold mb-2">Austroads Classification</div>
                    <div className="space-y-1 text-sm">
                      <div><span className="text-gray-600">Class Code:</span> {comprehensiveData.location_metadata_system.austroads_class_code}</div>
                      <div><span className="text-gray-600">Category:</span> {comprehensiveData.location_metadata_system.road_category_code}</div>
                    </div>
                  </div>

                  <div className="bg-indigo-50 border border-indigo-200 p-2 rounded text-xs">
                    <div className="font-semibold mb-1">LMS Dataset References:</div>
                    {comprehensiveData.location_metadata_system.dataset_references?.map((ref, idx) => (
                      <div key={idx} className="text-gray-700">• {ref}</div>
                    ))}
                  </div>

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.location_metadata_system, 'location_metadata_system.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download LMS Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.location_metadata_system.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: DIT Infrastructure Assets Card */}
            {comprehensiveData.dit_infrastructure_assets && (
              <Card className="border-l-4 border-l-teal-500">
                <CardHeader>
                  <CardTitle className="text-teal-700">🛣️ DIT Infrastructure Assets</CardTitle>
                  <CardDescription>Road condition and asset management</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.dit_infrastructure_assets.road_condition && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.dit_infrastructure_assets.road_condition === 'Good' 
                        ? 'bg-green-50 border-green-300' 
                        : comprehensiveData.dit_infrastructure_assets.road_condition === 'Fair'
                        ? 'bg-yellow-50 border-yellow-300'
                        : 'bg-orange-50 border-orange-300'
                    }`}>
                      <div className="font-semibold mb-1">Road Condition Assessment</div>
                      <div className="text-sm">
                        Condition: <span className="font-bold">{comprehensiveData.dit_infrastructure_assets.road_condition}</span>
                      </div>
                      {comprehensiveData.dit_infrastructure_assets.pavement_type && (
                        <div className="text-sm">
                          Pavement: {comprehensiveData.dit_infrastructure_assets.pavement_type}
                        </div>
                      )}
                    </div>
                  )}

                  {comprehensiveData.dit_infrastructure_assets.asset_inventory?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Asset Inventory</h4>
                      <div className="space-y-2">
                        {comprehensiveData.dit_infrastructure_assets.asset_inventory.map((asset, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 p-2 rounded">
                            <div className="font-medium text-sm">{asset.asset_type}</div>
                            <div className="text-xs text-gray-600">{asset.details}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.dit_infrastructure_assets.maintenance_schedule && (
                    <div className="bg-teal-50 border border-teal-200 p-3 rounded">
                      <div className="font-semibold mb-2 text-sm">Maintenance Schedule</div>
                      <div className="space-y-1 text-xs">
                        <div><span className="text-gray-600">Frequency:</span> {comprehensiveData.dit_infrastructure_assets.maintenance_schedule.inspection_frequency}</div>
                        <div><span className="text-gray-600">Type:</span> {comprehensiveData.dit_infrastructure_assets.maintenance_schedule.maintenance_type}</div>
                        <div><span className="text-gray-600">Contact:</span> {comprehensiveData.dit_infrastructure_assets.maintenance_schedule.contact}</div>
                        <div><span className="text-gray-600">Phone:</span> {comprehensiveData.dit_infrastructure_assets.maintenance_schedule.phone}</div>
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.dit_infrastructure_assets, 'dit_infrastructure_assets.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download DIT Assets Data
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: {comprehensiveData.dit_infrastructure_assets.data_source}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* NEW: SA Traffic Intelligence Card (Top 40 Roads, Intersections, Travel Speeds) */}
            {comprehensiveData.sa_traffic_intelligence && (
              <Card className="border-l-4 border-l-red-500">
                <CardHeader>
                  <CardTitle className="text-red-700">🚦 SA Traffic Intelligence</CardTitle>
                  <CardDescription>Top 40 Roads, Intersections & Travel Speeds</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Top 40 Road Analysis */}
                  {comprehensiveData.sa_traffic_intelligence.top_40_road_analysis && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.is_top_40_road 
                        ? 'bg-red-50 border-red-300' 
                        : 'bg-gray-50 border-gray-300'
                    }`}>
                      <div className="font-semibold mb-2 text-sm">Top 40 Road Analysis</div>
                      {comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.is_top_40_road ? (
                        <div>
                          <div className="text-xs mb-2">
                            <span className="font-bold text-red-700">⚠️ HIGH TRAFFIC LOCATION</span>
                          </div>
                          <div className="text-xs space-y-1">
                            <div><span className="text-gray-600">Rank:</span> <span className="font-bold">#{comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.rank}</span> busiest in SA</div>
                            <div><span className="text-gray-600">AADT:</span> <span className="font-bold">{comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.traffic_volume?.toLocaleString()}</span></div>
                            <div><span className="text-gray-600">Road:</span> {comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.road_match?.road_name}</div>
                          </div>
                          <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs">
                            {comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.message}
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs text-gray-600">
                          {comprehensiveData.sa_traffic_intelligence.top_40_road_analysis.message}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Top 40 Intersection Analysis */}
                  {comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.is_top_40_intersection 
                        ? 'bg-orange-50 border-orange-300' 
                        : 'bg-gray-50 border-gray-300'
                    }`}>
                      <div className="font-semibold mb-2 text-sm">Top 40 Intersection Analysis</div>
                      {comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.is_top_40_intersection ? (
                        <div>
                          <div className="text-xs mb-2">
                            <span className="font-bold text-orange-700">⚠️ MAJOR INTERSECTION</span>
                          </div>
                          <div className="text-xs space-y-1">
                            <div><span className="text-gray-600">Rank:</span> <span className="font-bold">#{comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.rank}</span> busiest intersection</div>
                            <div><span className="text-gray-600">Location:</span> {comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.intersection_match?.location}</div>
                            <div><span className="text-gray-600">Vehicle Exposure:</span> {comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.vehicle_exposure?.toLocaleString()}</div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs text-gray-600">
                          {comprehensiveData.sa_traffic_intelligence.top_40_intersection_analysis.message}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Overall Traffic Level & Recommendations */}
                  {comprehensiveData.sa_traffic_intelligence.overall_traffic_level && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'VERY HIGH' ? 'bg-red-50 border-red-400' :
                      comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'HIGH' ? 'bg-orange-50 border-orange-400' :
                      comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'MEDIUM-HIGH' ? 'bg-yellow-50 border-yellow-400' :
                      'bg-green-50 border-green-400'
                    }`}>
                      <div className="font-semibold mb-2 text-sm">
                        Overall Traffic Level: <span className={
                          comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'VERY HIGH' ? 'text-red-700' :
                          comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'HIGH' ? 'text-orange-700' :
                          comprehensiveData.sa_traffic_intelligence.overall_traffic_level === 'MEDIUM-HIGH' ? 'text-yellow-700' :
                          'text-green-700'
                        }>{comprehensiveData.sa_traffic_intelligence.overall_traffic_level}</span>
                      </div>
                      {comprehensiveData.sa_traffic_intelligence.recommendations?.length > 0 && (
                        <div className="space-y-1 mt-2">
                          {comprehensiveData.sa_traffic_intelligence.recommendations.map((rec, idx) => (
                            <div key={idx} className="text-xs bg-white border border-gray-200 p-2 rounded">
                              {rec}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Travel Speed Data Summary */}
                  {comprehensiveData.sa_traffic_intelligence.travel_speed_data?.success && (
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded">
                      <div className="font-semibold mb-1 text-sm">Travel Speed Data Available</div>
                      <div className="text-xs text-gray-600">
                        {comprehensiveData.sa_traffic_intelligence.travel_speed_data.total_records} Metropolitan Adelaide speed records retrieved
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.sa_traffic_intelligence, 'sa_traffic_intelligence.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Traffic Intelligence
                  </Button>

                  <div className="text-xs text-gray-500 italic pt-2 border-t">
                    Data source: DIT SA - Top 40 Roads, Intersections & Travel Speeds
                  </div>
                </CardContent>
              </Card>
            )}

                </CardContent>
              </Card>
            )}
            {/* NEW: Dilapidation Report Card */}
            {comprehensiveData.dilapidation_report && (
              <Card className="border-l-4 border-l-purple-500">
                <CardHeader>
                  <CardTitle className="text-purple-700">📋 Dilapidation Report</CardTitle>
                  <CardDescription>Pre/Post-construction road condition assessment</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-purple-50 border border-purple-200 p-3 rounded">
                    <div className="font-semibold mb-2">Report Details</div>
                    <div className="space-y-1 text-sm">
                      <div><span className="text-gray-600">Type:</span> {comprehensiveData.dilapidation_report.report_type}</div>
                      <div><span className="text-gray-600">Location:</span> {comprehensiveData.dilapidation_report.location}</div>
                      <div><span className="text-gray-600">Inspector:</span> {comprehensiveData.dilapidation_report.inspector || 'TBC'}</div>
                    </div>
                  </div>

                  {comprehensiveData.dilapidation_report.defect_categories?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Defect Categories</h4>
                      <div className="space-y-2">
                        {comprehensiveData.dilapidation_report.defect_categories.slice(0, 3).map((category, idx) => (
                          <div key={idx} className="bg-white border border-gray-200 p-2 rounded">
                            <div className="font-medium text-sm">{category.category}</div>
                            <div className="text-xs text-gray-600">
                              {category.types?.length || 0} defect types tracked
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.dilapidation_report, 'dilapidation_report.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Dilapidation Report
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* NEW: Traffic Volumes Card */}
            {comprehensiveData.traffic_volumes && (
              <Card className="border-l-4 border-l-blue-500">
                <CardHeader>
                  <CardTitle className="text-blue-700">🚗 Traffic Volume Analysis</CardTitle>
                  <CardDescription>AADT and construction traffic calculations</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.traffic_volumes.existing_traffic && (
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded">
                      <div className="font-semibold mb-2">Existing Traffic</div>
                      <div className="space-y-1 text-sm">
                        <div><span className="text-gray-600">AADT:</span> <span className="font-bold">{comprehensiveData.traffic_volumes.existing_traffic.aadt?.toLocaleString()}</span> vehicles/day</div>
                        <div><span className="text-gray-600">Peak Hour:</span> {comprehensiveData.traffic_volumes.existing_traffic.peak_hour_volume?.toLocaleString()} vehicles</div>
                        <div><span className="text-gray-600">Commercial:</span> {comprehensiveData.traffic_volumes.existing_traffic.commercial_percentage}%</div>
                      </div>
                    </div>
                  )}

                  {comprehensiveData.traffic_volumes.construction_phase && (
                    <div className="bg-orange-50 border border-orange-200 p-3 rounded">
                      <div className="font-semibold mb-2">Construction Traffic</div>
                      <div className="space-y-1 text-sm">
                        <div><span className="text-gray-600">Daily Vehicles:</span> {comprehensiveData.traffic_volumes.construction_phase.daily_total}</div>
                        <div><span className="text-gray-600">Heavy Vehicles:</span> {comprehensiveData.traffic_volumes.construction_phase.heavy_percentage}%</div>
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.traffic_volumes, 'traffic_volumes.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Traffic Volume Data
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* NEW: Comprehensive Risk Assessment Card */}
            {comprehensiveData.comprehensive_risk_assessment && (
              <Card className="border-l-4 border-l-red-500">
                <CardHeader>
                  <CardTitle className="text-red-700">⚠️ Comprehensive Risk Assessment</CardTitle>
                  <CardDescription>SA DIT Field Guide compliant hazard analysis</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.comprehensive_risk_assessment.overall_risk_level && (
                    <div className={`border p-3 rounded ${
                      comprehensiveData.comprehensive_risk_assessment.overall_risk_level.includes('Extreme')
                        ? 'bg-red-50 border-red-300'
                        : comprehensiveData.comprehensive_risk_assessment.overall_risk_level.includes('High')
                        ? 'bg-orange-50 border-orange-300'
                        : 'bg-yellow-50 border-yellow-300'
                    }`}>
                      <div className="font-semibold mb-1">Overall Risk Level</div>
                      <div className="text-sm">{comprehensiveData.comprehensive_risk_assessment.overall_risk_level}</div>
                    </div>
                  )}

                  {comprehensiveData.comprehensive_risk_assessment.identified_hazards?.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Identified Hazards ({comprehensiveData.comprehensive_risk_assessment.identified_hazards.length})</h4>
                      <div className="space-y-2">
                        {comprehensiveData.comprehensive_risk_assessment.identified_hazards.slice(0, 3).map((hazard, idx) => (
                          <div key={idx} className={`border p-2 rounded ${
                            hazard.risk_rating === 'Extreme' ? 'bg-red-50 border-red-300' :
                            hazard.risk_rating === 'High' ? 'bg-orange-50 border-orange-300' :
                            hazard.risk_rating === 'Medium' ? 'bg-yellow-50 border-yellow-300' :
                            'bg-green-50 border-green-300'
                          }`}>
                            <div className="font-medium text-sm">{hazard.hazard}</div>
                            <div className="text-xs text-gray-600">{hazard.description}</div>
                            <div className="text-xs mt-1">
                              <span className="font-medium">Risk:</span> {hazard.risk_rating} (L:{hazard.likelihood} × C:{hazard.consequence})
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.comprehensive_risk_assessment, 'risk_assessment.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Risk Assessment
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* NEW: DIT TMC Permit Application Card */}
            {comprehensiveData.permit_application && (
              <Card className="border-l-4 border-l-green-500">
                <CardHeader>
                  <CardTitle className="text-green-700">📋 DIT TMC Permit Application</CardTitle>
                  <CardDescription>Traffic Management Centre permit details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {comprehensiveData.permit_application.permit_application && (
                    <div className="bg-green-50 border border-green-200 p-3 rounded">
                      <div className="font-semibold mb-2">Application Details</div>
                      <div className="space-y-1 text-sm">
                        <div><span className="text-gray-600">Application ID:</span> {comprehensiveData.permit_application.permit_application.application_id}</div>
                        <div><span className="text-gray-600">Status:</span> {comprehensiveData.permit_application.permit_application.status}</div>
                      </div>
                    </div>
                  )}

                  {comprehensiveData.permit_application.authority_information && (
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded">
                      <div className="font-semibold mb-2">DIT TMC Contact</div>
                      <div className="space-y-1 text-sm">
                        <div>📞 {comprehensiveData.permit_application.authority_information.traffic_management_centre?.phone}</div>
                        <div>📧 {comprehensiveData.permit_application.authority_information.traffic_management_centre?.email}</div>
                        <div className="text-xs text-gray-600 mt-2">
                          Processing time: {comprehensiveData.permit_application.authority_information.processing_time}
                        </div>
                      </div>
                    </div>
                  )}

                  {comprehensiveData.permit_application.critical_dit_requirements && (
                    <div className="bg-red-50 border-2 border-red-300 p-3 rounded">
                      <div className="font-bold text-red-900 mb-1">⚠️ CRITICAL REQUIREMENTS</div>
                      <div className="text-xs text-red-800 space-y-1">
                        <div>• Continuous traffic flow MUST be maintained</div>
                        <div>• All controllers must be accredited</div>
                        <div>• Roadworks App logging MANDATORY</div>
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.permit_application, 'permit_application.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Permit Application
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* NEW: Field Guide Zones Card */}
            {comprehensiveData.field_guide_zones && (
              <Card className="border-l-4 border-l-indigo-500">
                <CardHeader>
                  <CardTitle className="text-indigo-700">📏 SA DIT Field Guide Zones</CardTitle>
                  <CardDescription>Austroads-compliant zone layout calculations</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-indigo-50 border border-indigo-200 p-3 rounded">
                    <div className="font-semibold mb-2">Zone Layout Summary</div>
                    <div className="space-y-1 text-sm">
                      <div><span className="text-gray-600">Speed Limit:</span> {comprehensiveData.field_guide_zones.speed_limit} km/h</div>
                      <div><span className="text-gray-600">Work Length:</span> {comprehensiveData.field_guide_zones.work_length}m</div>
                      <div><span className="text-gray-600">Total Setup:</span> {comprehensiveData.field_guide_zones.total_setup_length}m</div>
                    </div>
                  </div>

                  {comprehensiveData.field_guide_zones.zones && (
                    <div>
                      <h4 className="font-semibold mb-2 text-sm">Zone Breakdown</h4>
                      <div className="space-y-2">
                        {Object.entries(comprehensiveData.field_guide_zones.zones).slice(0, 5).map(([key, zone], idx) => (
                          <div key={idx} className="bg-white border border-gray-200 p-2 rounded">
                            <div className="font-medium text-sm">{zone.name} ({zone.code})</div>
                            <div className="text-xs text-gray-600">Length: {zone.length}m</div>
                            <div className="text-xs text-gray-500">{zone.description}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {comprehensiveData.field_guide_zones.compliance && (
                    <div className="bg-green-50 border border-green-200 p-2 rounded text-xs">
                      <span className="text-gray-600">Compliance:</span> {comprehensiveData.field_guide_zones.compliance}
                    </div>
                  )}

                  <Button
                    onClick={() => downloadJSON(comprehensiveData.field_guide_zones, 'field_guide_zones.json')}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Zone Data
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* END AUTO-POPULATED DATA SECTION */}

            {/* Final Create TMP Button */}
            {autoPopulationComplete && (
              <Card className="border-4 border-green-500 bg-gradient-to-r from-green-50 to-emerald-50">
                <CardContent className="p-6">
                  <div className="text-center space-y-4">
                    <div className="flex justify-center">
                      <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
                        <FileText className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-green-900 mb-2">
                        Ready to Generate Your Professional TMP
                      </h3>
                      <p className="text-gray-700 mb-1">
                        All data has been auto-populated and is ready for final generation
                      </p>
                      <p className="text-sm text-gray-600">
                        This will create a comprehensive PDF including all professional sections:
                        Dilapidation Reports, Risk Assessment, Permit Application, and Field Guide Zones
                      </p>
                    </div>
                    
                    <div className="flex gap-4 justify-center pt-2">
                      <Button
                        onClick={handleSave}
                        disabled={saving}
                        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-lg px-8 py-6 h-auto"
                      >
                        {saving ? (
                          <>
                            <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                            Generating TMP...
                          </>
                        ) : (
                          <>
                            <FileText className="w-5 h-5 mr-2" />
                            Create Professional TMP
                          </>
                        )}
                      </Button>
                      
                      <Button
                        variant="outline"
                        onClick={() => setShowAutoPopulatedData(!showAutoPopulatedData)}
                        className="text-lg px-6 py-6 h-auto"
                      >
                        <Eye className="w-5 h-5 mr-2" />
                        {showAutoPopulatedData ? 'Hide' : 'Review'} All Data
                      </Button>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg text-sm text-left">
                      <div className="font-semibold mb-2 text-blue-900">📋 Your TMP will include:</div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-blue-800">
                        <div>✓ Company & Project Details</div>
                        <div>✓ Traffic Volume Analysis</div>
                        <div>✓ Road & Site Assessment</div>
                        <div>✓ Comprehensive Risk Assessment</div>
                        <div>✓ Dilapidation Report</div>
                        <div>✓ DIT TMC Permit Application</div>
                        <div>✓ Field Guide Zone Layout</div>
                        <div>✓ Traffic Control Devices</div>
                        <div>✓ Pedestrian Controls</div>
                        <div>✓ Emergency Procedures</div>
                        <div>✓ SA Government Datasets</div>
                        <div>✓ Austroads Compliance</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

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

            {/* Section 7: Implementation Plan */}
            <ImplementationSection 
              formData={formData} 
              handleInputChange={handleInputChange} 
            />

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

            {/* Section 6: Safety Plan */}
            <SafetyPlanSection 
              formData={formData} 
              handleInputChange={handleInputChange} 
            />

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

            {/* Section 9: Monitoring & Inspection */}
            <MonitoringSection 
              formData={formData} 
              handleInputChange={handleInputChange} 
            />

            {/* Section 10: Management Review */}
            <ManagementReviewSection 
              formData={formData} 
              handleInputChange={handleInputChange} 
            />

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

            {/* Visual TGS with Sign Overlays */}
            <VisualTGSViewer 
              planData={formData}
              placedDevices={formData.devices.map(d => ({
                code: d.device_code || d.device_name.split(' ').map(w => w[0]).join(''),
                name: d.device_name,
                latitude: d.position_lat,
                longitude: d.position_lng,
                distance: d.properties?.distance || 0,
                side: d.properties?.side || 'left'
              }))}
            />

          </div>
        </div>
      </div>
    </div>
  );
}
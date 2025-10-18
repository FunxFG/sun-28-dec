import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { MapPin, Briefcase, Activity, FileText, Shield, CheckSquare, Eye, Settings } from 'lucide-react';

/**
 * Additional TMP Form Sections
 * Sections 2, 4, 5, 6, 7, 9, 10 from TMP Template
 */

export const ProjectOverviewSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <MapPin className="w-5 h-5 text-blue-600" />
        Project Overview
      </CardTitle>
      <CardDescription>Location description, purpose, and special requirements (Section 2)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <Label>Location Description</Label>
        <Textarea
          value={formData.project_overview.location_description}
          onChange={(e) => handleInputChange('project_overview', 'location_description', e.target.value)}
          placeholder="Detailed description of project location and surroundings"
          rows={2}
        />
      </div>
      <div>
        <Label>Project Purpose</Label>
        <Textarea
          value={formData.project_overview.project_purpose}
          onChange={(e) => handleInputChange('project_overview', 'project_purpose', e.target.value)}
          placeholder="Purpose and objectives of this traffic management plan"
          rows={2}
        />
      </div>
      <div>
        <Label>Site Constraints</Label>
        <Textarea
          value={formData.project_overview.site_constraints}
          onChange={(e) => handleInputChange('project_overview', 'site_constraints', e.target.value)}
          placeholder="Physical, temporal, or operational constraints"
          rows={2}
        />
      </div>
      <div>
        <Label>Special Requirements</Label>
        <Input
          value={formData.project_overview.special_requirements}
          onChange={(e) => handleInputChange('project_overview', 'special_requirements', e.target.value)}
          placeholder="Any special considerations or requirements"
        />
      </div>
      <div>
        <Label>Coordinated By</Label>
        <Input
          value={formData.project_overview.coordinated_by}
          onChange={(e) => handleInputChange('project_overview', 'coordinated_by', e.target.value)}
          placeholder="Agency or authority coordinating this TMP"
        />
      </div>
    </CardContent>
  </Card>
);

export const TrafficAssessmentSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Activity className="w-5 h-5 text-indigo-600" />
        Traffic Assessment
      </CardTitle>
      <CardDescription>Traffic volume data and speed analysis (Section 4.1)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>AADT (Annual Average Daily Traffic)</Label>
          <Input
            type="number"
            value={formData.traffic_assessment.aadt}
            onChange={(e) => handleInputChange('traffic_assessment', 'aadt', e.target.value)}
            placeholder="e.g., 25000"
          />
        </div>
        <div>
          <Label>Peak Hour Volume</Label>
          <Input
            type="number"
            value={formData.traffic_assessment.peak_hour_volume}
            onChange={(e) => handleInputChange('traffic_assessment', 'peak_hour_volume', e.target.value)}
            placeholder="e.g., 2500 vehicles/hour"
          />
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>85th Percentile Speed</Label>
          <Input
            value={formData.traffic_assessment['85th_percentile_speed']}
            onChange={(e) => handleInputChange('traffic_assessment', '85th_percentile_speed', e.target.value)}
            placeholder="e.g., 65 km/h"
          />
        </div>
        <div>
          <Label>Heavy Vehicle Percentage</Label>
          <Input
            value={formData.traffic_assessment.heavy_vehicle_percentage}
            onChange={(e) => handleInputChange('traffic_assessment', 'heavy_vehicle_percentage', e.target.value)}
            placeholder="e.g., 12%"
          />
        </div>
      </div>
      <div>
        <Label>Crash History (Last 5 Years)</Label>
        <Textarea
          value={formData.traffic_assessment.crash_history}
          onChange={(e) => handleInputChange('traffic_assessment', 'crash_history', e.target.value)}
          placeholder="Summary of crash history at this location"
          rows={2}
        />
      </div>
      <div>
        <Label>Assessment Method</Label>
        <Input
          value={formData.traffic_assessment.assessment_method}
          onChange={(e) => handleInputChange('traffic_assessment', 'assessment_method', e.target.value)}
          placeholder="e.g., Traffic counter, Observation, Historical data"
        />
      </div>
    </CardContent>
  </Card>
);

export const SiteAssessmentSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Eye className="w-5 h-5 text-cyan-600" />
        Site Assessment
      </CardTitle>
      <CardDescription>Physical site characteristics and facilities (Section 5)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <Label>Road Geometry</Label>
        <Textarea
          value={formData.site_assessment.road_geometry}
          onChange={(e) => handleInputChange('site_assessment', 'road_geometry', e.target.value)}
          placeholder="Number of lanes, width, curves, gradients, intersections"
          rows={2}
        />
      </div>
      <div>
        <Label>Sight Distances</Label>
        <Input
          value={formData.site_assessment.sight_distances}
          onChange={(e) => handleInputChange('site_assessment', 'sight_distances', e.target.value)}
          placeholder="Available sight distances in both directions"
        />
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>Parking Restrictions</Label>
          <Input
            value={formData.site_assessment.parking_restrictions}
            onChange={(e) => handleInputChange('site_assessment', 'parking_restrictions', e.target.value)}
            placeholder="Existing parking controls"
          />
        </div>
        <div>
          <Label>Public Transport</Label>
          <Input
            value={formData.site_assessment.public_transport}
            onChange={(e) => handleInputChange('site_assessment', 'public_transport', e.target.value)}
            placeholder="Bus routes, stops, tram lines"
          />
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>Pedestrian Facilities</Label>
          <Input
            value={formData.site_assessment.pedestrian_facilities}
            onChange={(e) => handleInputChange('site_assessment', 'pedestrian_facilities', e.target.value)}
            placeholder="Footpaths, crossings, ramps"
          />
        </div>
        <div>
          <Label>Cyclist Facilities</Label>
          <Input
            value={formData.site_assessment.cyclist_facilities}
            onChange={(e) => handleInputChange('site_assessment', 'cyclist_facilities', e.target.value)}
            placeholder="Bike lanes, paths, parking"
          />
        </div>
      </div>
      <div>
        <Label>Utility Services</Label>
        <Input
          value={formData.site_assessment.utility_services}
          onChange={(e) => handleInputChange('site_assessment', 'utility_services', e.target.value)}
          placeholder="Power, water, gas, telecommunications"
        />
      </div>
      <div>
        <Label>Environmental Factors</Label>
        <Textarea
          value={formData.site_assessment.environmental_factors}
          onChange={(e) => handleInputChange('site_assessment', 'environmental_factors', e.target.value)}
          placeholder="Noise, dust, vegetation, heritage considerations"
          rows={2}
        />
      </div>
    </CardContent>
  </Card>
);

export const SafetyPlanSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Shield className="w-5 h-5 text-red-600" />
        Safety Plan & WHS Management
      </CardTitle>
      <CardDescription>Work Health & Safety roles and responsibilities (Section 6)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>WHS Manager</Label>
          <Input
            value={formData.safety_plan.whs_manager}
            onChange={(e) => handleInputChange('safety_plan', 'whs_manager', e.target.value)}
            placeholder="Name of WHS Manager"
          />
        </div>
        <div>
          <Label>Site Safety Officer</Label>
          <Input
            value={formData.safety_plan.site_safety_officer}
            onChange={(e) => handleInputChange('safety_plan', 'site_safety_officer', e.target.value)}
            placeholder="Name of Site Safety Officer"
          />
        </div>
      </div>
      <div>
        <Label>Safety Responsibilities</Label>
        <Textarea
          value={formData.safety_plan.safety_responsibilities}
          onChange={(e) => handleInputChange('safety_plan', 'safety_responsibilities', e.target.value)}
          placeholder="Define safety responsibilities for key roles"
          rows={3}
        />
      </div>
      <div>
        <Label>Hazard Identification</Label>
        <Textarea
          value={formData.safety_plan.hazard_identification}
          onChange={(e) => handleInputChange('safety_plan', 'hazard_identification', e.target.value)}
          placeholder="Process for identifying and documenting hazards"
          rows={2}
        />
      </div>
      <div>
        <Label>Risk Controls</Label>
        <Textarea
          value={formData.safety_plan.risk_controls}
          onChange={(e) => handleInputChange('safety_plan', 'risk_controls', e.target.value)}
          placeholder="Hierarchy of controls applied to identified risks"
          rows={2}
        />
      </div>
      <div>
        <Label>Emergency Procedures</Label>
        <Textarea
          value={formData.safety_plan.emergency_procedures}
          onChange={(e) => handleInputChange('safety_plan', 'emergency_procedures', e.target.value)}
          placeholder="Emergency response procedures specific to this site"
          rows={2}
        />
      </div>
      <div>
        <Label>Incident Reporting</Label>
        <Input
          value={formData.safety_plan.incident_reporting}
          onChange={(e) => handleInputChange('safety_plan', 'incident_reporting', e.target.value)}
          placeholder="Incident reporting process and contacts"
        />
      </div>
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="safety_induction"
          checked={formData.safety_plan.safety_induction_required}
          onChange={(e) => handleInputChange('safety_plan', 'safety_induction_required', e.target.checked)}
          className="w-4 h-4"
        />
        <Label htmlFor="safety_induction">Site-Specific Safety Induction Required</Label>
      </div>
    </CardContent>
  </Card>
);

export const ImplementationSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Briefcase className="w-5 h-5 text-orange-600" />
        Implementation Plan
      </CardTitle>
      <CardDescription>Installation, staging, and TGS references (Section 7)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <Label>Installation Sequence</Label>
        <Textarea
          value={formData.implementation.installation_sequence}
          onChange={(e) => handleInputChange('implementation', 'installation_sequence', e.target.value)}
          placeholder="Step-by-step sequence for device installation"
          rows={3}
        />
      </div>
      <div>
        <Label>Staging Requirements</Label>
        <Textarea
          value={formData.implementation.staging_requirements}
          onChange={(e) => handleInputChange('implementation', 'staging_requirements', e.target.value)}
          placeholder="Staging areas, phasing, progressive implementation"
          rows={2}
        />
      </div>
      <div>
        <Label>TGS Drawing Numbers</Label>
        <Input
          value={formData.implementation.tgs_drawing_numbers}
          onChange={(e) => handleInputChange('implementation', 'tgs_drawing_numbers', e.target.value)}
          placeholder="e.g., TGS-001, TGS-002"
        />
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>Device Setup Time</Label>
          <Input
            value={formData.implementation.device_setup_time}
            onChange={(e) => handleInputChange('implementation', 'device_setup_time', e.target.value)}
            placeholder="e.g., 30 minutes"
          />
        </div>
        <div>
          <Label>Removal Sequence</Label>
          <Input
            value={formData.implementation.removal_sequence}
            onChange={(e) => handleInputChange('implementation', 'removal_sequence', e.target.value)}
            placeholder="Reverse order, specific procedures"
          />
        </div>
      </div>
      <div>
        <Label>Handover Procedures</Label>
        <Textarea
          value={formData.implementation.handover_procedures}
          onChange={(e) => handleInputChange('implementation', 'handover_procedures', e.target.value)}
          placeholder="Shift handover and completion procedures"
          rows={2}
        />
      </div>
    </CardContent>
  </Card>
);

export const MonitoringSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <CheckSquare className="w-5 h-5 text-green-600" />
        Monitoring & Inspection
      </CardTitle>
      <CardDescription>Daily inspections and audit requirements (Section 9)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <input
          type="checkbox"
          id="daily_inspection"
          checked={formData.monitoring.daily_inspection_required}
          onChange={(e) => handleInputChange('monitoring', 'daily_inspection_required', e.target.checked)}
          className="w-4 h-4"
        />
        <Label htmlFor="daily_inspection">Daily Inspection Required</Label>
      </div>
      <div>
        <Label>Inspection Frequency</Label>
        <Input
          value={formData.monitoring.inspection_frequency}
          onChange={(e) => handleInputChange('monitoring', 'inspection_frequency', e.target.value)}
          placeholder="e.g., Daily at start of shift, After incidents"
        />
      </div>
      <div>
        <Label>Inspection Checklist Items</Label>
        <Textarea
          value={formData.monitoring.inspection_checklist}
          onChange={(e) => handleInputChange('monitoring', 'inspection_checklist', e.target.value)}
          placeholder="List key items to check (devices, visibility, damage, positioning)"
          rows={3}
        />
      </div>
      <div>
        <Label>Defect Rectification Process</Label>
        <Textarea
          value={formData.monitoring.defect_rectification}
          onChange={(e) => handleInputChange('monitoring', 'defect_rectification', e.target.value)}
          placeholder="Process for identifying and rectifying defects"
          rows={2}
        />
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>Audit Schedule</Label>
          <Input
            value={formData.monitoring.audit_schedule}
            onChange={(e) => handleInputChange('monitoring', 'audit_schedule', e.target.value)}
            placeholder="e.g., Weekly, Monthly"
          />
        </div>
        <div>
          <Label>Responsible Person</Label>
          <Input
            value={formData.monitoring.responsible_person}
            onChange={(e) => handleInputChange('monitoring', 'responsible_person', e.target.value)}
            placeholder="Name of person responsible for monitoring"
          />
        </div>
      </div>
    </CardContent>
  </Card>
);

export const ManagementReviewSection = ({ formData, handleInputChange }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Settings className="w-5 h-5 text-purple-600" />
        Management Review
      </CardTitle>
      <CardDescription>Review process and variation procedures (Section 10)</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <Label>Review Frequency</Label>
        <Input
          value={formData.management_review.review_frequency}
          onChange={(e) => handleInputChange('management_review', 'review_frequency', e.target.value)}
          placeholder="e.g., Monthly, At project milestones"
        />
      </div>
      <div>
        <Label>Review Process</Label>
        <Textarea
          value={formData.management_review.review_process}
          onChange={(e) => handleInputChange('management_review', 'review_process', e.target.value)}
          placeholder="Process for reviewing and updating this TMP"
          rows={2}
        />
      </div>
      <div>
        <Label>Variation Procedures</Label>
        <Textarea
          value={formData.management_review.variation_procedures}
          onChange={(e) => handleInputChange('management_review', 'variation_procedures', e.target.value)}
          placeholder="Process for requesting and approving variations to this TMP"
          rows={2}
        />
      </div>
      <div>
        <Label>Approval Authority</Label>
        <Input
          value={formData.management_review.approval_authority}
          onChange={(e) => handleInputChange('management_review', 'approval_authority', e.target.value)}
          placeholder="Person or role authorized to approve variations"
        />
      </div>
      <div>
        <Label>Record Keeping</Label>
        <Textarea
          value={formData.management_review.record_keeping}
          onChange={(e) => handleInputChange('management_review', 'record_keeping', e.target.value)}
          placeholder="Process for maintaining TMP records and documentation"
          rows={2}
        />
      </div>
    </CardContent>
  </Card>
);

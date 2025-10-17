import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { toast } from 'sonner';
import { Building2, User, Phone, Mail, FileText, Calendar, MapPin } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ComprehensiveTMPForm({ formData, setFormData, onNext }) {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    // Company Information Validation
    if (!formData.company_info?.company_name) newErrors.company_name = 'Required';
    if (!formData.company_info?.abn) newErrors.abn = 'Required';
    if (!formData.company_info?.address) newErrors.company_address = 'Required';
    if (!formData.company_info?.phone) newErrors.company_phone = 'Required';
    
    // Liaison Person Validation
    if (!formData.liaison?.name) newErrors.liaison_name = 'Required';
    if (!formData.liaison?.phone) newErrors.liaison_phone = 'Required';
    if (!formData.liaison?.email) newErrors.liaison_email = 'Required';
    
    // TMP Details Validation
    if (!formData.tmp_details?.tmp_number) newErrors.tmp_number = 'Required';
    if (!formData.tmp_details?.work_description) newErrors.work_description = 'Required';
    if (!formData.tmp_details?.start_date) newErrors.start_date = 'Required';
    if (!formData.tmp_details?.end_date) newErrors.end_date = 'Required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      toast.success('TMP details saved. Proceeding to site assessment...');
      onNext && onNext();
    } else {
      toast.error('Please fill in all required fields');
    }
  };

  const updateField = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Company Information Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-orange-600" />
            Traffic Control Company Information
          </CardTitle>
          <CardDescription>
            Details of the company responsible for traffic management
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="company_name">
                Company Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="company_name"
                value={formData.company_info?.company_name || ''}
                onChange={(e) => updateField('company_info', 'company_name', e.target.value)}
                placeholder="ABC Traffic Control Pty Ltd"
                className={errors.company_name ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="abn">
                ABN <span className="text-red-500">*</span>
              </Label>
              <Input
                id="abn"
                value={formData.company_info?.abn || ''}
                onChange={(e) => updateField('company_info', 'abn', e.target.value)}
                placeholder="12 345 678 901"
                className={errors.abn ? 'border-red-500' : ''}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="company_address">
              Company Address <span className="text-red-500">*</span>
            </Label>
            <Input
              id="company_address"
              value={formData.company_info?.address || ''}
              onChange={(e) => updateField('company_info', 'address', e.target.value)}
              placeholder="123 Main Street, Adelaide SA 5000"
              className={errors.company_address ? 'border-red-500' : ''}
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="company_phone">
                Phone Number <span className="text-red-500">*</span>
              </Label>
              <Input
                id="company_phone"
                value={formData.company_info?.phone || ''}
                onChange={(e) => updateField('company_info', 'phone', e.target.value)}
                placeholder="(08) 1234 5678"
                className={errors.company_phone ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="company_email">
                Email Address
              </Label>
              <Input
                id="company_email"
                type="email"
                value={formData.company_info?.email || ''}
                onChange={(e) => updateField('company_info', 'email', e.target.value)}
                placeholder="contact@abc-traffic.com.au"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="accreditation">
              Accreditations / Certifications
            </Label>
            <Input
              id="accreditation"
              value={formData.company_info?.accreditation || ''}
              onChange={(e) => updateField('company_info', 'accreditation', e.target.value)}
              placeholder="e.g., RIICWD503D, Traffic Management Level 3"
            />
          </div>
        </CardContent>
      </Card>

      {/* Liaison Person Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5 text-orange-600" />
            Site Liaison / Contact Person
          </CardTitle>
          <CardDescription>
            Primary contact for this traffic management plan
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="liaison_name">
                Full Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="liaison_name"
                value={formData.liaison?.name || ''}
                onChange={(e) => updateField('liaison', 'name', e.target.value)}
                placeholder="John Smith"
                className={errors.liaison_name ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="liaison_position">
                Position / Title
              </Label>
              <Input
                id="liaison_position"
                value={formData.liaison?.position || ''}
                onChange={(e) => updateField('liaison', 'position', e.target.value)}
                placeholder="Site Supervisor"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="liaison_phone">
                Mobile Phone <span className="text-red-500">*</span>
              </Label>
              <Input
                id="liaison_phone"
                value={formData.liaison?.phone || ''}
                onChange={(e) => updateField('liaison', 'phone', e.target.value)}
                placeholder="0412 345 678"
                className={errors.liaison_phone ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="liaison_email">
                Email Address <span className="text-red-500">*</span>
              </Label>
              <Input
                id="liaison_email"
                type="email"
                value={formData.liaison?.email || ''}
                onChange={(e) => updateField('liaison', 'email', e.target.value)}
                placeholder="john.smith@abc-traffic.com.au"
                className={errors.liaison_email ? 'border-red-500' : ''}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="after_hours_contact">
              After Hours Emergency Contact
            </Label>
            <Input
              id="after_hours_contact"
              value={formData.liaison?.after_hours_contact || ''}
              onChange={(e) => updateField('liaison', 'after_hours_contact', e.target.value)}
              placeholder="0400 000 000"
            />
          </div>
        </CardContent>
      </Card>

      {/* TMP Document Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-orange-600" />
            Traffic Management Plan Details
          </CardTitle>
          <CardDescription>
            Official TMP identification and permit information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tmp_number">
                TMP Document Number <span className="text-red-500">*</span>
              </Label>
              <Input
                id="tmp_number"
                value={formData.tmp_details?.tmp_number || ''}
                onChange={(e) => updateField('tmp_details', 'tmp_number', e.target.value)}
                placeholder="TMP-2025-001"
                className={errors.tmp_number ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="permit_number">
                Road Occupancy Permit Number
              </Label>
              <Input
                id="permit_number"
                value={formData.tmp_details?.permit_number || ''}
                onChange={(e) => updateField('tmp_details', 'permit_number', e.target.value)}
                placeholder="ROP-2025-001"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="work_description">
              Work Description <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="work_description"
              value={formData.tmp_details?.work_description || ''}
              onChange={(e) => updateField('tmp_details', 'work_description', e.target.value)}
              placeholder="Detailed description of works including scope, methods, and expected traffic impacts"
              rows={4}
              className={errors.work_description ? 'border-red-500' : ''}
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">
                Works Start Date <span className="text-red-500">*</span>
              </Label>
              <Input
                id="start_date"
                type="date"
                value={formData.tmp_details?.start_date || ''}
                onChange={(e) => updateField('tmp_details', 'start_date', e.target.value)}
                className={errors.start_date ? 'border-red-500' : ''}
              />
            </div>
            
            <div>
              <Label htmlFor="end_date">
                Works End Date <span className="text-red-500">*</span>
              </Label>
              <Input
                id="end_date"
                type="date"
                value={formData.tmp_details?.end_date || ''}
                onChange={(e) => updateField('tmp_details', 'end_date', e.target.value)}
                className={errors.end_date ? 'border-red-500' : ''}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="work_hours">
              Working Hours
            </Label>
            <Input
              id="work_hours"
              value={formData.tmp_details?.work_hours || ''}
              onChange={(e) => updateField('tmp_details', 'work_hours', e.target.value)}
              placeholder="e.g., Monday-Friday 7:00am - 5:00pm, Night works 8:00pm - 6:00am"
            />
          </div>

          <div>
            <Label htmlFor="governing_authority">
              Governing Road Authority
            </Label>
            <Select 
              value={formData.tmp_details?.governing_authority || ''}
              onValueChange={(value) => updateField('tmp_details', 'governing_authority', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select authority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dtmr">Department for Infrastructure and Transport (DIT)</SelectItem>
                <SelectItem value="adelaide_council">City of Adelaide</SelectItem>
                <SelectItem value="local_council">Local Council</SelectItem>
                <SelectItem value="national_highways">National Highways</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={() => window.history.back()}>
          Back
        </Button>
        <Button type="submit" className="bg-orange-600 hover:bg-orange-700">
          Continue to Site Assessment
        </Button>
      </div>
    </form>
  );
}

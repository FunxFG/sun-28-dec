import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { 
  Plus, 
  MapPin, 
  Calendar, 
  Building, 
  FileText, 
  Download,
  LogOut,
  Edit,
  Trash2,
  Shield
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://traffic-plan-genius.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ user, onLogout }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/plans`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlans(response.data);
    } catch (error) {
      toast.error('Failed to fetch plans');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePlan = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this plan?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/plans/${planId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlans(plans.filter(plan => plan.id !== planId));
      toast.success('Plan deleted successfully');
    } catch (error) {
      toast.error('Failed to delete plan');
    }
  };

  const handleDownloadPdf = async (planId, planName) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/plans/${planId}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${planName.replace(/\s+/g, '_')}_traffic_plan.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const getWorkTypeColor = (workType) => {
    switch (workType?.toLowerCase()) {
      case 'emergency': return 'bg-red-100 text-red-800 border-red-200';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'construction': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
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
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-800 font-serif">
                  SafeRoad<span className="text-orange-600">Works</span>
                </h1>
                <p className="text-sm text-slate-600">Welcome back, {user.company_name}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={() => navigate('/plan')}
                className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-medium"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Plan
              </Button>
              <Button
                variant="outline"
                onClick={onLogout}
                className="border-slate-300 text-slate-700 hover:bg-slate-50"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Plans</p>
                  <p className="text-3xl font-bold text-slate-800">{plans.length}</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-full">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Active Projects</p>
                  <p className="text-3xl font-bold text-slate-800">
                    {plans.filter(p => new Date(p.work_details?.end_date) > new Date()).length}
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-full">
                  <MapPin className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">This Month</p>
                  <p className="text-3xl font-bold text-slate-800">
                    {plans.filter(p => {
                      const created = new Date(p.created_at);
                      const now = new Date();
                      return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear();
                    }).length}
                  </p>
                </div>
                <div className="p-3 bg-orange-50 rounded-full">
                  <Calendar className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Plans List */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-xl text-slate-800">Traffic Management Plans</CardTitle>
            <CardDescription>
              Manage and access your traffic management plans
            </CardDescription>
          </CardHeader>
          <CardContent>
            {plans.length === 0 ? (
              <div className="text-center py-12">
                <div className="p-4 bg-slate-50 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <FileText className="w-8 h-8 text-slate-400" />
                </div>
                <h3 className="text-lg font-medium text-slate-800 mb-2">No plans yet</h3>
                <p className="text-slate-600 mb-6">Create your first traffic management plan to get started.</p>
                <Button
                  onClick={() => navigate('/plan')}
                  className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Plan
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className="border border-slate-200 rounded-lg p-6 hover:bg-slate-50/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-slate-800">
                            {plan.plan_name}
                          </h3>
                          <Badge className={getWorkTypeColor(plan.work_details?.work_type)}>
                            {plan.work_details?.work_type?.toUpperCase()}
                          </Badge>
                        </div>
                        
                        <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600 mb-4">
                          <div className="flex items-center gap-2">
                            <Building className="w-4 h-4" />
                            <span>{plan.company_details?.name || 'No company'}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {plan.work_details?.start_date ? 
                                new Date(plan.work_details.start_date).toLocaleDateString() : 
                                'No date'
                              }
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span className="truncate">
                              {plan.work_details?.start_address || 'No location'}
                            </span>
                          </div>
                          <div>
                            <span className="text-xs text-slate-500">
                              Devices: {plan.devices?.length || 0}
                            </span>
                          </div>
                        </div>
                        
                        {plan.work_details?.description && (
                          <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                            {plan.work_details.description}
                          </p>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadPdf(plan.id, plan.plan_name)}
                          className="text-slate-700 hover:bg-slate-50"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/plan/${plan.id}`)}
                          className="text-slate-700 hover:bg-slate-50"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeletePlan(plan.id)}
                          className="text-red-600 hover:bg-red-50 border-red-200"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
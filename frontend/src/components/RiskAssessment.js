import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Shield,
  Users,
  Building,
  DollarSign,
  TrendingUp,
  FileText
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://traffic-plan-mapper.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

const categoryIcons = {
  people: Users,
  information: FileText,
  property: Building,
  reputation: TrendingUp,
  financial: DollarSign,
  capability: Shield
};

const getRiskColor = (rating) => {
  const colors = {
    'Low': 'bg-green-100 text-green-800 border-green-300',
    'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'High': 'bg-orange-100 text-orange-800 border-orange-300',
    'Critical': 'bg-red-100 text-red-800 border-red-300'
  };
  return colors[rating] || colors['Medium'];
};

export default function RiskAssessment({ planId, onComplete }) {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRisks, setSelectedRisks] = useState({});
  const [customRisks, setCustomRisks] = useState([]);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterRating, setFilterRating] = useState('all');

  useEffect(() => {
    fetchRiskData();
    if (planId) {
      loadExistingAssessment();
    }
  }, [planId]);

  const fetchRiskData = async () => {
    try {
      const response = await fetch(`${API}/risks`);
      const data = await response.json();
      setRiskData(data);
    } catch (error) {
      toast.error('Failed to load risk data');
    } finally {
      setLoading(false);
    }
  };

  const loadExistingAssessment = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/plans/${planId}/risk-assessment`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.risk_assessment && data.risk_assessment.selected_risks) {
          setSelectedRisks(data.risk_assessment.selected_risks);
          setCustomRisks(data.risk_assessment.custom_risks || []);
        }
      }
    } catch (error) {
      console.error('Failed to load existing assessment:', error);
    }
  };

  const handleRiskToggle = (riskId) => {
    setSelectedRisks(prev => ({
      ...prev,
      [riskId]: prev[riskId] ? undefined : {
        applicable: true,
        likelihood: riskData.risks.find(r => r.id === riskId)?.default_likelihood || 'possible',
        consequence: riskData.risks.find(r => r.id === riskId)?.default_consequence || 'moderate',
        additional_controls: '',
        notes: ''
      }
    }));
  };

  const updateRiskAssessment = (riskId, field, value) => {
    setSelectedRisks(prev => ({
      ...prev,
      [riskId]: {
        ...prev[riskId],
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    if (!planId) {
      toast.error('Please save the plan first');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      // Calculate risk matrix summary
      const riskSummary = Object.entries(selectedRisks).reduce((acc, [riskId, assessment]) => {
        if (assessment && assessment.applicable) {
          const score = calculateRiskScore(assessment.likelihood, assessment.consequence);
          acc[score.rating] = (acc[score.rating] || 0) + 1;
        }
        return acc;
      }, {});

      const assessmentData = {
        selected_risks: selectedRisks,
        custom_risks: customRisks,
        summary: riskSummary,
        completed_at: new Date().toISOString()
      };

      const response = await fetch(`${API}/plans/${planId}/risk-assessment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(assessmentData)
      });

      if (!response.ok) throw new Error('Failed to save');

      toast.success('Risk assessment saved successfully');
      if (onComplete) onComplete();
    } catch (error) {
      toast.error('Failed to save risk assessment');
    }
  };

  const calculateRiskScore = (likelihood, consequence) => {
    const likelihoodLevels = { rare: 1, unlikely: 2, possible: 3, likely: 4, almost_certain: 5 };
    const consequenceLevels = { insignificant: 1, negligible: 2, moderate: 3, extensive: 4, significant: 5 };
    
    const l = likelihoodLevels[likelihood] || 3;
    const c = consequenceLevels[consequence] || 3;
    const score = l * c;
    
    let rating = 'Medium';
    if (score <= 4) rating = 'Low';
    else if (score <= 9) rating = 'Medium';
    else if (score <= 16) rating = 'High';
    else rating = 'Critical';
    
    return { score, rating };
  };

  const filteredRisks = riskData?.risks.filter(risk => {
    if (filterCategory !== 'all' && risk.category !== filterCategory) return false;
    if (filterRating !== 'all' && risk.risk_score.rating !== filterRating) return false;
    return true;
  }) || [];

  const selectedCount = Object.values(selectedRisks).filter(r => r?.applicable).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Risk Assessment</h2>
          <p className="text-sm text-slate-600 mt-1">
            Identify and assess risks for this traffic management plan
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-sm">
            <CheckCircle className="w-4 h-4 mr-1" />
            {selectedCount} risks identified
          </Badge>
          <Button onClick={handleSave} className="bg-green-600 hover:bg-green-700">
            Save Assessment
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Label>Filter by Category</Label>
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {Object.entries(riskData?.categories || {}).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label>Filter by Risk Rating</Label>
              <Select value={filterRating} onValueChange={setFilterRating}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Ratings</SelectItem>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                  <SelectItem value="Critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk List */}
      <div className="space-y-3">
        {filteredRisks.map((risk) => {
          const Icon = categoryIcons[risk.category] || AlertTriangle;
          const isSelected = selectedRisks[risk.id]?.applicable;
          
          return (
            <Card key={risk.id} className={`transition-all ${isSelected ? 'border-orange-500 shadow-md' : ''}`}>
              <CardHeader className="pb-3">
                <div className="flex items-start gap-4">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() => handleRiskToggle(risk.id)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon className="w-5 h-5 text-slate-600" />
                        <CardTitle className="text-lg">{risk.title}</CardTitle>
                      </div>
                      <Badge className={getRiskColor(risk.risk_score.rating)}>
                        {risk.risk_score.rating}
                      </Badge>
                    </div>
                    <CardDescription className="text-sm">{risk.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>

              {isSelected && (
                <CardContent className="pt-0 pl-14 space-y-4">
                  {/* Likelihood and Consequence */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label>Likelihood</Label>
                      <Select
                        value={selectedRisks[risk.id]?.likelihood}
                        onValueChange={(value) => updateRiskAssessment(risk.id, 'likelihood', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(riskData?.likelihood_levels || {}).map(([key, level]) => (
                            <SelectItem key={key} value={key}>{level.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Consequence</Label>
                      <Select
                        value={selectedRisks[risk.id]?.consequence}
                        onValueChange={(value) => updateRiskAssessment(risk.id, 'consequence', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(riskData?.consequence_levels || {}).map(([key, level]) => (
                            <SelectItem key={key} value={key}>{level.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Standard Controls */}
                  <div>
                    <Label className="text-sm font-semibold">Standard Controls</Label>
                    <ul className="mt-2 space-y-1">
                      {risk.controls.map((control, idx) => (
                        <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{control}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Additional Controls */}
                  <div>
                    <Label>Additional Controls or Notes</Label>
                    <Textarea
                      value={selectedRisks[risk.id]?.notes || ''}
                      onChange={(e) => updateRiskAssessment(risk.id, 'notes', e.target.value)}
                      placeholder="Add any site-specific controls or notes..."
                      rows={2}
                    />
                  </div>

                  {/* References */}
                  {risk.references && risk.references.length > 0 && (
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Info className="w-3 h-3" />
                      <span>References: {risk.references.join(', ')}</span>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      {filteredRisks.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <AlertTriangle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No risks match the current filters</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

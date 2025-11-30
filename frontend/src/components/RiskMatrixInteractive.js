import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  FileText,
  Download,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Risk Matrix Configuration
const LIKELIHOOD_LEVELS = {
  1: { name: 'Rare', color: '#4CAF50' },
  2: { name: 'Unlikely', color: '#8BC34A' },
  3: { name: 'Possible', color: '#FFC107' },
  4: { name: 'Likely', color: '#FF9800' },
  5: { name: 'Almost Certain', color: '#F44336' }
};

const CONSEQUENCE_LEVELS = {
  1: { name: 'Insignificant', color: '#4CAF50' },
  2: { name: 'Negligible', color: '#8BC34A' },
  3: { name: 'Moderate', color: '#FFC107' },
  4: { name: 'Extensive', color: '#FF9800' },
  5: { name: 'Significant', color: '#F44336' }
};

// Risk rating calculation
const getRiskRating = (likelihood, consequence) => {
  const score = likelihood * consequence;
  if (score <= 4) return { level: 'Low', color: '#4CAF50' };
  if (score <= 9) return { level: 'Medium', color: '#FFC107' };
  if (score <= 16) return { level: 'High', color: '#FF9800' };
  return { level: 'Critical', color: '#F44336' };
};

export default function RiskMatrixInteractive({ formData, setFormData, onNext }) {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRisks, setSelectedRisks] = useState({});
  const [expandedRisk, setExpandedRisk] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterRiskLevel, setFilterRiskLevel] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [view, setView] = useState('list'); // 'list' or 'matrix'

  useEffect(() => {
    fetchRisks();
  }, []);

  const fetchRisks = async () => {
    try {
      // Fetch from backend risk registry
      const response = await fetch(`${API}/risks`);
      const data = await response.json();
      
      // Parse CSV data from backend
      setRisks(data.risks || []);
      
      // Load existing risk assessment from formData
      if (formData.risk_assessment) {
        setSelectedRisks(formData.risk_assessment);
      }
    } catch (error) {
      console.error('Error fetching risks:', error);
      toast.error('Failed to load risk data');
    } finally {
      setLoading(false);
    }
  };

  const toggleRiskSelection = (riskId) => {
    const risk = risks.find(r => r.id === riskId);
    if (!risk) return;

    setSelectedRisks(prev => {
      const newSelected = { ...prev };
      
      if (newSelected[riskId]) {
        // Deselect
        delete newSelected[riskId];
      } else {
        // Select with default values
        newSelected[riskId] = {
          risk_id: riskId,
          site_type: risk.site_type,
          hazard: risk.hazard,
          cause: risk.cause,
          consequence: risk.consequence,
          likelihood: risk.likelihood,
          consequence_level: risk.consequence_level,
          risk_score: risk.risk_score,
          risk_level: risk.risk_level,
          controls: {
            elimination: risk.control_elimination,
            substitution: risk.control_substitution,
            engineering: risk.control_engineering,
            administrative: risk.control_administrative,
            ppe: risk.control_ppe
          },
          residual_likelihood: risk.residual_likelihood,
          residual_consequence_level: risk.residual_consequence_level,
          residual_risk_score: risk.residual_risk_score,
          residual_risk_level: risk.residual_risk_level,
          standards_refs: risk.standards_refs,
          additional_notes: ''
        };
      }
      
      return newSelected;
    });
  };

  const updateRiskNotes = (riskId, notes) => {
    setSelectedRisks(prev => ({
      ...prev,
      [riskId]: {
        ...prev[riskId],
        additional_notes: notes
      }
    }));
  };

  const filteredRisks = risks.filter(risk => {
    if (filterCategory !== 'all' && risk.category !== filterCategory) return false;
    if (filterRiskLevel !== 'all' && risk.risk_level !== filterRiskLevel) return false;
    if (searchTerm && !risk.hazard.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !risk.site_type.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const selectedCount = Object.keys(selectedRisks).length;
  
  const riskSummary = Object.values(selectedRisks).reduce((acc, risk) => {
    acc[risk.risk_level] = (acc[risk.risk_level] || 0) + 1;
    return acc;
  }, {});

  const handleSave = () => {
    // Build summary by risk level for quick profile
    const summary = Object.values(selectedRisks).reduce((acc, risk) => {
      if (!risk || !risk.risk_level) return acc;
      acc[risk.risk_level] = (acc[risk.risk_level] || 0) + 1;
      return acc;
    }, {});

    setFormData(prev => ({
      ...prev,
      risk_assessment: {
        selected_risks: selectedRisks,
        summary,
        completed_at: new Date().toISOString()
      }
    }));
    
    toast.success(`${selectedCount} risks saved to TMP`);
    
    if (onNext) {
      onNext();
    }
  };

  const getRiskColor = (level) => {
    const colors = {
      'Low': 'bg-green-100 text-green-800 border-green-300',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'High': 'bg-orange-100 text-orange-800 border-orange-300',
      'Critical': 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[level] || colors['Medium'];
  };

  const categories = [...new Set(risks.map(r => r.category))];

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-6 h-6 text-orange-600" />
                Risk Assessment & Management
              </CardTitle>
              <CardDescription className="mt-2">
                Select applicable risks for your traffic management plan. Control measures will be automatically populated.
              </CardDescription>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="text-base px-4 py-2">
                <CheckCircle className="w-4 h-4 mr-2" />
                {selectedCount} Risks Selected
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Risk Summary */}
      {selectedCount > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Info className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">Risk Profile:</span>
              </div>
              <div className="flex gap-3">
                {riskSummary.Critical && (
                  <Badge className="bg-red-100 text-red-800">Critical: {riskSummary.Critical}</Badge>
                )}
                {riskSummary.High && (
                  <Badge className="bg-orange-100 text-orange-800">High: {riskSummary.High}</Badge>
                )}
                {riskSummary.Medium && (
                  <Badge className="bg-yellow-100 text-yellow-800">Medium: {riskSummary.Medium}</Badge>
                )}
                {riskSummary.Moderate && (
                  <Badge className="bg-yellow-100 text-yellow-800">Moderate: {riskSummary.Moderate}</Badge>
                )}
                {riskSummary.Low && (
                  <Badge className="bg-green-100 text-green-800">Low: {riskSummary.Low}</Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* View Toggle & Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search risks by hazard or site type..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="w-full md:w-64">
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Risk Level Filter */}
            <div className="w-full md:w-48">
              <Select value={filterRiskLevel} onValueChange={setFilterRiskLevel}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="Critical">Critical</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="Moderate">Moderate</SelectItem>
                  <SelectItem value="Low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2">
              <Button
                variant={view === 'list' ? 'default' : 'outline'}
                onClick={() => setView('list')}
                className={view === 'list' ? 'bg-orange-600' : ''}
              >
                List View
              </Button>
              <Button
                variant={view === 'matrix' ? 'default' : 'outline'}
                onClick={() => setView('matrix')}
                className={view === 'matrix' ? 'bg-orange-600' : ''}
              >
                Matrix View
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Matrix View */}
      {view === 'matrix' && (
        <RiskMatrix 
          risks={filteredRisks}
          selectedRisks={selectedRisks}
          onRiskClick={toggleRiskSelection}
        />
      )}

      {/* List View */}
      {view === 'list' && (
        <div className="space-y-3">
          {filteredRisks.map((risk) => {
            const isSelected = selectedRisks[risk.id];
            const isExpanded = expandedRisk === risk.id;

            return (
              <Card 
                key={risk.id}
                className={`transition-all ${isSelected ? 'border-orange-500 shadow-md' : ''}`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-4">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => toggleRiskSelection(risk.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              {risk.id}
                            </Badge>
                            <Badge className="text-xs bg-slate-100 text-slate-700">
                              {risk.category}
                            </Badge>
                          </div>
                          <h3 className="font-semibold text-lg">{risk.site_type}</h3>
                          <p className="text-sm text-slate-600 mt-1">
                            <strong>Hazard:</strong> {risk.hazard}
                          </p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <Badge className={getRiskColor(risk.risk_level)}>
                            {risk.risk_level} ({risk.risk_score?.rating || risk.risk_score?.score || risk.risk_score})
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpandedRisk(isExpanded ? null : risk.id)}
                          >
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </Button>
                        </div>
                      </div>

                      {/* Expanded Details */}
                      {isExpanded && (
                        <div className="mt-4 space-y-4 border-t pt-4">
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <Label className="text-sm font-semibold text-slate-700">Cause</Label>
                              <p className="text-sm text-slate-600 mt-1">{risk.cause}</p>
                            </div>
                            <div>
                              <Label className="text-sm font-semibold text-slate-700">Consequence</Label>
                              <p className="text-sm text-slate-600 mt-1">{risk.consequence}</p>
                            </div>
                          </div>

                          {/* Pre-Treatment Risk */}
                          <div className="bg-red-50 p-3 rounded-md">
                            <Label className="text-sm font-semibold text-red-900">
                              Pre-Treatment Risk
                            </Label>
                            <div className="flex gap-4 mt-2 text-sm">
                              <span>Likelihood: <strong>{risk.likelihood}</strong></span>
                              <span>Consequence: <strong>{risk.consequence_level}</strong></span>
                              <span>Score: <strong>{risk.risk_score?.score || risk.risk_score}</strong></span>
                            </div>
                          </div>

                          {/* Control Measures (5-Level Hierarchy) */}
                          <div className="space-y-2">
                            <Label className="text-sm font-semibold text-slate-700">
                              Control Measures (Hierarchy of Controls)
                            </Label>
                            
                            {risk.control_elimination && (
                              <div className="bg-green-50 p-3 rounded">
                                <strong className="text-green-900">1. Elimination:</strong>
                                <p className="text-sm mt-1">{risk.control_elimination}</p>
                              </div>
                            )}
                            
                            {risk.control_substitution && (
                              <div className="bg-blue-50 p-3 rounded">
                                <strong className="text-blue-900">2. Substitution:</strong>
                                <p className="text-sm mt-1">{risk.control_substitution}</p>
                              </div>
                            )}
                            
                            {risk.control_engineering && (
                              <div className="bg-purple-50 p-3 rounded">
                                <strong className="text-purple-900">3. Engineering:</strong>
                                <p className="text-sm mt-1">{risk.control_engineering}</p>
                              </div>
                            )}
                            
                            {risk.control_administrative && (
                              <div className="bg-yellow-50 p-3 rounded">
                                <strong className="text-yellow-900">4. Administrative:</strong>
                                <p className="text-sm mt-1">{risk.control_administrative}</p>
                              </div>
                            )}
                            
                            {risk.control_ppe && (
                              <div className="bg-orange-50 p-3 rounded">
                                <strong className="text-orange-900">5. PPE:</strong>
                                <p className="text-sm mt-1">{risk.control_ppe}</p>
                              </div>
                            )}
                          </div>

                          {/* Residual Risk (After Controls) */}
                          <div className="bg-green-50 p-3 rounded-md">
                            <Label className="text-sm font-semibold text-green-900">
                              Residual Risk (After Controls Applied)
                            </Label>
                            <div className="flex gap-4 mt-2 text-sm">
                              <span>Likelihood: <strong>{risk.residual_likelihood}</strong></span>
                              <span>Consequence: <strong>{risk.residual_consequence_level}</strong></span>
                              <span>Score: <strong>{risk.residual_risk_score?.score || risk.residual_risk_score}</strong></span>
                              <Badge className={getRiskColor(risk.residual_risk_level)}>
                                {typeof risk.residual_risk_level === 'object' ? risk.residual_risk_level?.level || 'Unknown' : risk.residual_risk_level}
                              </Badge>
                            </div>
                          </div>

                          {/* Standards References */}
                          {risk.standards_refs && (
                            <div className="bg-slate-50 p-3 rounded">
                              <Label className="text-sm font-semibold text-slate-700">
                                Standards References
                              </Label>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {risk.std_SA_WZTM && (
                                  <Badge variant="outline" className="text-xs">SA WZTM: {risk.std_SA_WZTM}</Badge>
                                )}
                                {risk.std_AGTTM && (
                                  <Badge variant="outline" className="text-xs">AGTTM: {risk.std_AGTTM}</Badge>
                                )}
                                {risk.std_AS1742_3 && (
                                  <Badge variant="outline" className="text-xs">AS 1742.3: {risk.std_AS1742_3}</Badge>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Additional Notes (if selected) */}
                          {isSelected && (
                            <div>
                              <Label htmlFor={`notes-${risk.id}`}>
                                Additional Site-Specific Notes
                              </Label>
                              <Textarea
                                id={`notes-${risk.id}`}
                                value={selectedRisks[risk.id]?.additional_notes || ''}
                                onChange={(e) => updateRiskNotes(risk.id, e.target.value)}
                                placeholder="Add any site-specific considerations or additional control measures..."
                                rows={3}
                                className="mt-2"
                              />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </CardHeader>
              </Card>
            );
          })}

          {filteredRisks.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <AlertTriangle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No risks match your current filters</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between sticky bottom-4 bg-white p-4 rounded-lg shadow-lg border">
        <Button variant="outline" onClick={() => window.history.back()}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button 
            variant="outline"
            onClick={() => {
              const csv = generateRiskCSV(selectedRisks);
              downloadCSV(csv, 'risk-assessment.csv');
            }}
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button 
            onClick={handleSave}
            className="bg-orange-600 hover:bg-orange-700"
            disabled={selectedCount === 0}
          >
            Save & Continue ({selectedCount} Risks)
          </Button>
        </div>
      </div>
    </div>
  );
}

// Risk Matrix Visualization Component
function RiskMatrix({ risks, selectedRisks, onRiskClick }) {
  const matrix = {};
  
  // Organize risks into matrix cells
  risks.forEach(risk => {
    const likelihoodMap = {
      'Rare': 1, 'Unlikely': 2, 'Possible': 3, 'Likely': 4, 'Almost Certain': 5
    };
    const consequenceMap = {
      'Insignificant': 1, 'Negligible': 2, 'Moderate': 3, 'Extensive': 4, 'Significant': 5
    };
    
    const l = likelihoodMap[risk.likelihood] || 3;
    const c = consequenceMap[risk.consequence_level] || 3;
    
    const key = `${l}-${c}`;
    if (!matrix[key]) matrix[key] = [];
    matrix[key].push(risk);
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Matrix (5×5)</CardTitle>
        <CardDescription>
          Click on any cell to see risks in that category
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="border p-2 bg-slate-100 w-24"></th>
                <th className="border p-2 bg-slate-100" colSpan={5}>
                  CONSEQUENCE →
                </th>
              </tr>
              <tr>
                <th className="border p-2 bg-slate-100">
                  <div className="transform -rotate-90 whitespace-nowrap">
                    LIKELIHOOD ↓
                  </div>
                </th>
                <th className="border p-2 bg-green-100 text-xs">Insignificant</th>
                <th className="border p-2 bg-green-100 text-xs">Negligible</th>
                <th className="border p-2 bg-yellow-100 text-xs">Moderate</th>
                <th className="border p-2 bg-orange-100 text-xs">Extensive</th>
                <th className="border p-2 bg-red-100 text-xs">Significant</th>
              </tr>
            </thead>
            <tbody>
              {[5, 4, 3, 2, 1].map(likelihood => (
                <tr key={likelihood}>
                  <td className="border p-2 bg-slate-100 text-xs font-semibold">
                    {LIKELIHOOD_LEVELS[likelihood].name}
                  </td>
                  {[1, 2, 3, 4, 5].map(consequence => {
                    const key = `${likelihood}-${consequence}`;
                    const cellRisks = matrix[key] || [];
                    const rating = getRiskRating(likelihood, consequence);
                    
                    return (
                      <td
                        key={consequence}
                        className="border p-2 text-center cursor-pointer hover:opacity-80 transition-opacity"
                        style={{ backgroundColor: rating.color + '20' }}
                        title={`${cellRisks.length} risk(s)`}
                      >
                        <div className="text-xs font-semibold">{rating.level}</div>
                        <div className="text-lg font-bold">{cellRisks.length}</div>
                        {cellRisks.length > 0 && (
                          <div className="text-xs text-slate-600 mt-1">
                            {cellRisks.filter(r => selectedRisks[r.id]).length} selected
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper Functions
function generateRiskCSV(selectedRisks) {
  const headers = [
    'Risk ID', 'Site Type', 'Hazard', 'Cause', 'Consequence',
    'Likelihood', 'Consequence Level', 'Risk Score', 'Risk Level',
    'Control: Elimination', 'Control: Substitution', 'Control: Engineering',
    'Control: Administrative', 'Control: PPE',
    'Residual Likelihood', 'Residual Consequence', 'Residual Score', 'Residual Level',
    'Additional Notes'
  ];
  
  const rows = Object.values(selectedRisks).map(risk => [
    risk.risk_id,
    risk.site_type,
    risk.hazard,
    risk.cause,
    risk.consequence,
    risk.likelihood,
    risk.consequence_level,
    risk.risk_score,
    risk.risk_level,
    risk.controls.elimination,
    risk.controls.substitution,
    risk.controls.engineering,
    risk.controls.administrative,
    risk.controls.ppe,
    risk.residual_likelihood,
    risk.residual_consequence_level,
    risk.residual_risk_score,
    risk.residual_risk_level,
    risk.additional_notes
  ]);
  
  return [headers, ...rows].map(row => 
    row.map(cell => `"${(cell || '').toString().replace(/"/g, '""')}"`).join(',')
  ).join('\n');
}

function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  Info
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Risk level colors
const RISK_COLORS = {
  Low: { bg: 'bg-green-100', border: 'border-green-500', text: 'text-green-800', badge: 'bg-green-500' },
  Medium: { bg: 'bg-yellow-100', border: 'border-yellow-500', text: 'text-yellow-800', badge: 'bg-yellow-500' },
  High: { bg: 'bg-orange-100', border: 'border-orange-500', text: 'text-orange-800', badge: 'bg-orange-500' },
  Extreme: { bg: 'bg-red-100', border: 'border-red-500', text: 'text-red-800', badge: 'bg-red-500' },
};

export default function RiskMatrixInteractive({ formData, setFormData, onNext }) {
  const [risks, setRisks] = useState([]);
  const [risksByCategory, setRisksByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedRisks, setSelectedRisks] = useState({});
  const [expandedRisks, setExpandedRisks] = useState({});
  const [activeCategory, setActiveCategory] = useState('all');
  const [filterRiskLevel, setFilterRiskLevel] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [summary, setSummary] = useState(null);

  const fetchRisks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/risks`);
      const data = await response.json();
      
      console.log('✅ Fetched risks from CSV:', data.total_risks, 'risks');
      console.log('📋 Categories:', Object.keys(data.risks_by_category || {}));
      
      setRisks(data.risks || []);
      setRisksByCategory(data.risks_by_category || {});
      setSummary(data.summary || null);
      
      // Load existing selections from formData
      if (formData?.risk_assessment?.selected_risks) {
        setSelectedRisks(formData.risk_assessment.selected_risks);
      }
      
      toast.success(`Loaded ${data.total_risks} risks from registry`);
    } catch (error) {
      console.error('Error fetching risks:', error);
      toast.error('Failed to load risk registry');
    } finally {
      setLoading(false);
    }
  }, [formData?.risk_assessment?.selected_risks]);

  useEffect(() => {
    fetchRisks();
  }, [fetchRisks]);

  // Save selections to formData whenever they change
  useEffect(() => {
    const selectedCount = Object.keys(selectedRisks).length;
    if (selectedCount > 0 || formData?.risk_assessment?.selected_risks) {
      setFormData(prev => ({
        ...prev,
        risk_assessment: {
          ...prev.risk_assessment,
          selected_risks: selectedRisks,
          total_selected: selectedCount,
          last_updated: new Date().toISOString()
        }
      }));
    }
  }, [selectedRisks, setFormData]);

  const toggleRiskSelection = (risk) => {
    setSelectedRisks(prev => {
      const newSelected = { ...prev };
      
      if (newSelected[risk.id]) {
        delete newSelected[risk.id];
        toast.info(`Removed: ${risk.hazard.substring(0, 40)}...`);
      } else {
        // Select risk with all controls enabled by default
        newSelected[risk.id] = {
          ...risk,
          selected_controls: [...risk.controls], // Select all controls by default
          notes: '',
          custom_controls: []
        };
        toast.success(`Added: ${risk.hazard.substring(0, 40)}...`);
      }
      
      return newSelected;
    });
  };

  const toggleControl = (riskId, control) => {
    setSelectedRisks(prev => {
      if (!prev[riskId]) return prev;
      
      const currentControls = prev[riskId].selected_controls || [];
      const controlIndex = currentControls.indexOf(control);
      
      let newControls;
      if (controlIndex >= 0) {
        newControls = currentControls.filter(c => c !== control);
      } else {
        newControls = [...currentControls, control];
      }
      
      return {
        ...prev,
        [riskId]: {
          ...prev[riskId],
          selected_controls: newControls
        }
      };
    });
  };

  const toggleExpanded = (riskId) => {
    setExpandedRisks(prev => ({
      ...prev,
      [riskId]: !prev[riskId]
    }));
  };

  const getRiskColor = (level) => RISK_COLORS[level] || RISK_COLORS.Medium;

  // Filter risks
  const filteredRisks = risks.filter(risk => {
    // Category filter
    if (activeCategory !== 'all' && risk.category !== activeCategory) return false;
    
    // Risk level filter
    if (filterRiskLevel !== 'all' && risk.risk_rating !== filterRiskLevel) return false;
    
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return (
        risk.hazard?.toLowerCase().includes(search) ||
        risk.category?.toLowerCase().includes(search) ||
        risk.subcategory?.toLowerCase().includes(search) ||
        risk.controls?.some(c => c.toLowerCase().includes(search))
      );
    }
    
    return true;
  });

  const selectedCount = Object.keys(selectedRisks).length;

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Loading risk registry...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with Summary */}
      <Card className="border-2 border-blue-200">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-600" />
            Risk Assessment Registry
          </CardTitle>
          <CardDescription>
            Select applicable risks and controls for your traffic management plan
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Summary Stats */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
              <div className="bg-blue-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-700">{summary.total_risks}</div>
                <div className="text-xs text-blue-600">Total Risks</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-700">{summary.risk_levels?.Low || 0}</div>
                <div className="text-xs text-green-600">Low Risk</div>
              </div>
              <div className="bg-yellow-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-700">{summary.risk_levels?.Medium || 0}</div>
                <div className="text-xs text-yellow-600">Medium Risk</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-orange-700">{summary.risk_levels?.High || 0}</div>
                <div className="text-xs text-orange-600">High Risk</div>
              </div>
              <div className="bg-red-50 p-3 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-700">{summary.risk_levels?.Extreme || 0}</div>
                <div className="text-xs text-red-600">Extreme Risk</div>
              </div>
            </div>
          )}

          {/* Selection Summary */}
          <div className={`p-3 rounded-lg ${selectedCount > 0 ? 'bg-green-100 border border-green-300' : 'bg-gray-100'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className={`w-5 h-5 ${selectedCount > 0 ? 'text-green-600' : 'text-gray-400'}`} />
                <span className="font-medium">
                  {selectedCount} risk{selectedCount !== 1 ? 's' : ''} selected for this plan
                </span>
              </div>
              {selectedCount > 0 && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setSelectedRisks({})}
                >
                  Clear All
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-3 items-center">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search risks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Risk Level Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterRiskLevel}
                onChange={(e) => setFilterRiskLevel(e.target.value)}
                className="border rounded-md px-3 py-2 text-sm"
              >
                <option value="all">All Risk Levels</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Extreme">Extreme</option>
              </select>
            </div>

            {/* Quick Select Buttons */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // Select all high/extreme risks
                  const highRisks = risks.filter(r => r.risk_rating === 'High' || r.risk_rating === 'Extreme');
                  const newSelected = { ...selectedRisks };
                  highRisks.forEach(risk => {
                    if (!newSelected[risk.id]) {
                      newSelected[risk.id] = {
                        ...risk,
                        selected_controls: [...risk.controls],
                        notes: ''
                      };
                    }
                  });
                  setSelectedRisks(newSelected);
                  toast.success(`Added ${highRisks.length} high/extreme risks`);
                }}
              >
                <AlertTriangle className="w-4 h-4 mr-1 text-orange-500" />
                Select High Risks
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Category Tabs */}
      <Tabs value={activeCategory} onValueChange={setActiveCategory}>
        <TabsList className="flex flex-wrap h-auto gap-1 p-1">
          <TabsTrigger value="all" className="text-xs">
            All ({risks.length})
          </TabsTrigger>
          {Object.keys(risksByCategory).map(category => (
            <TabsTrigger key={category} value={category} className="text-xs">
              {category.split(' ')[0]} ({risksByCategory[category]?.length || 0})
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Risk List */}
        <TabsContent value={activeCategory} className="mt-4">
          <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-2">
            {filteredRisks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No risks match your filters</p>
              </div>
            ) : (
              filteredRisks.map(risk => {
                const isSelected = !!selectedRisks[risk.id];
                const isExpanded = expandedRisks[risk.id];
                const colors = getRiskColor(risk.risk_rating);
                
                return (
                  <Card 
                    key={risk.id} 
                    className={`transition-all ${isSelected ? `${colors.border} border-2 ${colors.bg}` : 'border hover:border-gray-300'}`}
                  >
                    <CardContent className="p-3">
                      {/* Risk Header Row */}
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => toggleRiskSelection(risk)}
                          className="mt-1"
                        />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <span className="text-sm font-mono bg-gray-200 px-1.5 py-0.5 rounded">
                              {risk.id}
                            </span>
                            <Badge className={`${colors.badge} text-white text-xs`}>
                              {risk.risk_rating}
                            </Badge>
                            <span className="text-xs text-gray-500">{risk.category}</span>
                          </div>
                          
                          <h4 className="font-medium text-sm">{risk.hazard}</h4>
                          
                          {risk.trigger && (
                            <p className="text-xs text-gray-600 mt-1">
                              <span className="font-medium">Trigger:</span> {risk.trigger}
                            </p>
                          )}
                        </div>
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpanded(risk.id)}
                        >
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </Button>
                      </div>
                      
                      {/* Expanded Details */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t space-y-3">
                          {/* Consequence */}
                          {risk.consequence && (
                            <div>
                              <Label className="text-xs font-medium text-gray-700">Potential Consequence</Label>
                              <p className="text-sm text-gray-600">{risk.consequence}</p>
                            </div>
                          )}
                          
                          {/* Controls */}
                          {risk.controls && risk.controls.length > 0 && (
                            <div>
                              <Label className="text-xs font-medium text-gray-700 mb-2 block">
                                Controls / Mitigation ({risk.controls.length})
                              </Label>
                              <div className="space-y-2">
                                {risk.controls.map((control, idx) => {
                                  const controlSelected = isSelected && 
                                    selectedRisks[risk.id]?.selected_controls?.includes(control);
                                  
                                  return (
                                    <div 
                                      key={idx} 
                                      className={`flex items-start gap-2 p-2 rounded text-sm ${
                                        controlSelected ? 'bg-green-50 border border-green-200' : 'bg-gray-50'
                                      }`}
                                    >
                                      <Checkbox
                                        checked={controlSelected}
                                        onCheckedChange={() => isSelected && toggleControl(risk.id, control)}
                                        disabled={!isSelected}
                                        className="mt-0.5"
                                      />
                                      <span className={!isSelected ? 'text-gray-400' : ''}>{control}</span>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                          
                          {/* Additional Info */}
                          <div className="grid grid-cols-2 gap-3 text-xs">
                            {risk.monitoring && (
                              <div>
                                <span className="font-medium text-gray-700">Monitoring:</span>
                                <p className="text-gray-600">{risk.monitoring}</p>
                              </div>
                            )}
                            {risk.responsible_role && (
                              <div>
                                <span className="font-medium text-gray-700">Responsible:</span>
                                <p className="text-gray-600">{risk.responsible_role}</p>
                              </div>
                            )}
                            {risk.reference && (
                              <div>
                                <span className="font-medium text-gray-700">Reference:</span>
                                <p className="text-gray-600">{risk.reference}</p>
                              </div>
                            )}
                            {risk.residual_risk && (
                              <div>
                                <span className="font-medium text-gray-700">Residual Risk:</span>
                                <Badge className={`${getRiskColor(risk.residual_risk).badge} text-white text-xs ml-1`}>
                                  {risk.residual_risk}
                                </Badge>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Selected Risks Summary */}
      {selectedCount > 0 && (
        <Card className="border-2 border-green-300 bg-green-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Selected Risks Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.values(selectedRisks).map(risk => (
                <div key={risk.id} className="flex items-center justify-between p-2 bg-white rounded border">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs bg-gray-200 px-1 rounded">{risk.id}</span>
                    <span className="text-sm truncate max-w-[300px]">{risk.hazard}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">
                      {risk.selected_controls?.length || 0} controls
                    </span>
                    <Badge className={`${getRiskColor(risk.risk_rating).badge} text-white text-xs`}>
                      {risk.risk_rating}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

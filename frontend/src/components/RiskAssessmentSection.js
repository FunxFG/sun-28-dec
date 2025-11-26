import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Label } from './ui/label';
import { AlertTriangle, Shield, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

const RiskAssessmentSection = ({ formData, handleInputChange, BACKEND_URL }) => {
  const [riskRegistry, setRiskRegistry] = useState([]);
  const [selectedRisks, setSelectedRisks] = useState(formData?.risk_assessment?.selected_risks || []);
  const [expandedRisks, setExpandedRisks] = useState(new Set());
  const [filterCategory, setFilterCategory] = useState('all');
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'matrix'
  
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    const fetchRiskRegistry = async () => {
      try {
        const response = await axios.get(`${API}/risks`);
        // Handle both array response and object with risks property
        const risksData = Array.isArray(response.data) ? response.data : (response.data.risks || []);
        setRiskRegistry(risksData);
      } catch (error) {
        console.error('Error fetching risk registry:', error);
        setRiskRegistry([]); // Set empty array on error
      }
    };

    fetchRiskRegistry();
  }, []);

  const getRiskColor = (score) => {
    if (score >= 17) return 'bg-red-100 border-red-500 text-red-900';
    if (score >= 11) return 'bg-orange-100 border-orange-500 text-orange-900';
    if (score >= 6) return 'bg-yellow-100 border-yellow-500 text-yellow-900';
    return 'bg-green-100 border-green-500 text-green-900';
  };

  const getRiskRating = (score) => {
    if (score >= 17) return 'CRITICAL';
    if (score >= 11) return 'HIGH';
    if (score >= 6) return 'MEDIUM';
    return 'LOW';
  };

  const toggleRiskSelection = (riskId) => {
    const risk = riskRegistry.find(r => r.id === riskId);
    if (!risk) return;

    setSelectedRisks(prev => {
      const isSelected = prev.some(r => r.id === riskId);
      let updated;
      
      if (isSelected) {
        updated = prev.filter(r => r.id !== riskId);
      } else {
        updated = [...prev, {
          id: risk.id,
          title: risk.title,
          category: risk.category,
          likelihood: risk.default_likelihood,
          consequence: risk.default_consequence,
          controls: risk.controls,
          risk_score: risk.risk_score
        }];
      }
      
      // Update formData
      handleInputChange('risk_assessment', 'selected_risks', updated);
      return updated;
    });
  };

  const toggleExpanded = (riskId) => {
    setExpandedRisks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(riskId)) {
        newSet.delete(riskId);
      } else {
        newSet.add(riskId);
      }
      return newSet;
    });
  };

  const filteredRisks = filterCategory === 'all' 
    ? (riskRegistry || [])
    : (riskRegistry || []).filter(r => r.category === filterCategory);

  const categories = {
    'all': 'All Categories',
    'people': 'People',
    'information': 'Information',
    'property': 'Property & Equipment',
    'reputation': 'Reputation',
    'financial': 'Financial',
    'capability': 'Capability'
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          Risk Assessment
        </CardTitle>
        <CardDescription>
          Identify and assess risks according to AS 1742.3 and AGTTM standards
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 p-3 rounded">
            <div className="text-2xl font-bold text-blue-900">{riskRegistry.length}</div>
            <div className="text-xs text-blue-700">Total Risks</div>
          </div>
          <div className="bg-green-50 border border-green-200 p-3 rounded">
            <div className="text-2xl font-bold text-green-900">{selectedRisks.length}</div>
            <div className="text-xs text-green-700">Selected</div>
          </div>
          <div className="bg-orange-50 border border-orange-200 p-3 rounded">
            <div className="text-2xl font-bold text-orange-900">
              {selectedRisks.filter(r => r.risk_score?.score >= 11).length}
            </div>
            <div className="text-xs text-orange-700">High Risk</div>
          </div>
          <div className="bg-red-50 border border-red-200 p-3 rounded">
            <div className="text-2xl font-bold text-red-900">
              {selectedRisks.filter(r => r.risk_score?.score >= 17).length}
            </div>
            <div className="text-xs text-red-700">Critical</div>
          </div>
        </div>

        {/* View Controls */}
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              List View
            </button>
            <button
              onClick={() => setViewMode('matrix')}
              className={`px-4 py-2 rounded ${viewMode === 'matrix' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              Risk Matrix
            </button>
          </div>
          
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-4 py-2 border rounded"
          >
            {Object.entries(categories).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* List View */}
        {viewMode === 'list' && (
          <div className="space-y-3">
            {(filteredRisks || []).map((risk) => {
              const isSelected = selectedRisks.some(r => r.id === risk.id);
              const isExpanded = expandedRisks.has(risk.id);
              const riskScore = risk.risk_score?.score || 0;
              
              return (
                <div
                  key={risk.id}
                  className={`border-2 rounded-lg p-4 ${getRiskColor(riskScore)} ${isSelected ? 'border-blue-500' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleRiskSelection(risk.id)}
                        className="mt-1 w-5 h-5 cursor-pointer"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold">{risk.title}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${getRiskColor(riskScore)}`}>
                            {getRiskRating(riskScore)} ({riskScore})
                          </span>
                          <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                            {categories[risk.category]}
                          </span>
                        </div>
                        <p className="text-sm mt-1">{risk.description}</p>
                        
                        {isExpanded && (
                          <div className="mt-4 space-y-3">
                            {/* Controls */}
                            <div className="bg-white/50 p-3 rounded">
                              <div className="flex items-center gap-2 mb-2">
                                <Shield className="w-4 h-4 text-green-600" />
                                <span className="font-semibold text-sm">Control Measures</span>
                              </div>
                              <ul className="space-y-1 ml-6">
                                {risk.controls.map((control, idx) => (
                                  <li key={idx} className="text-sm flex items-start gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                                    <span>{control}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            
                            {/* References */}
                            <div className="bg-white/50 p-3 rounded">
                              <span className="font-semibold text-sm">Standards References:</span>
                              <div className="text-xs mt-1 space-y-1">
                                {risk.references.map((ref, idx) => (
                                  <div key={idx} className="text-gray-700">• {ref}</div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={() => toggleExpanded(risk.id)}
                      className="ml-2 p-1 hover:bg-white/50 rounded"
                    >
                      {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Matrix View */}
        {viewMode === 'matrix' && (
          <div className="overflow-x-auto">
            <div className="text-sm font-semibold mb-2">Risk Matrix (Likelihood × Consequence)</div>
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="border p-2 bg-gray-100">Likelihood →<br/>Consequence ↓</th>
                  <th className="border p-2 bg-gray-100">Rare (1)</th>
                  <th className="border p-2 bg-gray-100">Unlikely (2)</th>
                  <th className="border p-2 bg-gray-100">Possible (3)</th>
                  <th className="border p-2 bg-gray-100">Likely (4)</th>
                  <th className="border p-2 bg-gray-100">Almost Certain (5)</th>
                </tr>
              </thead>
              <tbody>
                {['significant', 'extensive', 'moderate', 'negligible', 'insignificant'].map((consequence, cidx) => (
                  <tr key={consequence}>
                    <th className="border p-2 bg-gray-100 text-left">
                      {consequence.charAt(0).toUpperCase() + consequence.slice(1)} ({5-cidx})
                    </th>
                    {['rare', 'unlikely', 'possible', 'likely', 'almost_certain'].map((likelihood, lidx) => {
                      const score = (lidx + 1) * (5 - cidx);
                      const risksInCell = selectedRisks.filter(r => 
                        r.likelihood === likelihood && r.consequence === consequence
                      );
                      
                      return (
                        <td
                          key={`${consequence}-${likelihood}`}
                          className={`border p-2 text-center ${getRiskColor(score)}`}
                        >
                          <div className="font-bold">{score}</div>
                          {risksInCell.length > 0 && (
                            <div className="text-xs mt-1">
                              {risksInCell.length} risk{risksInCell.length > 1 ? 's' : ''}
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4 flex gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-100 border border-red-500"></div>
                <span>Critical (17-25)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-orange-100 border border-orange-500"></div>
                <span>High (11-16)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-100 border border-yellow-500"></div>
                <span>Medium (6-10)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-100 border border-green-500"></div>
                <span>Low (1-5)</span>
              </div>
            </div>
          </div>
        )}

        {/* Selected Risks Summary */}
        {selectedRisks.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
            <h4 className="font-bold mb-2">Selected Risks Summary ({selectedRisks.length})</h4>
            <div className="space-y-2">
              {selectedRisks.map((risk) => (
                <div key={risk.id} className="text-sm flex justify-between items-center bg-white p-2 rounded">
                  <span>{risk.title}</span>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${getRiskColor(risk.risk_score?.score || 0)}`}>
                    {getRiskRating(risk.risk_score?.score || 0)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RiskAssessmentSection;

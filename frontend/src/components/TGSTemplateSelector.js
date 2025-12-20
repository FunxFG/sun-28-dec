import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Info } from 'lucide-react';

/**
 * TGS Template Multi-Selector Component
 * Complete implementation of GENERIC TGS PACKAGE 2026 (16 patterns)
 */
export default function TGSTemplateSelector({ selectedTemplates, onChange }) {
  
  const tgsTemplates = [
    // STOP-SLOW PATTERNS (4 patterns)
    { id: 'STOP_SLOW_LOW_TRAFFIC_LANE', name: 'Stop-Slow 40-70km (Traffic Lane)', description: 'Generic 1: Work in lane with TCs', icon: '👷', devices: '10-15', category: 'stop_slow' },
    { id: 'STOP_SLOW_HIGH_TRAFFIC_LANE', name: 'Stop-Slow 80-110km (Traffic Lane)', description: 'Generic 2: High speed TCs', icon: '👷', devices: '12-20', category: 'stop_slow' },
    { id: 'STOP_SLOW_LOW_SHOULDER', name: 'Stop-Slow 40-70km (Shoulder)', description: 'Generic 3: Shoulder work TCs', icon: '👷', devices: '8-12', category: 'stop_slow' },
    { id: 'STOP_SLOW_HIGH_SHOULDER', name: 'Stop-Slow 80-110km (Shoulder)', description: 'Generic 4: High speed shoulder', icon: '👷', devices: '10-15', category: 'stop_slow' },
    
    // LANE CLOSURE PATTERNS (4 patterns)
    { id: 'LANE_CLOSURE_LOW_NO_MEDIAN', name: 'Lane Closure 40-70km (No Median)', description: 'Generic 9: Undivided road', icon: '🚧', devices: '20-30', category: 'lane_closure' },
    { id: 'LANE_CLOSURE_HIGH_NO_MEDIAN', name: 'Lane Closure 80-110km (No Median)', description: 'Generic 10: High speed undivided', icon: '🚧', devices: '25-40', category: 'lane_closure' },
    { id: 'LANE_CLOSURE_LOW_MEDIAN', name: 'Lane Closure 40-70km (Median)', description: 'Generic 11: Divided road', icon: '🚧', devices: '20-30', category: 'lane_closure' },
    { id: 'LANE_CLOSURE_HIGH_MEDIAN', name: 'Lane Closure 80-110km (Median)', description: 'High speed divided', icon: '🚧', devices: '25-40', category: 'lane_closure' },
    
    // INTERSECTION PATTERNS (4 patterns)
    { id: 'ROUNDABOUT_LOW', name: 'Roundabout 40-70km', description: 'Generic 5: Roundabout TCs', icon: '🔄', devices: '15-25', category: 'intersection' },
    { id: 'ROUNDABOUT_HIGH', name: 'Roundabout 80-110km', description: 'Generic 6: High speed roundabout', icon: '🔄', devices: '18-30', category: 'intersection' },
    { id: 'T_INTERSECTION_LOW', name: 'T-Intersection 40-70km', description: 'Generic 7: T-junction TCs', icon: '⊥', devices: '12-20', category: 'intersection' },
    { id: 'T_INTERSECTION_HIGH', name: 'T-Intersection 80-110km', description: 'Generic 8: High speed T-junction', icon: '⊥', devices: '15-25', category: 'intersection' },
    
    // CONTRA FLOW PATTERNS (2 patterns)
    { id: 'CONTRA_FLOW_LOW', name: 'Contra Flow 40-70km', description: 'Generic 12: Two-way in one lane', icon: '↔️', devices: '15-25', category: 'contra_flow' },
    { id: 'CONTRA_FLOW_HIGH', name: 'Contra Flow 80-110km', description: 'Generic 13: High speed contra flow', icon: '↔️', devices: '20-35', category: 'contra_flow' },
    
    // ROAD CLOSURE PATTERNS (2 patterns)
    { id: 'ROAD_CLOSURE_DETOUR', name: 'Road Closure with Detour', description: 'Generic 14: Full closure + detour', icon: '🚫', devices: '15-25', category: 'road_closure' },
    { id: 'ROAD_CLOSURE_COURT_BOWL', name: 'Court Bowl Closure', description: 'Generic 15: Cul-de-sac closure', icon: '🚫', devices: '10-15', category: 'road_closure' },
    
    // PEDESTRIAN PATTERNS (1 pattern)
    { id: 'FOOTPATH_CLOSURE', name: 'Footpath Works', description: 'Generic 16: Pedestrian management', icon: '🚶', devices: '10-20', category: 'pedestrian' }
  ];

  const handleToggle = (templateId) => {
    const newSelection = selectedTemplates.includes(templateId)
      ? selectedTemplates.filter(id => id !== templateId)
      : [...selectedTemplates, templateId];
    onChange(newSelection);
  };

  const groupedTemplates = {
    stop_slow: tgsTemplates.filter(t => t.category === 'stop_slow'),
    lane_closure: tgsTemplates.filter(t => t.category === 'lane_closure'),
    intersection: tgsTemplates.filter(t => t.category === 'intersection'),
    contra_flow: tgsTemplates.filter(t => t.category === 'contra_flow'),
    road_closure: tgsTemplates.filter(t => t.category === 'road_closure'),
    pedestrian: tgsTemplates.filter(t => t.category === 'pedestrian')
  };

  const renderTemplateCard = (template, borderColor, bgColor) => (
    <div
      key={template.id}
      className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
        selectedTemplates.includes(template.id)
          ? `${borderColor} ${bgColor}`
          : 'border-gray-200 hover:border-gray-400 hover:bg-gray-50'
      }`}
      onClick={() => handleToggle(template.id)}
    >
      <div className="flex items-start gap-3">
        <Checkbox
          checked={selectedTemplates.includes(template.id)}
          className="mt-1"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">{template.icon}</span>
            <Label className="font-semibold cursor-pointer text-sm">
              {template.name}
            </Label>
          </div>
          <p className="text-xs text-gray-600 mb-2">
            {template.description}
          </p>
          <Badge variant="outline" className="text-xs">
            {template.devices} devices
          </Badge>
        </div>
      </div>
    </div>
  );

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>TGS Template Selection (16 Patterns Available)</span>
          <Badge variant="outline" className="ml-auto text-lg px-3 py-1">
            {selectedTemplates.length} Selected
          </Badge>
        </CardTitle>
        <CardDescription>
          Select one or more TGS patterns from GENERIC TGS PACKAGE 2026. All devices will be combined on the same map.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          
          {/* Stop-Slow Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-blue-700">👷 Stop-Slow Operations (Generic 1-4)</span>
              <div className="flex-1 h-px bg-blue-200"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.stop_slow.length} patterns</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {groupedTemplates.stop_slow.map(template => 
                renderTemplateCard(template, 'border-blue-500', 'bg-blue-50')
              )}
            </div>
          </div>

          {/* Lane Closure Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-orange-700">🚧 Lane Closures (Generic 9-11)</span>
              <div className="flex-1 h-px bg-orange-200"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.lane_closure.length} patterns</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {groupedTemplates.lane_closure.map(template => 
                renderTemplateCard(template, 'border-orange-500', 'bg-orange-50')
              )}
            </div>
          </div>

          {/* Intersection Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-purple-700">🔄 Intersections (Generic 5-8)</span>
              <div className="flex-1 h-px bg-purple-200"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.intersection.length} patterns</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {groupedTemplates.intersection.map(template => 
                renderTemplateCard(template, 'border-purple-500', 'bg-purple-50')
              )}
            </div>
          </div>

          {/* Contra Flow Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-red-700">↔️ Contra Flow (Generic 12-13)</span>
              <div className="flex-1 h-px bg-red-200"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.contra_flow.length} patterns</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.contra_flow.map(template => 
                renderTemplateCard(template, 'border-red-500', 'bg-red-50')
              )}
            </div>
          </div>

          {/* Road Closure Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-gray-700">🚫 Road Closures (Generic 14-15)</span>
              <div className="flex-1 h-px bg-gray-300"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.road_closure.length} patterns</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.road_closure.map(template => 
                renderTemplateCard(template, 'border-gray-600', 'bg-gray-50')
              )}
            </div>
          </div>

          {/* Pedestrian Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-green-700">🚶 Pedestrian Management (Generic 16)</span>
              <div className="flex-1 h-px bg-green-200"></div>
              <Badge variant="outline" className="text-xs">{groupedTemplates.pedestrian.length} pattern</Badge>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.pedestrian.map(template => 
                renderTemplateCard(template, 'border-green-500', 'bg-green-50')
              )}
            </div>
          </div>

          {/* Info Box */}
          {selectedTemplates.length > 1 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex gap-2">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-900">
                <strong>Multi-Pattern Mode:</strong> {selectedTemplates.length} patterns selected. 
                Devices from all patterns will be combined on the same TGS drawing.
                Estimated total: {selectedTemplates.length * 15}-{selectedTemplates.length * 30} devices.
              </div>
            </div>
          )}
          
          {selectedTemplates.length === 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex gap-2">
              <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-900">
                <strong>Select at least one pattern</strong> to enable auto-placement.
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Info } from 'lucide-react';

/**
 * TGS Template Multi-Selector Component
 * Allows selection of multiple TGS patterns to be applied simultaneously
 */
export default function TGSTemplateSelector({ selectedTemplates, onChange }) {
  
  const tgsTemplates = [
    // STOP-SLOW PATTERNS (Work in Traffic Lane)
    {
      id: 'STOP_SLOW_LOW_TRAFFIC_LANE',
      name: 'Stop-Slow 40-70km (Traffic Lane)',
      description: 'Generic 1: Work in traffic lane with TCs',
      icon: '👷',
      devices: '10-15',
      category: 'stop_slow',
      speed: 'low'
    },
    {
      id: 'STOP_SLOW_HIGH_TRAFFIC_LANE',
      name: 'Stop-Slow 80-110km (Traffic Lane)',
      description: 'Generic 2: Work in traffic lane with TCs (high speed)',
      icon: '👷',
      devices: '12-20',
      category: 'stop_slow',
      speed: 'high'
    },
    {
      id: 'STOP_SLOW_LOW_SHOULDER',
      name: 'Stop-Slow 40-70km (Shoulder)',
      description: 'Generic 3: Work in shoulder with TCs',
      icon: '👷',
      devices: '8-12',
      category: 'stop_slow',
      speed: 'low'
    },
    {
      id: 'STOP_SLOW_HIGH_SHOULDER',
      name: 'Stop-Slow 80-110km (Shoulder)',
      description: 'Generic 4: Work in shoulder with TCs (high speed)',
      icon: '👷',
      devices: '10-15',
      category: 'stop_slow',
      speed: 'high'
    },
    
    // ROUNDABOUT PATTERNS
    {
      id: 'ROUNDABOUT_LOW',
      name: 'Roundabout 40-70km',
      description: 'Generic 5: Roundabout with TCs and side road signs',
      icon: '🔄',
      devices: '15-25',
      category: 'intersection',
      speed: 'low'
    },
    {
      id: 'ROUNDABOUT_HIGH',
      name: 'Roundabout 80-110km',
      description: 'Generic 6: Roundabout TCs (high speed)',
      icon: '🔄',
      devices: '18-30',
      category: 'intersection',
      speed: 'high'
    },
    
    // T-INTERSECTION PATTERNS
    {
      id: 'T_INTERSECTION_LOW',
      name: 'T-Intersection 40-70km',
      description: 'Generic 7: T-intersection with TCs',
      icon: '⊥',
      devices: '12-20',
      category: 'intersection',
      speed: 'low'
    },
    {
      id: 'T_INTERSECTION_HIGH',
      name: 'T-Intersection 80-110km',
      description: 'Generic 8: T-intersection TCs (high speed)',
      icon: '⊥',
      devices: '15-25',
      category: 'intersection',
      speed: 'high'
    },
    
    // LANE CLOSURE NO MEDIAN
    {
      id: 'LANE_CLOSURE_LOW_NO_MEDIAN',
      name: 'Lane Closure 40-70km (No Median)',
      description: 'Generic 9: Single lane closure, undivided road',
      icon: '🚧',
      devices: '20-30',
      category: 'lane_closure',
      speed: 'low'
    },
    {
      id: 'LANE_CLOSURE_HIGH_NO_MEDIAN',
      name: 'Lane Closure 80-110km (No Median)',
      description: 'Generic 10: Lane closure (high speed, no median)',
      icon: '🚧',
      devices: '25-40',
      category: 'lane_closure',
      speed: 'high'
    },
    
    // LANE CLOSURE WITH RAISED MEDIAN
    {
      id: 'LANE_CLOSURE_LOW_MEDIAN',
      name: 'Lane Closure 40-70km (Raised Median)',
      description: 'Generic 11: Lane closure on divided road',
      icon: '🚧',
      devices: '20-30',
      category: 'lane_closure',
      speed: 'low'
    },
    {
      id: 'LANE_CLOSURE_HIGH_MEDIAN',
      name: 'Lane Closure 80-110km (Raised Median)',
      description: 'Generic 10 variant: Lane closure (high speed, median)',
      icon: '🚧',
      devices: '25-40',
      category: 'lane_closure',
      speed: 'high'
    },
    
    // CONTRA FLOW PATTERNS
    {
      id: 'CONTRA_FLOW_LOW',
      name: 'Contra Flow 40-70km',
      description: 'Generic 12: Two-way traffic in single lane',
      icon: '↔️',
      devices: '15-25',
      category: 'contra_flow',
      speed: 'low'
    },
    {
      id: 'CONTRA_FLOW_HIGH',
      name: 'Contra Flow 80-110km',
      description: 'Generic 13: Contra flow (high speed)',
      icon: '↔️',
      devices: '20-35',
      category: 'contra_flow',
      speed: 'high'
    },
    
    // ROAD CLOSURE PATTERNS
    {
      id: 'ROAD_CLOSURE_DETOUR',
      name: 'Road Closure with Detour',
      description: 'Generic 14: Complete road closure, detour routing',
      icon: '🚫',
      devices: '15-25',
      category: 'road_closure'
    },
    {
      id: 'ROAD_CLOSURE_COURT_BOWL',
      name: 'Road Closure - Court Bowl',
      description: 'Generic 15: Cul-de-sac/court bowl closure',
      icon: '🚫',
      devices: '10-15',
      category: 'road_closure'
    },
    
    // PEDESTRIAN MANAGEMENT
    {
      id: 'FOOTPATH_CLOSURE',
      name: 'Footpath Works',
      description: 'Generic 16: Footpath closure & pedestrian management',
      icon: '🚶',
      devices: '10-20',
      category: 'pedestrian'
    }
  ];

  const handleToggle = (templateId) => {
    console.log('🔘 Template clicked:', templateId);
    console.log('   Current selection:', selectedTemplates);
    
    const newSelection = selectedTemplates.includes(templateId)
      ? selectedTemplates.filter(id => id !== templateId)
      : [...selectedTemplates, templateId];
    
    console.log('   New selection:', newSelection);
    onChange(newSelection);
  };

  const getCategoryColor = (category) => {
    switch(category) {
      case 'roadwork': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'traffic_control': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'pedestrian': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const groupedTemplates = {
    roadwork: tgsTemplates.filter(t => t.category === 'roadwork'),
    traffic_control: tgsTemplates.filter(t => t.category === 'traffic_control'),
    pedestrian: tgsTemplates.filter(t => t.category === 'pedestrian')
  };

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>TGS Template Selection</span>
          <Badge variant="outline" className="ml-auto">
            {selectedTemplates.length} Selected
          </Badge>
        </CardTitle>
        <CardDescription>
          Select one or more TGS patterns to apply. Devices from all selected patterns will be combined on the same map.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          
          {/* Roadwork Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-orange-600">Roadwork Templates</span>
              <div className="flex-1 h-px bg-orange-200"></div>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.roadwork.map(template => (
                <div
                  key={template.id}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedTemplates.includes(template.id)
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-gray-200 hover:border-orange-300 hover:bg-gray-50'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleToggle(template.id);
                  }}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={(checked) => {
                        console.log('Checkbox changed:', template.id, checked);
                        handleToggle(template.id);
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    <div className="flex-1" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{template.icon}</span>
                        <Label className="font-semibold cursor-pointer">
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
              ))}
            </div>
          </div>

          {/* Traffic Control Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-blue-600">Traffic Control Templates</span>
              <div className="flex-1 h-px bg-blue-200"></div>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.traffic_control.map(template => (
                <div
                  key={template.id}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedTemplates.includes(template.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleToggle(template.id);
                  }}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={(checked) => {
                        console.log('Checkbox changed:', template.id, checked);
                        handleToggle(template.id);
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    <div className="flex-1" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{template.icon}</span>
                        <Label className="font-semibold cursor-pointer">
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
              ))}
            </div>
          </div>

          {/* Pedestrian Templates */}
          <div>
            <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="text-green-600">Pedestrian Management</span>
              <div className="flex-1 h-px bg-green-200"></div>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {groupedTemplates.pedestrian.map(template => (
                <div
                  key={template.id}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedTemplates.includes(template.id)
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-green-300 hover:bg-gray-50'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleToggle(template.id);
                  }}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={(checked) => {
                        console.log('Checkbox changed:', template.id, checked);
                        handleToggle(template.id);
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1"
                    />
                    <div className="flex-1" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{template.icon}</span>
                        <Label className="font-semibold cursor-pointer">
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
              ))}
            </div>
          </div>

          {/* Info Box */}
          {selectedTemplates.length > 1 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex gap-2">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-900">
                <strong>Multi-Pattern Mode:</strong> All {selectedTemplates.length} selected patterns will be combined on the same TGS. 
                Total estimated devices: {selectedTemplates.length * 15}-{selectedTemplates.length * 30} depending on road configuration.
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

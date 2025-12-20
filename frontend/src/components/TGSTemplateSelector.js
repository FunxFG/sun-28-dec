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
    {
      id: 'LANE_CLOSURE',
      name: 'Lane Closure',
      description: 'Single lane closure on multi-lane road (M01.2A)',
      icon: '🚧',
      devices: '20-35',
      category: 'roadwork'
    },
    {
      id: 'ROAD_CLOSURE',
      name: 'Road Closure',
      description: 'Complete road closure with detour signage',
      icon: '🚫',
      devices: '15-25',
      category: 'roadwork'
    },
    {
      id: 'STOP_SLOW_LOW_SPEED',
      name: 'Stop-Slow (Low Speed)',
      description: 'Traffic controllers for 40-70 km/h zones',
      icon: '👷',
      devices: '10-15',
      category: 'traffic_control'
    },
    {
      id: 'STOP_SLOW_HIGH_SPEED',
      name: 'Stop-Slow (High Speed)',
      description: 'Traffic controllers for 80-110 km/h zones',
      icon: '👷',
      devices: '12-20',
      category: 'traffic_control'
    },
    {
      id: 'SHOULDER_WORK',
      name: 'Shoulder Work',
      description: 'Work on road shoulder or verge',
      icon: '⚠️',
      devices: '8-15',
      category: 'roadwork'
    },
    {
      id: 'FOOTPATH_CLOSURE',
      name: 'Footpath Closure',
      description: 'Sidewalk/footpath closure with barriers',
      icon: '🚶',
      devices: '10-20',
      category: 'pedestrian'
    },
    {
      id: 'PEDESTRIAN_DETOUR',
      name: 'Pedestrian Detour',
      description: 'DDA-compliant pedestrian diversion route',
      icon: '🔄',
      devices: '8-15',
      category: 'pedestrian'
    },
    {
      id: 'CONTRA_FLOW',
      name: 'Contra Flow',
      description: 'Two-way traffic in single lane',
      icon: '↔️',
      devices: '15-30',
      category: 'traffic_control'
    }
  ];

  const handleToggle = (templateId) => {
    const newSelection = selectedTemplates.includes(templateId)
      ? selectedTemplates.filter(id => id !== templateId)
      : [...selectedTemplates, templateId];
    
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
                  onClick={() => handleToggle(template.id)}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={() => handleToggle(template.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
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
                  onClick={() => handleToggle(template.id)}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={() => handleToggle(template.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
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
                  onClick={() => handleToggle(template.id)}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={selectedTemplates.includes(template.id)}
                      onCheckedChange={() => handleToggle(template.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
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

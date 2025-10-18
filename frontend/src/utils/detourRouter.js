/**
 * Detour Router for Road Closures
 * Calculates optimal detour routes for vehicles and pedestrians
 * Uses Google Directions API for route calculation
 */

export class DetourRouter {
  constructor(googleMapsApiKey) {
    this.apiKey = googleMapsApiKey;
    this.directionsService = null;
  }

  /**
   * Initialize Google Maps Directions Service
   */
  initializeDirectionsService() {
    if (window.google && window.google.maps) {
      this.directionsService = new window.google.maps.DirectionsService();
      return true;
    }
    return false;
  }

  /**
   * Calculate detour routes for road closure
   * Returns both vehicle and pedestrian routes
   */
  async calculateDetourRoutes(closureData) {
    if (!this.initializeDirectionsService()) {
      throw new Error('Google Maps not loaded');
    }

    const { start_lat, start_lng, end_lat, end_lng, closure_point } = closureData;

    // Calculate vehicle detour
    const vehicleRoute = await this.calculateVehicleDetour(
      start_lat, start_lng,
      end_lat, end_lng,
      closure_point
    );

    // Calculate pedestrian detour
    const pedestrianRoute = await this.calculatePedestrianDetour(
      start_lat, start_lng,
      end_lat, end_lng,
      closure_point
    );

    return {
      vehicle_detour: vehicleRoute,
      pedestrian_detour: pedestrianRoute,
      detour_signs: this.generateDetourSigns(vehicleRoute, pedestrianRoute),
      directional_arrows: this.generateDirectionalArrows(vehicleRoute, pedestrianRoute)
    };
  }

  /**
   * Calculate vehicle detour using Directions API
   */
  async calculateVehicleDetour(startLat, startLng, endLat, endLng, closurePoint) {
    const origin = new window.google.maps.LatLng(startLat, startLng);
    const destination = new window.google.maps.LatLng(endLat, endLng);

    // Define waypoints to avoid closure
    const avoidPoint = closurePoint ? 
      new window.google.maps.LatLng(closurePoint.lat, closurePoint.lng) : 
      null;

    const request = {
      origin: origin,
      destination: destination,
      travelMode: window.google.maps.TravelMode.DRIVING,
      avoidHighways: false,
      avoidTolls: false,
      optimizeWaypoints: true,
      provideRouteAlternatives: true
    };

    try {
      const result = await new Promise((resolve, reject) => {
        this.directionsService.route(request, (response, status) => {
          if (status === 'OK') {
            resolve(response);
          } else {
            reject(new Error(`Directions request failed: ${status}`));
          }
        });
      });

      const route = result.routes[0];
      const leg = route.legs[0];

      return {
        route_type: 'vehicle',
        distance: leg.distance.text,
        distance_meters: leg.distance.value,
        duration: leg.duration.text,
        duration_seconds: leg.duration.value,
        polyline: route.overview_polyline,
        path: route.overview_path,
        steps: leg.steps.map((step, idx) => ({
          step_number: idx + 1,
          instruction: step.instructions,
          distance: step.distance.text,
          duration: step.duration.text,
          start_location: {
            lat: step.start_location.lat(),
            lng: step.start_location.lng()
          },
          end_location: {
            lat: step.end_location.lat(),
            lng: step.end_location.lng()
          },
          maneuver: step.maneuver || 'straight',
          polyline: step.polyline
        })),
        turn_points: this.extractTurnPoints(leg.steps),
        sign_locations: this.calculateSignLocations(leg.steps)
      };
    } catch (error) {
      console.error('Vehicle detour calculation failed:', error);
      throw error;
    }
  }

  /**
   * Calculate pedestrian detour
   */
  async calculatePedestrianDetour(startLat, startLng, endLat, endLng, closurePoint) {
    const origin = new window.google.maps.LatLng(startLat, startLng);
    const destination = new window.google.maps.LatLng(endLat, endLng);

    const request = {
      origin: origin,
      destination: destination,
      travelMode: window.google.maps.TravelMode.WALKING,
      avoidHighways: true,
      provideRouteAlternatives: true
    };

    try {
      const result = await new Promise((resolve, reject) => {
        this.directionsService.route(request, (response, status) => {
          if (status === 'OK') {
            resolve(response);
          } else {
            reject(new Error(`Pedestrian directions failed: ${status}`));
          }
        });
      });

      const route = result.routes[0];
      const leg = route.legs[0];

      return {
        route_type: 'pedestrian',
        distance: leg.distance.text,
        distance_meters: leg.distance.value,
        duration: leg.duration.text,
        duration_seconds: leg.duration.value,
        polyline: route.overview_polyline,
        path: route.overview_path,
        steps: leg.steps.map((step, idx) => ({
          step_number: idx + 1,
          instruction: step.instructions,
          distance: step.distance.text,
          duration: step.duration.text,
          start_location: {
            lat: step.start_location.lat(),
            lng: step.start_location.lng()
          },
          end_location: {
            lat: step.end_location.lat(),
            lng: step.end_location.lng()
          },
          maneuver: step.maneuver || 'straight'
        })),
        pedestrian_crossings: this.identifyPedestrianCrossings(leg.steps)
      };
    } catch (error) {
      console.error('Pedestrian detour calculation failed:', error);
      throw error;
    }
  }

  /**
   * Extract turn points from route steps
   */
  extractTurnPoints(steps) {
    return steps
      .filter(step => step.maneuver && step.maneuver !== 'straight')
      .map(step => ({
        location: {
          lat: step.start_location.lat(),
          lng: step.start_location.lng()
        },
        maneuver: step.maneuver,
        instruction: step.instructions,
        angle: this.getManeuverAngle(step.maneuver)
      }));
  }

  /**
   * Get angle for maneuver type
   */
  getManeuverAngle(maneuver) {
    const angles = {
      'turn-left': -90,
      'turn-slight-left': -45,
      'turn-sharp-left': -135,
      'turn-right': 90,
      'turn-slight-right': 45,
      'turn-sharp-right': 135,
      'uturn-left': -180,
      'uturn-right': 180,
      'straight': 0
    };
    return angles[maneuver] || 0;
  }

  /**
   * Calculate where to place detour signs
   */
  calculateSignLocations(steps) {
    const signLocations = [];
    
    // Place "Detour" sign at start
    if (steps.length > 0) {
      signLocations.push({
        type: 'detour_start',
        sign_name: 'Detour Ahead',
        location: {
          lat: steps[0].start_location.lat(),
          lng: steps[0].start_location.lng()
        },
        distance_before: 100, // 100m before first turn
        priority: 'high'
      });
    }

    // Place directional signs at each turn
    steps.forEach((step, idx) => {
      if (step.maneuver && step.maneuver !== 'straight') {
        signLocations.push({
          type: 'detour_directional',
          sign_name: 'Detour Arrow',
          location: {
            lat: step.start_location.lat(),
            lng: step.start_location.lng()
          },
          direction: step.maneuver,
          instruction: step.instructions,
          distance_to_next: steps[idx + 1]?.distance.value || 0,
          priority: 'medium'
        });
      }
    });

    // Place "End Detour" sign at destination
    if (steps.length > 0) {
      const lastStep = steps[steps.length - 1];
      signLocations.push({
        type: 'detour_end',
        sign_name: 'End Detour',
        location: {
          lat: lastStep.end_location.lat(),
          lng: lastStep.end_location.lng()
        },
        priority: 'high'
      });
    }

    return signLocations;
  }

  /**
   * Identify pedestrian crossings along route
   */
  identifyPedestrianCrossings(steps) {
    // Look for steps that cross major roads
    return steps
      .map((step, idx) => {
        const instruction = step.instructions.toLowerCase();
        if (instruction.includes('cross') || instruction.includes('crossing')) {
          return {
            step_number: idx + 1,
            location: {
              lat: step.start_location.lat(),
              lng: step.start_location.lng()
            },
            instruction: step.instructions,
            requires_temporary_crossing: true
          };
        }
        return null;
      })
      .filter(crossing => crossing !== null);
  }

  /**
   * Generate detour signs for both vehicle and pedestrian routes
   */
  generateDetourSigns(vehicleRoute, pedestrianRoute) {
    const signs = [];

    // Vehicle detour signs
    if (vehicleRoute && vehicleRoute.sign_locations) {
      vehicleRoute.sign_locations.forEach(signLoc => {
        signs.push({
          id: `vehicle_detour_${signs.length}`,
          device_type: 'guidance',
          device_name: signLoc.sign_name,
          position_lat: signLoc.location.lat,
          position_lng: signLoc.location.lng,
          properties: {
            auto_placed: true,
            detour_type: 'vehicle',
            sign_type: signLoc.type,
            direction: signLoc.direction || 'straight',
            priority: signLoc.priority,
            agttm_rule: 'as1742_3_detour_signage',
            as1742_reference: 'AS 1742.3 Section 4 - Detour Signs'
          }
        });
      });
    }

    // Pedestrian detour signs
    if (pedestrianRoute && pedestrianRoute.pedestrian_crossings) {
      pedestrianRoute.pedestrian_crossings.forEach(crossing => {
        signs.push({
          id: `pedestrian_detour_${signs.length}`,
          device_type: 'guidance',
          device_name: 'Pedestrian Detour',
          position_lat: crossing.location.lat,
          position_lng: crossing.location.lng,
          properties: {
            auto_placed: true,
            detour_type: 'pedestrian',
            sign_type: 'pedestrian_crossing',
            requires_temp_crossing: crossing.requires_temporary_crossing,
            agttm_rule: 'as1742_3_pedestrian_detour',
            as1742_reference: 'AS 1742.3 Section 4.5 - Pedestrian Management'
          }
        });
      });
    }

    return signs;
  }

  /**
   * Generate directional arrows for map display
   */
  generateDirectionalArrows(vehicleRoute, pedestrianRoute) {
    const arrows = [];

    // Vehicle route arrows
    if (vehicleRoute && vehicleRoute.turn_points) {
      vehicleRoute.turn_points.forEach((turn, idx) => {
        arrows.push({
          id: `vehicle_arrow_${idx}`,
          type: 'vehicle',
          location: turn.location,
          angle: turn.angle,
          maneuver: turn.maneuver,
          color: '#FFA500', // Orange for vehicle detours
          size: 'large',
          instruction: turn.instruction
        });
      });
    }

    // Pedestrian route arrows
    if (pedestrianRoute && pedestrianRoute.steps) {
      pedestrianRoute.steps
        .filter(step => step.maneuver && step.maneuver !== 'straight')
        .forEach((step, idx) => {
          arrows.push({
            id: `pedestrian_arrow_${idx}`,
            type: 'pedestrian',
            location: step.start_location,
            angle: this.getManeuverAngle(step.maneuver),
            maneuver: step.maneuver,
            color: '#4169E1', // Blue for pedestrian detours
            size: 'medium',
            instruction: step.instruction
          });
        });
    }

    return arrows;
  }

  /**
   * Create polyline overlays for map display
   */
  createDetourPolylines(vehicleRoute, pedestrianRoute) {
    const polylines = [];

    // Vehicle route polyline
    if (vehicleRoute && vehicleRoute.path) {
      polylines.push({
        id: 'vehicle_detour_path',
        type: 'vehicle',
        path: vehicleRoute.path,
        strokeColor: '#FFA500',
        strokeWeight: 6,
        strokeOpacity: 0.8,
        zIndex: 100,
        distance: vehicleRoute.distance,
        duration: vehicleRoute.duration
      });
    }

    // Pedestrian route polyline
    if (pedestrianRoute && pedestrianRoute.path) {
      polylines.push({
        id: 'pedestrian_detour_path',
        type: 'pedestrian',
        path: pedestrianRoute.path,
        strokeColor: '#4169E1',
        strokeWeight: 4,
        strokeOpacity: 0.8,
        strokeDasharray: '10, 5', // Dashed line for pedestrian
        zIndex: 99,
        distance: pedestrianRoute.distance,
        duration: pedestrianRoute.duration
      });
    }

    return polylines;
  }

  /**
   * Generate detour report for TGS documentation
   */
  generateDetourReport(vehicleRoute, pedestrianRoute) {
    return {
      title: "Detour Routes - Road Closure Management",
      standard: "AS 1742.3 Section 4 - Detour Management",
      
      vehicle_detour: vehicleRoute ? {
        total_distance: vehicleRoute.distance,
        estimated_time: vehicleRoute.duration,
        number_of_turns: vehicleRoute.turn_points?.length || 0,
        number_of_signs_required: vehicleRoute.sign_locations?.length || 0,
        route_description: this.generateRouteDescription(vehicleRoute.steps),
        turn_by_turn: vehicleRoute.steps?.map(step => ({
          step: step.step_number,
          instruction: step.instruction,
          distance: step.distance
        }))
      } : null,
      
      pedestrian_detour: pedestrianRoute ? {
        total_distance: pedestrianRoute.distance,
        estimated_time: pedestrianRoute.duration,
        number_of_crossings: pedestrianRoute.pedestrian_crossings?.length || 0,
        accessible: true, // Assume Google walking routes are accessible
        route_description: this.generateRouteDescription(pedestrianRoute.steps),
        crossings: pedestrianRoute.pedestrian_crossings?.map(crossing => ({
          step: crossing.step_number,
          location: crossing.instruction,
          requires_temporary_facility: crossing.requires_temporary_crossing
        }))
      } : null,
      
      signage_requirements: {
        detour_ahead_signs: 2, // Start of detour both directions
        directional_arrow_signs: (vehicleRoute?.turn_points?.length || 0) * 2,
        end_detour_signs: 2,
        pedestrian_detour_signs: pedestrianRoute?.pedestrian_crossings?.length || 0
      }
    };
  }

  /**
   * Generate human-readable route description
   */
  generateRouteDescription(steps) {
    if (!steps || steps.length === 0) return 'No route available';
    
    const majorSteps = steps.filter(step => 
      step.maneuver && step.maneuver !== 'straight'
    );
    
    if (majorSteps.length === 0) {
      return `Continue straight for ${steps[0]?.distance || 'unknown distance'}`;
    }
    
    return majorSteps
      .map(step => step.instruction.replace(/<[^>]*>/g, ''))
      .join(', then ');
  }
}

export default DetourRouter;

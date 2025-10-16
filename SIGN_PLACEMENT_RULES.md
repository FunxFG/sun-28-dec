# Sign Placement Rules & Definitions

## Current App Sign Placement Rules

The application follows **AS 1742.3** and **AGTTM (Austroads Guide to Temporary Traffic Management)** standards for sign placement:

### 1. Advance Warning Sign Distances (Speed-Based)

Based on approaching traffic speed:

| Speed Limit | Primary Warning | Secondary Warning | Tertiary Warning |
|------------|----------------|-------------------|------------------|
| ≤50 km/h   | 100m           | 50m               | -                |
| 60 km/h    | 150m           | 75m               | -                |
| 70 km/h    | 200m           | 100m              | -                |
| 80 km/h    | 250m           | 125m              | -                |
| ≥90 km/h   | 500m           | 200m              | 100m             |

**Reference**: AGTTM Table 3.2, AS 1742.3 Section 5.6

### 2. Lateral Clearances (Side Positioning)

**Verge Placement** (off-road):
- Minimum: 2.0m from carriageway edge
- Preferred: 3.0m from carriageway edge
- Maximum: 5.0m from carriageway edge

**Shoulder Placement** (on-road shoulder):
- Minimum: 0.5m from travel lane edge
- Preferred: 1.0m from travel lane edge
- Requires minimum shoulder width: 2.5m

**Reference**: AS 1742.3 Section 3.4, AGTTM Chapter 5

### 3. Sign Mounting Heights

- **Standard Signs**: 2.1m to 2.5m above ground level
- **Arrow Boards**: 1.5m above pavement
- **Overhead Signs**: As per road authority requirements

**Reference**: AS 1742.3 Appendix A

### 4. Bilateral Sign Placement

Required when:
- Multi-lane roads
- Speed zones ≥60 km/h
- Major arterial work
- Speed limit changes

**Spacing**:
- Longitudinal: 5.0m spacing between bilateral pairs
- Symmetry tolerance: ±0.5m

**Reference**: AGTTM Part 3 Section 3.2

### 5. Device Spacing

**Cones/Delineators**:
| Speed | Spacing |
|-------|---------|
| ≤50 km/h | 10m |
| 60 km/h | 15m |
| 70 km/h | 20m |
| 80 km/h | 25m |
| ≥90 km/h | 30m |

**Other Devices**:
- Barriers: 50m spacing
- Signs (sequential): Minimum 60m between signs

**Reference**: AS 1742.3 Table 5.2, AGTTM Part 3

### 6. Work Zone Categories

The app categorizes work zones to determine requirements:

**Category 1** (High Risk):
- Speed ≥80 km/h OR Traffic volume >25,000 AADT
- Bilateral signs: Required
- Minimum advance: 500m
- Traffic control: Required

**Category 2** (Medium Risk):
- Speed ≥60 km/h OR Traffic volume >10,000 AADT
- Bilateral signs: Required
- Minimum advance: 200m
- Traffic control: Required

**Category 3** (Lower Risk):
- Speed ≤50 km/h AND Traffic volume <5,000 AADT
- Bilateral signs: Optional
- Minimum advance: 100m
- Traffic control: May not be required

---

## What is a Detour?

### Definition

A **detour** is an **alternative route** that redirects traffic, pedestrians, or cyclists **around a work zone** when their normal path is closed or unsafe.

### Types of Detours

#### 1. **Vehicle Detour**
- Diverts motor vehicle traffic to an alternate road
- Used when:
  - Complete road closure required
  - Lane closures reduce capacity significantly
  - Intersection reconstruction needed
- **Requirements**:
  - Advance warning signs (DETOUR AHEAD)
  - Directional detour signs at each turn
  - END DETOUR sign when returning to normal route
  - Suitable for vehicle types (heavy vehicles, emergency access)

#### 2. **Pedestrian Detour**
- Alternative path for foot traffic
- Used when footpath/sidewalk closed
- **Requirements**:
  - Must NOT force pedestrians into live traffic lanes
  - Continuous fencing/hoarding protection
  - Accessible for people with disabilities (DDA compliant)
  - Tactile indicators maintained
  - Adequate lighting for night
  - Clear wayfinding signage
  - Width: Minimum 1.2m clear passage

**Reference**: AGTTM Part 10 Section 4 - "Pedestrian detours and not diverting onto road"

#### 3. **Cyclist Detour**
- Alternative route for bicycle traffic
- Preferred options (in order):
  1. Off-road shared path detour (safest)
  2. Protected on-road cycle lane
  3. Lane sharing with adequate width
- **Avoid**: Forcing cyclists into narrow lanes with traffic

### Detour Sign Sequence (AS 1742.3)

**Before work zone**:
1. DETOUR AHEAD (at advance warning distance)
2. DETOUR (with arrow) at actual diversion point
3. Directional arrows at each turn point

**After work zone**:
4. END DETOUR (when rejoining normal route)

### Key Requirements for Detours

✅ **Must provide**:
- Equal or better level of service
- Suitable for all vehicle classes that normally use the road
- Emergency vehicle access maintained
- Clear signage throughout
- Advance notification to affected parties

✅ **Assessment needed**:
- Route capacity analysis
- Impact on local streets
- Consultation with road authority
- Emergency services notification
- Community notification (7+ days advance)

❌ **Not acceptable**:
- Forcing pedestrians into live traffic
- Inadequate wayfinding causing confusion
- Routes unsuitable for vehicle types
- No accessibility for disabled persons
- Unsafe cycling conditions

### References

- **AS 1742.3**: Sections 5.6, 5.7, 6.3 (Detour signage and design)
- **AGTTM Part 3**: Section 6 (Detour routes)
- **AGTTM Part 10**: Section 4 (Pedestrian management)
- **DDA Standards**: Accessible detour requirements
- **AS 1428**: Design for Access and Mobility

---

## Implementation in the App

The app currently implements:
- ✅ Sign placement distances (speed-based)
- ✅ Lateral clearances (verge/shoulder)
- ✅ Bilateral placement logic
- ✅ Work zone categorization
- ✅ Device spacing rules

**Not yet implemented**:
- ⚠️ Detour route planning
- ⚠️ Detour signage placement
- ⚠️ Pedestrian/cyclist detour assessment
- ⚠️ Alternative route capacity analysis

Would you like me to add detour planning functionality to the app?

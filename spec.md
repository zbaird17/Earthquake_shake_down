## Purpose
An interactive 2D structural dynamics simulator for engineering students to design multi-story framed towers and test their ability to withstand earthquakes.

## Scope
The app is a single-page tool for designing 2D framed towers and testing them with horizontal sine-wave shaking. It is intended for conceptual engineering learning, not building-code certification.

## User Workflow
The app opens in design mode with a blank 1 ft grid.

1. The user selects columns, beams, diagonal braces, or floor masses from the toolbar.
2. The user places structural elements on the grid. Placement snaps to 1 ft grid lines and lengths are measured in feet.
3. The user may select **Load Starter Tower** to replace the blank grid with a simple starter design. If a custom structure is already in place, loading the starter tower should require confirmation.
4. The user sets the shake table's sine-wave amplitude and frequency.
5. The user starts the test. While a test is running, the structure is fixed and cannot be edited.
6. The app animates the shake table and tower, displaying stress states and structural failure.
7. The test ends with a win after 10.0 seconds of survival, or with a failure if a floor mass reaches the ground or the structure collapses.
8. The user may stop the test or clear the structure to return to design mode.

## Initial State
The app starts with no structural elements, floor masses, or starter tower. The blank canvas includes a 1 ft grid for placement and design.

A clearly labeled **Load Starter Tower** control adds a simple default frame. It is optional, and it replaces the current structure only when the user activates it.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($300/ft), and floor masses ($20/ft), placed via grid snapping.

Grid Resolution: 1 ft between adjacent grid lines.

Shaking Controls: Shake table amplitude A and frequency f for a sine-wave test. Each value has a slider and a corresponding synchronized number box.

Simulation Controls: Start/Stop Test button and Clear Structure button.

## Calculations
2D Rigid-Body Physics (Matter.js): Conversion scale of 
g=32.2 ft/s 

Joint Failure: If the force exfeeds 15 kip at any joint, the Matter.js constraint breaks.

Tower wins if it survived for 10.0 s without any floor mass colliding with the ground plane.

## Outputs
Real-time animation of the tower, shake table motion, color-coded joint stress states, and structural collapse.

Numerical Readouts: Total Cost ($)
Elapsed Survival Time (s)
Peak Ground Acceleration (g)
High Score (g)

## Look and Feel
A clean, single-page layout featuring a central interactive
600×500 px simulation canvas, a top toolbar for selecting structural members, and a collapsible sidebar for seismic parameters and readouts. On mobile viewports, the control panel stacks cleanly beneath the canvas with touch-friendly placement buttons.

## Validation
Free-Fall Calibration: a block starting 10ft off the ground should take .78811 seconds to fall to the ground
Measure the table's motion from the animation (the time for 10 cycles and the distance between the extremes) and compare it to the frequency and amplitude set.


## Out of Scope
Three-dimensional out-of-plane torsion or buckling
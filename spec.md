## Purpose
An interactive 2D structural dynamics simulator for engineering students to design multi-story framed towers and test their ability to withstand horizontal sine-wave shaking. This is a single-page conceptual learning tool, not a building-code certification system.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($300/ft), and floor masses ($20/ft), placed via grid snapping.

Grid Resolution: The canvas has 1 ft grid lines, and placement snaps to those lines. Structural lengths are measured in feet.

Shaking Controls: Shake table amplitude A and frequency f for a sine-wave test. Each value has a slider and a corresponding synchronized number box.

Simulation Controls: Start/Stop Test button and Clear Structure button.

The app opens in design mode with a blank grid and no structural elements or floor masses. The user selects a structural element, places it on the 1 ft grid, and may remove or revise the design before testing. A clearly labeled **Load Starter Tower** button replaces the blank design with a simple default frame; if a custom structure is already in place, loading the starter tower requires confirmation.

The user sets the sine-wave amplitude and frequency, starts the test, and observes the shake table and tower. During testing, the structure cannot be edited. The user may stop the test manually or clear the structure to return to design mode.

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
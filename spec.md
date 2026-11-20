## Purpose
An interactive 2D structural dynamics simulator for engineering students to design multi-story framed towers and test their ability to withstand earthquakes.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($300/ft), and floor masses ($20/ft), placed via grid snapping.

Shaking Controls: Shake table amplitude A, frequency f. Sliders with corresponding number boxes

Simulation Controls: Start/Stop Test button, Clear Structure button, and Ground Motion Mode toggle (Sine Wave vs. 1940 El Centro Ground Motion).

## Calculations
2D Rigid-Body Physics (Matter.js): Conversion scale of 
g=32.2 ft/s 

Shake Table Displacement: For harmonic motion, horizontal table position is 

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
Free-Fall Calibration: 

## Out of Scope
Three-dimensional out-of-plane torsion or buckling
## Purpose
An interactive 2D structural-dynamics learning tool for engineering students to design multi-story framed towers, compare structural choices and construction costs, and observe their approximate response to user-selected horizontal sine-wave shaking. The app supports conceptual instruction and design exploration rather than formal structural analysis or building-code certification.

## Inputs
Structural Elements (Canvas Placement): Columns ($50/ft), beams ($40/ft), diagonal braces ($300/ft), and floor masses ($20/ft), placed via grid snapping.

Grid Resolution: The canvas has 1 ft grid lines, and placement snaps to those lines. Structural lengths are measured in feet. All structural elements and floor masses must remain within the visible canvas boundary.

Floor Masses: Floor masses may be placed freely at any grid point. Placement does not require a specific attachment location.

Shaking Controls: Shake table amplitude A ranges from 0 to 12 inches, and frequency f ranges from 0.1 to 10 Hz for a sine-wave test. Each value has a slider and a corresponding synchronized number box.

Simulation Controls: Start/Stop Test button, Clear Structure button, and Load Starter Tower button.

The app opens in design mode with a blank grid and no structural elements or floor masses. The user selects a structural element, places it on the 1 ft grid, and may remove or revise the design before testing. Invalid placements outside the canvas boundary are rejected or prevented.

A clearly labeled **Load Starter Tower** button replaces the blank design with a simple default frame. If a custom structure is already in place, loading the starter tower requires confirmation.

The user sets the sine-wave amplitude and frequency, starts the test, and observes the shake table and tower. During testing, the structure cannot be edited. The user may stop the test manually or clear the structure to return to design mode.

## Calculations
2D Rigid-Body Physics (Matter.js): The simulation uses 2D rigid-body physics to model tower motion and constraints. Unit conversion must consistently represent positions, forces, acceleration, and time.

Gravity: Earth gravity is 32.2 ft/s². Mars gravity is 12.21 ft/s², and Moon gravity is 5.33 ft/s². Selecting a gravity mode applies the corresponding acceleration to the simulation.

Shake Table Displacement: For sine-wave shaking, horizontal table displacement is `x(t) = A sin(2πft)`, where A is amplitude in inches, f is frequency in Hz, t is elapsed time in seconds, and the table starts at zero displacement.

Joint Failure: If the force magnitude at any joint exceeds 15 kip, the associated Matter.js constraint breaks.

Tower wins if it survives for 10.0 seconds without any floor mass colliding with the ground plane.

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

## Features
Place a gravity control at the bottom of the app for Earth, Mars, and Moon modes. Earth uses the default 32.2 ft/s² setting and appearance. Mars uses 12.21 ft/s² and changes the background to red. The Moon uses 5.33 ft/s² and changes the background to grey.
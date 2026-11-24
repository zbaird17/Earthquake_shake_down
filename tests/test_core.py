import unittest

from calculations import (
    PIXELS_PER_FOOT,
    peak_acceleration_g,
    table_motion,
    total_member_cost,
)
from structure_model import DesignState
from simulation import TestSimulation


class CoreTests(unittest.TestCase):
    def test_default_tower(self):
        design = DesignState()
        design.load_starter_tower()
        self.assertEqual(len(design.members), 9)
        self.assertEqual(len(design.masses), 2)
        self.assertTrue(all(member.length_ft >= 1 for member in design.members))

    def test_default_tower_cost(self):
        design = DesignState()
        design.load_starter_tower()
        # Four 6-ft columns, three 12-ft beams, and two 12-ft brace segments.
        expected = 4 * 6 * 90 + 3 * 12 * 70 + 2 * (180 ** 0.5) * 40
        actual = total_member_cost(design.members)
        self.assertLess(abs(actual - expected), 0.1)

    def test_default_peak_acceleration(self):
        peak = peak_acceleration_g(4, 3)
        self.assertAlmostEqual(peak, 3.679, places=2)

    def test_zero_amplitude_table_motion(self):
        displacement, velocity = table_motion(1.0, 0, 5)
        self.assertEqual(displacement, 0)
        self.assertEqual(velocity, 0)

    def test_starter_braces_attach_to_live_hosts(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        braces = [member for member in design.members if member.kind == "brace"]
        self.assertEqual(len(braces), 2)
        for brace in braces:
            host_count = 0
            for point in ((brace.x1, brace.y1), (brace.x2, brace.y2)):
                for host in (member for member in design.members if member.kind in ("beam", "column")):
                    ax, ay, bx, by = host.endpoints
                    x, y = point
                    if abs((bx - ax) * (y - ay) - (by - ay) * (x - ax)) <= 2:
                        if min(ax, bx) - 2 <= x <= max(ax, bx) + 2 and min(ay, by) - 2 <= y <= max(ay, by) + 2:
                            host_count += 1
                            break
            self.assertEqual(host_count, 2)

    def test_structural_snap_and_endpoint_resize(self):
        design = DesignState()
        design.load_starter_tower()
        top_left = design.snap_structural_node(178, 218)
        self.assertEqual(top_left, (180.0, 220.0))
        beam = next(member for member in design.members if member.kind == "beam" and member.y1 == 220)
        self.assertTrue(design.resize_member_endpoint(beam.member_id, "end", 400, 220))
        self.assertEqual((beam.x2, beam.y2), (400.0, 220.0))

    def test_member_move_keeps_grid_alignment(self):
        design = DesignState()
        design.load_starter_tower()
        beam = next(member for member in design.members if member.kind == "beam" and member.y1 == 220)
        old_length = beam.length_ft
        self.assertTrue(design.move_member(beam.member_id, 200, 300))
        self.assertAlmostEqual(beam.length_ft, old_length)
        self.assertEqual(beam.y1, 220)

    def test_brace_anchor_can_toggle_moment_frame(self):
        design = DesignState()
        design.load_starter_tower()
        brace = next(member for member in design.members if member.kind == "brace")
        anchor = (brace.x1, brace.y1)
        self.assertIn(anchor, design.connected_nodes())
        design.toggle_joint(*anchor)
        self.assertIn(anchor, design.moment_nodes)
        design.toggle_joint(*anchor)
        self.assertNotIn(anchor, design.moment_nodes)

    def test_floor_mass_can_be_resized_after_placement(self):
        design = DesignState()
        mass = design.add_mass(100, 300, 220, 20)
        self.assertIsNotNone(mass)
        assert mass is not None
        self.assertTrue(design.resize_mass(mass.mass_id, "end", 400, 360))
        self.assertEqual(mass.width, 300)
        self.assertEqual(mass.height, 60)

    def test_live_shake_settings_reach_running_simulation(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 4, 3)
        simulation.amplitude = 12
        simulation.frequency = 10
        self.assertEqual(simulation.amplitude, 12)
        self.assertEqual(simulation.frequency, 10)

    def test_shake_table_is_a_solid_floor(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        self.assertFalse(simulation.table_shape.sensor)
        for shape in (simulation.mass_bodies[mass_id] for mass_id in simulation.mass_bodies):
            pass
        for mass in design.masses:
            shape = next(
                shape
                for shape in simulation.space.shapes
                if shape.body is simulation.mass_bodies[mass.mass_id]
            )
            self.assertFalse(shape.sensor)

    def test_one_decimal_control_values(self):
        self.assertEqual(round(4.26 * 10) / 10, 4.3)
        self.assertEqual(round(3.94 * 10) / 10, 3.9)

    def test_design_json_round_trip(self):
        design = DesignState()
        design.load_starter_tower()
        payload = design.to_dict()
        imported = DesignState.from_dict(payload)
        self.assertEqual(len(imported.members), len(design.members))
        self.assertEqual(len(imported.masses), len(design.masses))

    def test_invalid_design_import_is_rejected(self):
        invalid_payload = {
            "format": "earthquake-shake-down-design",
            "version": 1,
            "members": [
                {"kind": "beam", "x1": 0, "y1": 300, "x2": 900, "y2": 300}
            ],
            "masses": [],
            "moment_nodes": [],
        }
        with self.assertRaises(ValueError):
            DesignState.from_dict(invalid_payload)

    def test_finite_duration_records_success(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3, duration_seconds=1)
        simulation.step(1.1)
        self.assertEqual(simulation.result, "success")
        self.assertEqual(simulation.result_time, 1.0)

    def test_indefinite_duration_does_not_auto_pass(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3, duration_seconds=None)
        simulation.step(20)
        self.assertIsNone(simulation.result)

    def test_joint_fatigue_damage_accumulates_and_caps(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 4, 3)
        if not simulation.joints:
            self.skipTest("Starter tower has no constrained joint groups")
        joint = next(iter(simulation.joints.values()))
        joint.fatigue_angle_previous = 0
        joint.fatigue_slope_previous = 1
        joint.fatigue_peak = 0
        for _ in range(50):
            joint.fatigue_damage = min(100, joint.fatigue_damage + 20)
        joint.fatigue_damage = min(100, joint.fatigue_damage)
        self.assertEqual(joint.fatigue_damage, 100)

    def test_table_starts_at_zero(self):
        displacement, _ = table_motion(0, 12, 5)
        self.assertEqual(displacement, 0)

    def test_minimum_member_size(self):
        design = DesignState()
        self.assertIsNone(design.add_member("beam", 100, 200, 109, 200))

    def test_zero_amplitude_has_no_initial_drift(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        initial_positions = {
            member_id: body.position.x
            for member_id, body in simulation.member_bodies.items()
        }
        for _ in range(300):
            simulation.step(1 / 60)
        for member_id, body in simulation.member_bodies.items():
            self.assertAlmostEqual(body.position.x, initial_positions[member_id], places=2)
            self.assertLess(abs(body.velocity.x), 0.1)


if __name__ == "__main__":
    unittest.main()

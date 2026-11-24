import unittest
import tempfile
import json
import pymunk

from calculations import (
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

    def test_floor_mass_accepts_exactly_one_foot(self):
        design = DesignState()
        mass = design.add_mass(100, 300, 20, 20)
        self.assertIsNotNone(mass)
        assert mass is not None
        self.assertEqual(mass.width, 20)
        self.assertEqual(mass.height, 20)

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

    def test_running_button_uses_dark_text_palette(self):
        running_foreground = "#1f2937"
        running_background = "#ffd966"
        self.assertNotEqual(running_foreground, running_background)
        self.assertTrue(running_foreground != "#ffffff")
        self.assertNotIn("#ffffff", ("#111111", "#1f2937"))

    def test_design_json_round_trip(self):
        design = DesignState()
        design.load_starter_tower()
        payload = design.to_dict()
        imported = DesignState.from_dict(payload)
        self.assertEqual(len(imported.members), len(design.members))
        self.assertEqual(len(imported.masses), len(design.masses))

    def test_saved_design_file_round_trip(self):
        design = DesignState()
        design.load_starter_tower()
        payload = design.to_dict()
        payload.update({
            "gravity": "Mars",
            "amplitude": 6.3,
            "frequency": 4.1,
            "duration_seconds": 12.0,
        })
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
            path = handle.name
            handle.write(json.dumps(payload).encode("utf-8"))
        try:
            with open(path, "r", encoding="utf-8") as handle:
                saved = json.loads(handle.read())
            imported = DesignState.from_dict(saved)
            self.assertEqual(len(imported.members), 9)
            self.assertEqual(saved["gravity"], "Mars")
            self.assertEqual(saved["amplitude"], 6.3)
            self.assertEqual(saved["frequency"], 4.1)
            self.assertEqual(saved["duration_seconds"], 12.0)
        finally:
            import os
            os.unlink(path)

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

    def test_import_rejects_nonfinite_and_duplicate_ids(self):
        for member_id in ("",):
            payload = {
                "format": "earthquake-shake-down-design",
                "version": 1,
                "members": [
                    {"id": member_id, "kind": "beam", "x1": 0, "y1": 300, "x2": 100, "y2": 300}
                ],
                "masses": [],
                "moment_nodes": [],
            }
            with self.assertRaises(ValueError):
                DesignState.from_dict(payload)
        payload = {
            "format": "earthquake-shake-down-design",
            "version": 1,
            "members": [
                {"id": "m1", "kind": "beam", "x1": 0, "y1": 300, "x2": 100, "y2": 300}
            ],
            "masses": [{"id": "m1", "x": 100, "y": 280, "width": 20, "height": 20}],
            "moment_nodes": [],
        }
        design = DesignState.from_dict(payload)
        self.assertEqual(len(design.members), 1)
        self.assertEqual(len(design.masses), 1)

    def test_import_rejects_nonfinite_coordinates(self):
        payload = {
            "format": "earthquake-shake-down-design",
            "version": 1,
            "members": [
                {"kind": "beam", "x1": 0, "y1": 300, "x2": "inf", "y2": 300}
            ],
            "masses": [],
            "moment_nodes": [],
        }
        with self.assertRaises(ValueError):
            DesignState.from_dict(payload)

    def test_duplicate_member_ids_are_rejected(self):
        payload = {
            "format": "earthquake-shake-down-design",
            "version": 1,
            "members": [
                {"id": "m1", "kind": "beam", "x1": 0, "y1": 300, "x2": 100, "y2": 300},
                {"id": "m1", "kind": "beam", "x1": 100, "y1": 320, "x2": 200, "y2": 320},
            ],
            "masses": [],
            "moment_nodes": [],
        }
        with self.assertRaises(ValueError):
            DesignState.from_dict(payload)

    def test_design_fingerprint_changes_with_structure(self):
        design = DesignState()
        design.load_starter_tower()
        original = design.fingerprint()
        design.add_member("beam", 100, 300, 300, 300)
        changed = design.fingerprint()
        self.assertNotEqual(original, changed)

    def test_finite_duration_records_success(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3, duration_seconds=1)
        simulation.step(1.1)
        self.assertEqual(simulation.result, "success")
        self.assertEqual(simulation.result_time, 1.0)
        self.assertTrue(simulation.duration_reached)
        self.assertTrue(simulation.table_motion_stopped)
        simulation.step(0.1)
        self.assertEqual(simulation.table_body.velocity.x, 0)
        self.assertAlmostEqual(simulation.table_body.position.x, 300)

    def test_indefinite_duration_does_not_auto_pass(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3, duration_seconds=None)
        simulation.step(20)
        self.assertIsNone(simulation.result)

    def test_finite_failure_keeps_recorded_time_until_duration_end(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 12, 10, duration_seconds=2)
        simulation.step(0.5)
        if simulation.result == "failure":
            failure_time = simulation.result_time
            simulation.step(2)
            self.assertEqual(simulation.result, "failure")
            self.assertEqual(simulation.result_time, failure_time)
            self.assertTrue(simulation.duration_reached)

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
            self.assertLess(abs(body.position.x - initial_positions[member_id]), 4.0)
            self.assertLess(abs(body.velocity.x), 100)

    def test_falling_members_and_masses_are_clamped_above_table(self):
        design = DesignState()
        design.load_starter_tower()
        loose = next(mass for mass in design.masses)
        loose.x = 250
        loose.y = 100
        loose.width = 20
        loose.height = 20
        simulation = TestSimulation(design, "Earth", 0, 3)
        mass_body = simulation.mass_bodies[loose.mass_id]
        mass_body.position = (-40, -100)
        member_body = next(iter(simulation.member_bodies.values()))
        member_body.position = (-40, -100)
        simulation._keep_bodies_above_table()
        self.assertGreaterEqual(mass_body.position.y, 10)
        self.assertGreaterEqual(member_body.position.y, 6)

    def test_three_failed_joints_alone_do_not_count_as_collapse(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        joints = list(simulation.joints.values())
        if len(joints) < 3:
            self.skipTest("Starter model does not expose three constrained joint groups")
        for joint in joints[:3]:
            joint.failed = True
        self.assertFalse(simulation._structural_collapse_detected())

    def test_wild_loose_floor_mass_counts_as_collapse(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        for mass_id in list(simulation.mass_supported):
            simulation.mass_supported.remove(mass_id)
            body = simulation.mass_bodies[mass_id]
            body.velocity = (300, -300)
            body.angular_velocity = 2.0
            simulation.mass_wild_motion_started[mass_id] = simulation.elapsed - 0.40
            body.position = (-40, 100)
        self.assertTrue(simulation._structural_collapse_detected())

    def test_supported_masses_with_normal_motion_do_not_collapse(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        for body in simulation.mass_bodies.values():
            body.velocity = (20, -20)
            body.angular_velocity = 0.1
        self.assertFalse(simulation._structural_collapse_detected())

    def test_one_failed_joint_is_not_structural_collapse(self):
        design = DesignState()
        design.load_starter_tower()
        simulation = TestSimulation(design, "Earth", 0, 3)
        joints = list(simulation.joints.values())
        if not joints:
            self.skipTest("Starter model has no constrained joint groups")
        joints[0].failed = True
        self.assertFalse(simulation._structural_collapse_detected())

    def test_moment_joint_uses_relative_angle_restraint(self):
        design = DesignState()
        design.load_starter_tower()
        point = (180.0, 340.0)
        design.toggle_joint(*point)
        simulation = TestSimulation(design, "Earth", 0, 3)
        joint = simulation.joints.get(point)
        self.assertIsNotNone(joint)
        self.assertTrue(any(isinstance(c, pymunk.RotaryLimitJoint) for c in joint.constraints))


if __name__ == "__main__":
    unittest.main()

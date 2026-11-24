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

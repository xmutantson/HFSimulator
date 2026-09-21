import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "src" / "HFSim_BFD_2_04" / "HFSim_BFD_2_04.ino"
PROTO = (
    ROOT
    / "hardware"
    / "Alternate hardware platforms"
    / "src"
    / "HFSim_BFD_2_04_Proto"
    / "HFSim_BFD_2_04_Proto.ino"
)


class FirmwareRevisionTest(unittest.TestCase):
    def test_sketches_follow_the_2_04_naming_convention(self):
        self.assertTrue(PRODUCTION.is_file())
        self.assertTrue(PROTO.is_file())
        self.assertFalse((ROOT / "src" / "HFSim_BFD_2_03").exists())
        self.assertFalse(
            (
                ROOT
                / "hardware"
                / "Alternate hardware platforms"
                / "src"
                / "HFSim_BFD_2_03_Proto"
            ).exists()
        )

    def test_live_revision_surfaces_report_2_04(self):
        for firmware in (PRODUCTION, PROTO):
            with self.subTest(firmware=str(firmware.relative_to(ROOT))):
                source = firmware.read_text(encoding="utf-8")
                self.assertIn('#define HFSIM_FIRMWARE_REVISION "2.04"', source)
                self.assertIn('Serial.print(" REV=" HFSIM_FIRMWARE_REVISION)', source)
                self.assertIn('F("HELP IONOS SIM Rev " HFSIM_FIRMWARE_REVISION)', source)
                self.assertNotIn('strRevision = "    Rev 2.03', source)


if __name__ == "__main__":
    unittest.main()

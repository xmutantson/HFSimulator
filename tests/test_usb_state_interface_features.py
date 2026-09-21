import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRMWARES = (
    ROOT / "src" / "HFSim_BFD_2_03" / "HFSim_BFD_2_03.ino",
    ROOT
    / "hardware"
    / "Alternate hardware platforms"
    / "src"
    / "HFSim_BFD_2_03_Proto"
    / "HFSim_BFD_2_03_Proto.ino",
)


def section(source: str, start: str, end: str) -> str:
    start_index = source.index(start)
    return source[start_index : source.index(end, start_index)]


class USBStateInterfaceFeatureTest(unittest.TestCase):
    def test_features_are_independent_and_dsp_authoritative(self):
        for firmware in FIRMWARES:
            with self.subTest(firmware=str(firmware.relative_to(ROOT))):
                source = firmware.read_text(encoding="utf-8")

                self.assertIn('if (strCmd == "STATUS") {PrintStatus();}', source)
                self.assertIn('else if (strCmd == "LEVEL") {PrintLevel();}', source)
                self.assertIn('else if (strCmd == "HELP") {PrintHelp();}', source)
                self.assertIn('Serial.println(F("END HELP"))', source)
                self.assertIn('strCmd == "RESET"', source)
                self.assertIn('strCmd == "CODECINIT"', source)
                self.assertIn('Serial.println(F("MAINTENANCE: CODECINIT | RESET"))', source)

                codec = section(source, 'else if (strCmd == "CODECINIT")', 'else if (strCmd == "STATUS")')
                self.assertLess(codec.index("ReinitCodec();"), codec.index("OK CODECINIT"))
                self.assertIn("ulngAppliedGeneration++", codec)

                reset = section(source, 'if (strCmd == "RESET")', 'else if (strCmd == "CODECINIT")')
                self.assertLess(reset.index("Serial.flush();"), reset.index("SCB_AIRCR"))

                ack = section(source, "void PrintDSPStateAck(", "void PrintStatus()")
                self.assertIn("SimulatorStateParameterText(intMode)", ack)
                self.assertIn("BusyStateParameterText(intBusyMode)", ack)
                self.assertIn("ulngAppliedGeneration", ack)
                self.assertIn('" OK" : " ERROR"', ack)

                status = section(source, "void PrintStatus()", "void PrintLevel()")
                for live_variable in (
                    "chrModes[intMode]",
                    "intTargetSN",
                    "intMultipaths",
                    "intFadeDepth_dB",
                    "fltFadeRate",
                    "intTuneOffset",
                    "intGainLevel[0]",
                    "intGainLevel[1]",
                    "intGainLevel[2]",
                    "intGainLevel[3]",
                    "intBandwidth",
                    "ulngAppliedGeneration",
                    "chrBuildIdentity",
                ):
                    self.assertIn(live_variable, status)
                self.assertIn("PrintLevelFields();", status)

                level_fields = section(source, "void PrintLevelFields()", "void PrintStatus()")
                for measured_level in (
                    "fltppLPInputMeasAvg",
                    "fltppAmpLeftOutAvg",
                    "fltppAmpRightOutAvg",
                ):
                    self.assertIn(measured_level, level_fields)

                watchdog = section(source, "void DisplayWatchdog(", "void PrintDSPStateAck(")
                self.assertIn("RenderDSPStateToTFT()", watchdog)
                self.assertIn("DSPDisplayValue()", watchdog)
                self.assertIn("30000", watchdog)
                self.assertNotIn("intMode =", watchdog)
                self.assertNotIn("intTargetSN =", watchdog)
                self.assertNotIn("intBusyMode =", watchdog)

                renderer = section(source, "void RenderDSPStateToTFT()", "void DisplayWatchdog(")
                self.assertIn("10 * fltLogs[intFMRatePtr]", renderer)
                self.assertNotIn("100 * fltLogs[intFMRatePtr]", renderer)

                self.assertIn("DisplayWatchdog(false);", source)
                self.assertIn("SimulatorRequestConfirmed(strParameter", source)
                self.assertIn("BusyRequestConfirmed(strParameter", source)


if __name__ == "__main__":
    unittest.main()

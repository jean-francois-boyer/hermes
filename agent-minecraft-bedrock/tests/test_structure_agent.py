from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "structure_agent.py"


def load_module():
    spec = importlib.util.spec_from_file_location("structure_agent", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StructureAgentTests(unittest.TestCase):
    def test_generate_village_structure_outputs_mcfunction_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            outputs = module.generate_structure(
                brief="village médiéval avec spawn, maisons, marché et donjon",
                name="Village Test",
                output_dir=Path(tmp),
            )

            main_file = outputs["main"]
            self.assertTrue(main_file.exists())
            content = main_file.read_text(encoding="utf-8")
            self.assertIn("Structure: Village Test", content)
            self.assertIn("fill", content)
            self.assertIn("setblock", content)
            self.assertIn("function village-test_spawn", content)

            self.assertTrue(outputs["spawn"].exists())
            self.assertTrue(outputs["market"].exists())
            self.assertTrue(outputs["guide"].exists())

    def test_generate_dungeon_structure_contains_mob_and_reward_commands(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            outputs = module.generate_structure(
                brief="donjon sombre avec boss, pièges et coffre récompense",
                name="Donjon Test",
                output_dir=Path(tmp),
            )

            content = outputs["main"].read_text(encoding="utf-8")
            self.assertIn("summon", content)
            self.assertIn("chest", content)
            self.assertIn("Donjon Test", outputs["guide"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

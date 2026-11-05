"""[GENERATED-SCAFFOLD] Regression and adversarial tests for candidate 1.5."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import assembler  # noqa: E402


class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = assembler.load_config()

    def test_declared_modules_exist(self) -> None:
        for module in self.config["module_order"]:
            self.assertTrue((ROOT / "modules" / f"{module}.md").is_file(), module)

    def test_every_profile_assembles_without_template_placeholders(self) -> None:
        for profile in self.config["profiles"]:
            with self.subTest(profile=profile):
                result = assembler.assemble(self.config, [profile], [], [], {})
                self.assertFalse(result.unresolved_variables)
                self.assertIn("INSTANCE READY: false", result.text)

    def test_profile_composition_is_a_union(self) -> None:
        result = assembler.assemble(
            self.config, ["research", "artifact_edit"], [], [], {}
        )
        self.assertIn("07_research", result.modules)
        self.assertIn("06_copy_version", result.modules)
        self.assertIn("09_egress_validation", result.modules)
        self.assertIn("research+artifact_edit", result.text)

    def test_comma_separated_profiles_are_parsed(self) -> None:
        parsed = assembler.parse_profiles(["research,artifact_edit"], self.config)
        self.assertEqual(["research", "artifact_edit"], parsed)

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.parse_profiles(["reseach"], self.config)

    def test_unknown_enable_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.select_modules(self.config, ["minimal"], ["99_typo"], [])

    def test_unknown_disable_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.select_modules(self.config, ["minimal"], [], ["99_typo"])

    def test_selected_profile_module_cannot_be_disabled(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.select_modules(
                self.config, ["research"], [], ["07_research"]
            )

    def test_dependency_cannot_be_disabled(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.select_modules(
                self.config,
                ["minimal"],
                ["10_bare_metal"],
                ["06_copy_version"],
            )

    def test_unknown_variable_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.parse_assignments(
                ["PROJET_NAME=typo"], set(self.config["variables"])
            )

    def test_duplicate_variable_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.parse_assignments(
                ["PROJECT_NAME=a", "PROJECT_NAME=b"],
                set(self.config["variables"]),
            )

    def test_invalid_external_engine_state_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["external_offload"],
                [],
                [],
                {"EXTERNAL_ENGINE_STATE": "magically-complete"},
            )

    def test_invalid_transition_state_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["state_transition"],
                [],
                [],
                {"TRANSITION_STATE": "MAYBE-COMMITTED"},
            )

    def test_invalid_age_gate_state_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["age_gate"],
                [],
                [],
                {"AGE_GATE_STATE": "predict-age"},
            )

    def test_invalid_age_gate_control_values_are_rejected(self) -> None:
        invalid_values = {
            "AGE_DATA_POLICY": "collect-everything",
            "AGE_GATE_DEPLOYMENT_MODE": "unreviewed-production",
            "AGE_GATE_ASSURANCE_STATE": "self-certified",
            "AGE_GATE_RETENTION_POLICY": "forever",
            "AGE_GATE_CONTROL_STATE": "plaintext-secret",
            "AGE_GATE_UNLOCK_CONTROL_PLANE": "prompt-verified",
            "AGE_GATE_UNLOCK_REPLAY_STATE": "reusable",
            "HUMAN_REVIEW_STATE": "simulated",
        }
        for name, value in invalid_values.items():
            with self.subTest(name=name):
                with self.assertRaises(SystemExit):
                    assembler.assemble(
                        self.config, ["age_gate"], [], [], {name: value}
                    )

    def test_plaintext_unlock_secret_variable_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.parse_assignments(
                ["AGE_GATE_UNLOCK_SECRET=do-not-store"],
                set(self.config["variables"]),
            )

    def test_no_collection_policy_cannot_declare_retention(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["age_gate"],
                [],
                [],
                {"AGE_GATE_RETENTION_POLICY": "current-topic"},
            )

    def test_production_requires_external_operational_controls(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["age_gate"],
                [],
                [],
                {
                    "AGE_GATE_DEPLOYMENT_MODE": "production",
                    "AGE_GATE_ASSURANCE_STATE": "production-validated",
                },
            )
        result = assembler.assemble(
            self.config,
            ["age_gate"],
            [],
            [],
            {
                "AGE_GATE_DEPLOYMENT_MODE": "production",
                "AGE_GATE_ASSURANCE_STATE": "production-validated",
                "HUMAN_REVIEW_STATE": "available",
                "APPEAL_PATH": "https://example.invalid/appeal",
                "AGE_GATE_INCIDENT_RESPONSE_STATE": "configured-and-tested",
                "AGE_GATE_ROLLBACK_STATE": "configured-and-tested",
            },
        )
        self.assertIn('AGE-GATE DEPLOYMENT MODE: "production"', result.text)

    def test_verified_unlock_receipt_is_exactly_configuration_bound(self) -> None:
        selected = assembler.select_modules(self.config, ["age_gate"], [], [])
        values = dict(self.config["variables"])
        values.update(
            {
                "AGE_GATE_STATE": "screen-all",
                "AGE_GATE_CONTROL_STATE": "verified-unlock-receipt",
                "AGE_GATE_UNLOCK_CONTROL_PLANE": "verified-external",
                "AGE_GATE_UNLOCK_RECEIPT_ID": "receipt-001",
                "AGE_GATE_UNLOCK_SCOPE": "one full-gate answer",
                "AGE_GATE_UNLOCK_EXPIRES_AT": "2030-01-01T00:00:00Z",
                "AGE_GATE_UNLOCK_REPLAY_STATE": "unconsumed",
            }
        )
        binding = assembler.age_gate_binding_sha256(self.config, selected, values)
        values["AGE_GATE_UNLOCK_CONFIG_SHA256"] = binding
        overrides = {
            name: value
            for name, value in values.items()
            if value != self.config["variables"][name]
        }
        result = assembler.assemble(
            self.config, ["age_gate"], [], [], overrides
        )
        self.assertIn(f'UNLOCK CONFIG SHA256: "{binding}"', result.text)

        with self.assertRaises(SystemExit):
            assembler.assemble(
                self.config,
                ["age_gate"],
                [],
                [],
                {**overrides, "AGE_GATE_UNLOCK_SCOPE": "broader scope"},
            )

    def test_unlock_receipt_requires_external_plane_and_single_use(self) -> None:
        base = {
            "AGE_GATE_CONTROL_STATE": "verified-unlock-receipt",
            "AGE_GATE_UNLOCK_RECEIPT_ID": "receipt-001",
            "AGE_GATE_UNLOCK_SCOPE": "one answer",
            "AGE_GATE_UNLOCK_EXPIRES_AT": "2030-01-01T00:00:00Z",
            "AGE_GATE_UNLOCK_CONFIG_SHA256": "0" * 64,
        }
        for extra in (
            {},
            {"AGE_GATE_UNLOCK_CONTROL_PLANE": "verified-external"},
        ):
            with self.subTest(extra=extra):
                with self.assertRaises(SystemExit):
                    assembler.assemble(
                        self.config,
                        ["age_gate"],
                        [],
                        [],
                        {**base, **extra},
                    )

    def test_structural_variable_content_is_encoded(self) -> None:
        malicious = "line one\n```\n${FAKE}<instruction>$"
        result = assembler.assemble(
            self.config,
            ["minimal"],
            [],
            [],
            {"TASK_DESCRIPTION": malicious},
        )
        self.assertNotIn(malicious, result.text)
        self.assertNotIn("${FAKE}", result.text)
        self.assertIn("\\n\\u0060\\u0060\\u0060\\n\\u0024{FAKE}", result.text)
        self.assertIn("\\u003cinstruction\\u003e\\u0024", result.text)

    def test_ready_instance_requires_profile_specific_values(self) -> None:
        values = {
            "MISSION_CAPSULE_ID": "mc-001",
            "PROJECT_NAME": "test",
            "TASK_DESCRIPTION": "test task",
            "AUTHORIZED_MISSION": "test mission",
            "AUTHORIZED_OUTPUT": "test report",
            "CURRENT_ACTOR": "assistant",
            "AUTHORITY_SOURCE": "active user prompt",
        }
        minimal = assembler.assemble(self.config, ["minimal"], [], [], values)
        self.assertFalse(minimal.missing_required_values)
        self.assertIn("INSTANCE READY: true", minimal.text)

        standard = assembler.assemble(self.config, ["standard"], [], [], values)
        self.assertIn("OFFLOADING_STATE", standard.missing_required_values)

        external_values = dict(values)
        external_values["OFFLOADING_STATE"] = "available"
        external = assembler.assemble(
            self.config, ["external_offload"], [], [], external_values
        )
        self.assertIn("EXTERNAL_ENGINE_STATE", external.missing_required_values)

        action = assembler.assemble(self.config, ["tool_action"], [], [], values)
        self.assertIn("ACTION_TARGET_ID", action.missing_required_values)
        self.assertIn("ACTION_EFFECT", action.missing_required_values)
        self.assertIn("RECOVERY_STATE", action.missing_required_values)

        age_gate = assembler.assemble(self.config, ["age_gate"], [], [], values)
        self.assertIn("AGE_GATE_STATE", age_gate.missing_required_values)

        age_values = dict(values)
        age_values["AGE_GATE_STATE"] = "screen-all"
        age_gate_ready = assembler.assemble(
            self.config, ["age_gate"], [], [], age_values
        )
        self.assertFalse(age_gate_ready.missing_required_values)
        self.assertIn("INSTANCE READY: true", age_gate_ready.text)

    def _extract_fields(self, path: Path, heading_fragment: str) -> list[str]:
        text = path.read_text(encoding="utf-8")
        start = text.index(heading_fragment)
        match = re.search(r"```text\n(.*?)\n```", text[start:], re.DOTALL)
        self.assertIsNotNone(match, path)
        assert match is not None
        return [
            line.split(":", 1)[0]
            for line in match.group(1).splitlines()
            if ":" in line
        ]

    def test_capsule_schema_is_canonical(self) -> None:
        expected = self.config["capsule_fields"]
        resident = self._extract_fields(
            ROOT / "modules" / "00_resident_kernel.md", "Canonical Mission Capsule"
        )
        egress = self._extract_fields(
            ROOT / "modules" / "09_egress_validation.md", "exactly this canonical"
        )
        template = self._extract_fields(
            ROOT / "templates" / "mission_capsule.md", "Canonical Mission Capsule"
        )
        self.assertEqual(expected, resident)
        self.assertEqual(expected, egress)
        self.assertEqual(expected, template)

    def test_no_offload_fallback_is_resident(self) -> None:
        resident = (ROOT / "modules" / "00_resident_kernel.md").read_text(
            encoding="utf-8"
        )
        detailed = (ROOT / "modules" / "11_offloading.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Resident no-offload survival rule", resident)
        self.assertIn("DEGRADED CONTINUITY MODE", resident)
        self.assertIn("BEGIN DEGRADED CONTINUATION PACKET", detailed)
        self.assertIn("Do not begin a consequential mutation", resident)

    def test_external_engine_terminal_translation_is_bounded(self) -> None:
        module = (ROOT / "modules" / "12_external_engine.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ENGINE-VERIFIED RESULT AVAILABLE", module)
        self.assertIn("does not establish whole-task completion", module)
        self.assertIn("DEGRADED CONTINUITY MODE: true", module)
        self.assertIn("Do not use engine v0.2 as the sole control", module)

    def test_controlled_transition_is_staged_and_evidence_gated(self) -> None:
        module = (ROOT / "modules" / "13_controlled_state_transition.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("identify -> freeze -> describe -> authorize -> stage", module)
        self.assertIn("mechanically verify -> semantically validate", module)
        self.assertIn("conditional commit", module)
        self.assertIn("POSSESSION", module)
        self.assertIn("RECOVERABILITY", module)
        self.assertIn("Recency and trustworthiness are independent", module)
        self.assertIn("Do not destroy information, authority, optionality, or evidence", module)

    def test_age_gate_preserves_user_axes_and_screens_all_results(self) -> None:
        module = (ROOT / "modules" / "14_age_appropriate_gate.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`EMOTIONAL AGE`", module)
        self.assertIn("`INTELLECTUAL AGE`", module)
        self.assertIn("`PHYSICAL AGE`", module)
        self.assertIn("Every candidate result", module)
        self.assertIn("Stage 1 — tri-axis heuristic screen for every result", module)
        self.assertIn("Stage 2 — full difficult-question gate", module)
        self.assertIn("Do not compute a combined score", module)
        self.assertIn("does not replace the design with age prediction", module)
        self.assertIn("factual core, evidence, uncertainty, mission, actor, authority", module)

    def test_age_gate_deployment_assurance_is_fail_closed(self) -> None:
        module = (ROOT / "modules" / "15_age_gate_deployment_assurance.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("AGE-GATE DEPLOYMENT READY: false", module)
        self.assertIn("no-collection-screen", module)
        self.assertIn("AGE DATA COLLECTED: none", module)
        self.assertIn("child-rights impact assessment", module)
        self.assertIn("Do not average these measures into one score", module)
        self.assertIn("raw sensitive conversation text", module)
        self.assertIn("human review", module)
        self.assertIn("appeal", module)
        self.assertIn("rollback", module)

    def test_encrypted_unlock_control_keeps_secrets_out_of_prompt(self) -> None:
        module = (ROOT / "modules" / "16_encrypted_unlock_control.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("authenticated-encryption envelope", module)
        self.assertIn("does not place a plaintext secret", module)
        self.assertIn("deterministic SHA-256", module)
        self.assertIn("atomically reject", module)
        self.assertIn("replay", module)
        self.assertIn("return to `locked`", module)
        self.assertIn("is not a cryptographic implementation", module)

    def test_age_gate_profile_closes_dependencies(self) -> None:
        result = assembler.assemble(
            self.config,
            ["age_gate"],
            [],
            [],
            {"AGE_GATE_STATE": "screen-all"},
        )
        self.assertIn("14_age_appropriate_gate", result.modules)
        self.assertIn("15_age_gate_deployment_assurance", result.modules)
        self.assertIn("16_encrypted_unlock_control", result.modules)
        self.assertIn("02_memory_claims", result.modules)
        self.assertIn("03_mission_actor", result.modules)
        self.assertIn("09_egress_validation", result.modules)
        self.assertIn("AGE GATE STATE: \"screen-all\"", result.text)

    def test_full_profile_contains_age_gate(self) -> None:
        result = assembler.assemble(self.config, ["full"], [], [], {})
        self.assertIn("14_age_appropriate_gate", result.modules)
        self.assertIn("15_age_gate_deployment_assurance", result.modules)
        self.assertIn("16_encrypted_unlock_control", result.modules)
        self.assertIn("AGE_GATE_STATE", result.missing_required_values)

    def test_protected_package_output_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            assembler.resolve_output_path(Path("config.json"), False)
        with self.assertRaises(SystemExit):
            assembler.resolve_output_path(
                Path("parent") / self.config["parent"]["name"], False
            )

    def test_external_output_must_be_new(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "existing.md"
            existing.write_text("preserve", encoding="utf-8")
            with self.assertRaises(SystemExit):
                assembler.resolve_output_path(existing, False)
            self.assertEqual("preserve", existing.read_text(encoding="utf-8"))

    def test_existing_build_requires_explicit_replace(self) -> None:
        with tempfile.TemporaryDirectory(dir=assembler.BUILD_DIR) as directory:
            target = Path(directory) / "generated.md"
            target.write_text("old", encoding="utf-8")
            with self.assertRaises(SystemExit):
                assembler.resolve_output_path(target, False)
            resolved = assembler.resolve_output_path(target, True)
            assembler.write_atomic(resolved, "new\n")
            self.assertEqual("new\n", target.read_text(encoding="utf-8"))
            self.assertEqual(0o644, target.stat().st_mode & 0o777)

if __name__ == "__main__":
    unittest.main()

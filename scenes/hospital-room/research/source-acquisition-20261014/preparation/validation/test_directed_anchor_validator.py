"""Synthetic contract tests only. No hospital model, camera, or render is used."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

import directed_anchor_validator as validator


ROOT = Path(__file__).parent


def example(name="synthetic_upper_visible.json"):
    return validator.load_json(ROOT / "examples" / name)


def png_bytes(width=200, height=120):
    # A tiny, genuine synthetic PNG fixture, generated in memory for header tests.
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress((b"\x00" + b"\x00" * width) * height)) +
            chunk(b"IEND", b""))


class LintTests(unittest.TestCase):
    def assert_issue(self, document, code):
        issues = validator.lint_document(document)
        self.assertIn(code, [item["code"] for item in issues], issues)
        with self.assertRaises(validator.ValidationError):
            validator.score_document(document)

    def test_all_valid_examples_lint(self):
        for path in (ROOT / "examples").glob("synthetic_*.json"):
            with self.subTest(example=path.name):
                self.assertEqual(validator.lint_document(validator.load_json(path)), [])

    def test_wrong_branch_cannot_match_upper_source_to_lower(self):
        self.assert_issue(example("invalid_wrong_branch.json"), "association_mismatch")

    def test_unknown_branch_fails_closed(self):
        doc = example()
        doc["observations"][0]["contour_branch"] = "closest_hull"
        self.assert_issue(doc, "enum")

    def test_wrong_object_cannot_be_selected_automatically(self):
        doc = example()
        doc["projections"][0]["object_id"] = "A_NEARER_UNRELATED_SOFA"
        self.assert_issue(doc, "association_mismatch")

    def test_wrong_semantic_part_fails(self):
        doc = example()
        doc["projections"][0]["semantic_part"] = "seat_front"
        self.assert_issue(doc, "association_mismatch")

    def test_missing_source_dimensions_fails(self):
        doc = example()
        del doc["observations"][0]["source"]["actual_dimensions"]
        self.assert_issue(doc, "required")

    def test_missing_source_sha_fails(self):
        doc = example()
        del doc["observations"][0]["source"]["source_sha256"]
        self.assert_issue(doc, "required")

    def test_malformed_sha_fails(self):
        doc = example()
        doc["observations"][0]["source"]["source_sha256"] = "not-a-sha"
        self.assert_issue(doc, "pattern")

    def test_unknown_frame_fails(self):
        doc = example()
        doc["observations"][0]["source"]["frame_id"] = "UNREGISTERED"
        self.assert_issue(doc, "unknown_frame")

    def test_source_dimension_registry_mismatch_fails(self):
        doc = example()
        doc["observations"][0]["source"]["actual_dimensions"]["width_px"] = 400
        self.assert_issue(doc, "source_registry_mismatch")

    def test_source_hash_registry_mismatch_fails(self):
        doc = example()
        doc["projections"][0]["source"]["source_sha256"] = "0" * 64
        self.assert_issue(doc, "source_registry_mismatch")

    def test_undefined_identity_fails(self):
        for bad in (None, "undefined", "", "assumed", "VERIFIED"):
            with self.subTest(identity=bad):
                doc = example()
                doc["observations"][0]["identity_state"] = bad
                self.assertTrue(validator.lint_document(doc))

    def test_missing_identity_field_fails(self):
        doc = example()
        del doc["observations"][0]["identity_state"]
        self.assert_issue(doc, "required")

    def test_verified_identity_needs_evidence_note(self):
        doc = example()
        doc["observations"][0]["identity_evidence"] = None
        self.assert_issue(doc, "missing_identity_evidence")

    def test_conditional_identity_cannot_authorize_geometry_use(self):
        doc = example()
        doc["observations"][0]["identity_state"] = "conditional"
        self.assert_issue(doc, "unverified_geometry_use")

    def test_non_native_input_rejected_even_if_consistent(self):
        for field, bad in (("coordinate_transform", "resize_0.5"),
                           ("coordinate_transform", "crop"),
                           ("native_decode_status", "preview_decoded"),
                           ("native_decode_status", "unknown"),
                           ("pixel_coordinate_convention", "normalized_uv")):
            with self.subTest(field=field, value=bad):
                doc = example()
                for record in [doc["frames"][0], doc["observations"][0]["source"], doc["projections"][0]["source"]]:
                    record[field] = bad
                self.assert_issue(doc, "const")

    def test_wrong_axis_rejected(self):
        doc = example()
        doc["comparisons"][0]["cross_section_axis"] = "y"
        self.assert_issue(doc, "wrong_cross_section_axis")

    def test_missing_explicit_target_cannot_search_nearest(self):
        doc = example()
        doc["comparisons"][0]["projection_id"] = "pick_the_closest"
        self.assert_issue(doc, "unknown_target")

    def test_shading_cannot_be_physical_vertex(self):
        doc = example()
        record = doc["observations"][0]
        record.update(evidence_kind="soft_shading", contour_branch="physical_vertex")
        self.assert_issue(doc, "evidence_branch_mismatch")
        record["contour_branch"] = "soft_shading"
        self.assert_issue(doc, "shading_is_not_geometry")

    def test_shading_may_be_kept_as_non_geometric_annotation(self):
        doc = example()
        doc["observations"][0].update(evidence_kind="soft_shading", contour_branch="soft_shading", geometry_use_allowed=False)
        doc["projections"] = []
        doc["comparisons"] = []
        self.assertEqual(validator.lint_document(doc), [])

    def test_silhouette_sample_order_does_not_authorize_3d_point(self):
        doc = example()
        doc["observations"][0]["point_identity"] = {"state": "verified", "physical_point_id": "vertex_0", "evidence": "Same sample index in another frame."}
        self.assert_issue(doc, "unverified_point_identity")

    def test_unasserted_point_cannot_smuggle_physical_point_id(self):
        doc = example()
        doc["observations"][0]["point_identity"]["physical_point_id"] = "vertex_0"
        self.assert_issue(doc, "implicit_point_identity")

    def test_physical_vertex_needs_verified_point_identity(self):
        doc = example()
        doc["observations"][0].update(evidence_kind="physical_vertex", contour_branch="physical_vertex")
        doc["projections"] = []
        doc["comparisons"] = []
        self.assert_issue(doc, "vertex_requires_identity")

    def test_duplicate_ids_fail(self):
        doc = example()
        doc["observations"].append(copy.deepcopy(doc["observations"][0]))
        self.assert_issue(doc, "duplicate_id")

    def test_segment_visibility_count_must_match_vertices(self):
        doc = example()
        doc["projections"][0]["polylines"][0]["segment_visibility"] = []
        self.assert_issue(doc, "min_items")
        doc["projections"][0]["polylines"][0]["segment_visibility"] = ["visible", "visible"]
        self.assert_issue(doc, "segment_array_length")

    def test_duplicate_segment_ids_fail(self):
        doc = example()
        line = doc["projections"][0]["polylines"][0]
        line.update(vertices_xy=[[10,20],[50,20],[90,20]], segment_ids=["repeat", "repeat"], segment_visibility=["visible", "visible"])
        self.assert_issue(doc, "duplicate_segment_id")

    def test_degenerate_segment_fails(self):
        doc = example()
        doc["projections"][0]["polylines"][0]["vertices_xy"] = [[10,20], [10,20]]
        self.assert_issue(doc, "degenerate_segment")

    def test_nonfinite_and_boolean_numbers_fail(self):
        for value in (float("nan"), float("inf"), True):
            with self.subTest(value=value):
                doc = example()
                doc["observations"][0]["source_xy"][0] = value
                self.assert_issue(doc, "type")

    def test_extreme_coordinates_fail_without_overflow(self):
        doc = example()
        doc["observations"][0]["source_xy"][0] = 10 ** 1000
        self.assert_issue(doc, "maximum")

    def test_nonpositive_uncertainty_fails(self):
        for uncertainty in (0, -1):
            doc = example()
            doc["observations"][0]["uncertainty_px"] = uncertainty
            self.assert_issue(doc, "minimum")

    def test_source_point_must_be_inside_native_dimensions(self):
        doc = example()
        doc["observations"][0]["source_xy"] = [200, 10]
        self.assert_issue(doc, "source_point_out_of_bounds")

    def test_unknown_fallback_field_fails(self):
        doc = example()
        doc["comparisons"][0]["fallback"] = "nearest_hull"
        self.assert_issue(doc, "unknown_field")

    def test_euclidean_requires_verified_physical_edge(self):
        doc = example()
        doc["comparisons"][0].update(method="named_segment_distance", cross_section_axis=None, segment_id="upper_segment")
        self.assert_issue(doc, "physical_edge_identity_required")

    def test_named_segment_must_be_explicit_and_exist(self):
        for name in (None, "nearest", "some_other_segment"):
            doc = example("synthetic_named_physical_edge.json")
            doc["comparisons"][0]["segment_id"] = name
            self.assert_issue(doc, "unknown_named_segment")


class ScoreTests(unittest.TestCase):
    def first(self, doc):
        return validator.score_document(doc)["rows"][0]

    def test_upper_error_is_directed_y_residual(self):
        report = validator.score_document(example())
        row = report["rows"][0]
        self.assertEqual(row["residual_px"], -2)
        self.assertEqual(row["target_xy"], [50,20])
        self.assertEqual(row["error_over_declared_uncertainty"], -1)
        self.assertEqual(report["status"], validator.DIAGNOSTIC)
        self.assertEqual(report["model_validation"], "not_performed")
        self.assertEqual(report["groups"][0]["diagnostic_type"], validator.DIAGNOSTIC)
        self.assertEqual(report["source_verification"]["mode"], "metadata_consistency_only")

    def test_closer_lower_edge_is_never_considered(self):
        doc = example()
        lower = copy.deepcopy(doc["projections"][0])
        lower.update(projection_id="NEARER_LOWER_EDGE", contour_branch="lower")
        lower["polylines"][0]["vertices_xy"] = [[10,22], [90,22]]
        doc["projections"].append(lower)
        self.assertEqual(self.first(doc)["residual_px"], -2)
        self.assertEqual(self.first(doc)["projection_id"], "SYNTHETIC_A_SOFA_UPPER")

    def test_full_hull_smuggled_as_upper_is_ambiguous_and_rejected(self):
        doc = example()
        line = doc["projections"][0]["polylines"][0]
        line.update(vertices_xy=[[10,20], [90,20], [90,22], [10,22], [10,20]],
                    segment_ids=["top", "right", "bottom", "left"], segment_visibility=["visible"] * 4)
        self.assertEqual(self.first(doc)["reason"], "ambiguous_multiple_visible_intersections")

    def test_outside_support_is_rejected_without_endpoint_fallback(self):
        doc = example()
        doc["observations"][0]["source_xy"] = [100,22]
        row = self.first(doc)
        self.assertEqual(row["reason"], "unsupported_cross_section")
        self.assertNotIn("residual_px", row)
        self.assertNotIn("target_xy", row)

    def test_just_outside_support_is_not_admitted_by_tolerance(self):
        doc = example()
        doc["observations"][0]["source_xy"] = [90 + 1e-10,22]
        self.assertEqual(self.first(doc)["reason"], "unsupported_cross_section")

    def test_support_endpoint_is_included(self):
        doc = example()
        doc["observations"][0]["source_xy"] = [90,22]
        self.assertEqual(self.first(doc)["residual_px"], -2)

    def test_partial_occlusion_only_counts_visible_segments(self):
        report = validator.score_document(example("synthetic_partial_occlusion.json"))
        self.assertEqual(report["counts"], {"requested":5, "scored":2, "rejected":2, "excluded":1})
        self.assertEqual(report["rows"][1]["reason"], "unsupported_visible_cross_section")
        self.assertEqual(report["rows"][3]["reason"], "unsupported_cross_section")
        self.assertEqual(report["rows"][4]["reason"], "source_sample_not_visible")
        self.assertEqual(report["groups"][0]["statistics"]["mean_residual_px"], -3.5)
        self.assertEqual(report["groups"][0]["statistics"]["max_absolute_error_px"], 5)

    def test_unknown_segment_visibility_not_scored(self):
        doc = example()
        doc["projections"][0]["polylines"][0]["segment_visibility"] = ["unknown"]
        self.assertEqual(self.first(doc)["reason"], "unsupported_visible_cross_section")

    def test_occluded_nearer_segment_not_scored(self):
        doc = example()
        hidden = {"polyline_id":"occluded_part", "vertices_xy":[[10,22],[90,22]], "segment_ids":["hidden"], "segment_visibility":["occluded"]}
        doc["projections"][0]["polylines"].append(hidden)
        self.assertEqual(self.first(doc)["residual_px"], -2)
        self.assertEqual(self.first(doc)["matched_segment_ids"], ["upper_segment"])

    def test_disjoint_visible_runs_are_not_bridged(self):
        doc = example()
        doc["projections"][0]["polylines"] = [
            {"polyline_id":"left_run", "vertices_xy":[[10,20],[30,20]], "segment_ids":["left"], "segment_visibility":["visible"]},
            {"polyline_id":"right_run", "vertices_xy":[[70,20],[90,20]], "segment_ids":["right"], "segment_visibility":["visible"]},
        ]
        self.assertEqual(self.first(doc)["reason"], "unsupported_cross_section")

    def test_source_unknown_visibility_is_excluded(self):
        doc = example()
        doc["observations"][0]["visibility"] = "unknown"
        self.assertEqual(self.first(doc)["reason"], "source_sample_not_visible")

    def test_conditional_and_unresolved_identity_are_excluded(self):
        for identity in ("conditional", "unresolved"):
            doc = example()
            doc["observations"][0].update(identity_state=identity, geometry_use_allowed=False)
            self.assertEqual(self.first(doc)["reason"], "identity_not_verified")

    def test_explicit_geometry_exclusion_is_respected(self):
        doc = example()
        doc["observations"][0]["geometry_use_allowed"] = False
        self.assertEqual(self.first(doc)["reason"], "geometry_use_not_allowed")

    def test_left_and_right_use_x_residual_at_fixed_y(self):
        for branch in ("left", "right"):
            doc = example()
            for record in [doc["observations"][0], doc["projections"][0]]:
                record["contour_branch"] = branch
            doc["observations"][0]["source_xy"] = [23,50]
            doc["projections"][0]["polylines"][0]["vertices_xy"] = [[20,10],[20,90]]
            doc["comparisons"][0]["cross_section_axis"] = "y"
            row = self.first(doc)
            self.assertEqual(row["residual_px"], -3)
            self.assertEqual(row["target_xy"], [20,50])

    def test_lower_branch_is_available_only_when_explicitly_named(self):
        doc = example()
        for record in [doc["observations"][0], doc["projections"][0]]:
            record["contour_branch"] = "lower"
        self.assertEqual(self.first(doc)["residual_px"], -2)

    def test_sloped_polyline_interpolates_at_source_cross_section(self):
        doc = example()
        doc["projections"][0]["polylines"][0]["vertices_xy"] = [[10,10],[90,30]]
        self.assertEqual(self.first(doc)["target_xy"], [50,20])

    def test_adjacent_shared_vertex_is_not_double_counted(self):
        doc = example()
        line = doc["projections"][0]["polylines"][0]
        line.update(vertices_xy=[[10,10],[50,20],[90,30]], segment_ids=["a","b"], segment_visibility=["visible","visible"])
        row = self.first(doc)
        self.assertEqual(row["status"], "scored")
        self.assertEqual(row["matched_segment_ids"], ["a","b"])
        self.assertEqual(validator.score_document(doc)["counts"]["scored"], 1)

    def test_collinear_cross_section_is_rejected(self):
        doc = example()
        doc["projections"][0]["polylines"][0]["vertices_xy"] = [[50,10],[50,30]]
        self.assertEqual(self.first(doc)["reason"], "ambiguous_collinear_cross_section")

    def test_same_sample_order_in_two_frames_has_no_point_correspondence(self):
        doc = example()
        frame = copy.deepcopy(doc["frames"][0])
        frame.update(frame_id="SYNTHETIC_B", source_filename="SYNTHETIC_B_NOT_A_REAL_SOURCE.png", source_sha256="b" * 64)
        doc["frames"].append(frame)
        observation = copy.deepcopy(doc["observations"][0])
        observation.update(observation_id="frame_b_sample_0", source=copy.deepcopy(frame))
        doc["observations"].append(observation)
        projection = copy.deepcopy(doc["projections"][0])
        projection.update(projection_id="SYNTHETIC_B_SOFA_UPPER", source=copy.deepcopy(frame))
        doc["projections"].append(projection)
        comparison = copy.deepcopy(doc["comparisons"][0])
        comparison.update(comparison_id="frame_b_comparison", observation_id=observation["observation_id"], projection_id=projection["projection_id"])
        doc["comparisons"].append(comparison)
        report = validator.score_document(doc)
        self.assertEqual(len(report["groups"]), 2)
        self.assertTrue(report["no_3d_point_correspondence_inferred"])
        self.assertEqual(doc["observations"][0]["sample_order"], doc["observations"][1]["sample_order"])
        self.assertTrue(all(o["point_identity"]["state"] == "not_asserted" for o in doc["observations"]))

    def test_verified_named_edge_euclidean_distance(self):
        row = self.first(example("synthetic_named_physical_edge.json"))
        self.assertEqual(row["residual_px"], 6)
        self.assertEqual(row["target_xy"], [10,40])

    def test_named_edge_does_not_choose_another_nearer_edge(self):
        doc = example("synthetic_named_physical_edge.json")
        doc["projections"][0]["polylines"].append({"polyline_id":"closer_edge", "vertices_xy":[[16,10],[16,90]], "segment_ids":["closer"], "segment_visibility":["visible"]})
        self.assertEqual(self.first(doc)["residual_px"], 6)

    def test_named_edge_endpoint_clamp_is_explicit_finite_segment_behavior(self):
        doc = example("synthetic_named_physical_edge.json")
        doc["observations"][0]["source_xy"] = [16,98]
        row = self.first(doc)
        self.assertEqual(row["residual_px"], 10)
        self.assertEqual(row["target_xy"], [10,90])
        self.assertEqual(row["segment_parameter"], 1)

    def test_named_occluded_edge_is_rejected(self):
        doc = example("synthetic_named_physical_edge.json")
        doc["projections"][0]["polylines"][0]["segment_visibility"] = ["occluded"]
        self.assertEqual(self.first(doc)["reason"], "named_segment_not_visible")

    def test_physical_edge_can_use_explicit_directed_axis(self):
        doc = example("synthetic_named_physical_edge.json")
        doc["comparisons"][0].update(method="directed_cross_section", cross_section_axis="y", segment_id=None)
        self.assertEqual(self.first(doc)["residual_px"], -6)

    def test_all_excluded_produces_no_statistics(self):
        doc = example()
        doc["observations"][0]["visibility"] = "occluded"
        report = validator.score_document(doc)
        self.assertIsNone(report["groups"][0]["statistics"])
        self.assertEqual(report["counts"]["scored"], 0)

    def test_scoring_does_not_mutate_input(self):
        doc = example()
        before = copy.deepcopy(doc)
        validator.score_document(doc)
        self.assertEqual(before, doc)


class SourceFileAndCliTests(unittest.TestCase):
    def with_source(self, directory):
        doc = example()
        data = png_bytes()
        path = Path(directory) / doc["frames"][0]["source_filename"]
        path.write_bytes(data)
        for source in [doc["frames"][0], doc["observations"][0]["source"], doc["projections"][0]["source"]]:
            source["source_sha256"] = hashlib.sha256(data).hexdigest()
        return doc, path

    def test_optional_png_hash_and_dimensions_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            doc, _ = self.with_source(directory)
            errors, checked = validator.verify_source_files(doc, directory)
            self.assertEqual(errors, [])
            self.assertEqual(checked["checked_frame_ids"], ["SYNTHETIC_A"])
            self.assertFalse(checked["native_pixel_decode_independently_verified"])
            report = validator.score_document(doc, directory)
            self.assertEqual(report["source_verification"]["mode"], "sha256_and_png_jpeg_header_dimensions")

    def test_actual_source_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            doc, path = self.with_source(directory)
            path.write_bytes(path.read_bytes() + b"changed")
            with self.assertRaises(validator.ValidationError) as raised:
                validator.score_document(doc, directory)
            self.assertEqual(raised.exception.issues[0]["code"], "source_hash_mismatch")

    def test_actual_source_dimension_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            doc, _ = self.with_source(directory)
            for source in [doc["frames"][0], doc["observations"][0]["source"], doc["projections"][0]["source"]]:
                source["actual_dimensions"]["width_px"] = 201
            with self.assertRaises(validator.ValidationError) as raised:
                validator.score_document(doc, directory)
            self.assertEqual(raised.exception.issues[0]["code"], "source_dimensions_mismatch")

    def test_missing_source_is_not_reported_as_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(validator.ValidationError) as raised:
                validator.score_document(example(), directory)
            self.assertEqual(raised.exception.issues[0]["code"], "source_file_unverified")

    def test_jpeg_header_dimensions_are_only_a_header_check(self):
        payload = b"\x08" + struct.pack(">HH", 120, 200) + b"\x01\x01\x11\x00"
        data = b"\xff\xd8\xff\xc0" + struct.pack(">H", len(payload) + 2) + payload + b"\xff\xd9"
        self.assertEqual(validator._image_dimensions(data), (200,120))

    def test_truncated_and_unsupported_headers_fail(self):
        for data in (b"", b"not an image", b"\xff\xd8\xff\xc0\x00\x09"):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    validator._image_dimensions(data)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text('{"schema_version":"1.0","schema_version":"2.0"}')
            with self.assertRaises(ValueError):
                validator.load_json(path)

    def cli(self, command, name):
        result = subprocess.run([sys.executable, str(ROOT / "directed_anchor_validator.py"), command, str(ROOT / "examples" / name)], text=True, capture_output=True)
        return result.returncode, json.loads(result.stdout)

    def test_cli_lint_success(self):
        code, report = self.cli("lint", "synthetic_upper_visible.json")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "metadata_lint_ok")

    def test_cli_score_does_lint_first_and_rejects_wrong_branch(self):
        code, report = self.cli("score", "invalid_wrong_branch.json")
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "input_rejected")
        self.assertNotIn("rows", report)

    def test_cli_score_success_is_only_conditional_diagnostic(self):
        code, report = self.cli("score", "synthetic_upper_visible.json")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], validator.DIAGNOSTIC)

    def test_cli_partial_rejection_has_nonzero_exit_and_visible_scores(self):
        code, report = self.cli("score", "synthetic_partial_occlusion.json")
        self.assertEqual(code, 3)
        self.assertEqual(report["counts"]["scored"], 2)
        self.assertEqual(report["counts"]["rejected"], 2)


if __name__ == "__main__":
    unittest.main()

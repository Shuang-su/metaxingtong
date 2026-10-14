#!/usr/bin/env python3
"""Fail-closed metadata lint and named-branch screen-space diagnostics.

Only the Python standard library is used. This module never fits cameras, loads
meshes, renders, selects objects, builds hulls, or infers 3D correspondences.
The adjacent JSON Schema defines the structural contract; lint_document adds
association/semantic checks that JSON Schema alone cannot express.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import struct
import sys


SCHEMA_PATH = Path(__file__).with_name("anchor_input.schema.json")
DIAGNOSTIC = "conditional_screen_space_diagnostic"
EPSILON_PX = 1e-9  # Arithmetic tolerance only, never expanded image support.
BRANCH_AXIS = {"upper": "x", "lower": "x", "left": "y", "right": "y"}
SOURCE_FIELDS = (
    "frame_id", "source_sha256", "source_filename", "actual_dimensions",
    "coordinate_transform", "native_decode_status", "pixel_coordinate_convention",
)


class ValidationError(ValueError):
    def __init__(self, issues):
        self.issues = issues
        super().__init__("; ".join(f"{i['path']}: {i['message']}" for i in issues))


def issue(code, path, message):
    return {"code": code, "path": path, "message": message}


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    with open(path, encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=_reject_duplicate_keys,
                         parse_constant=reject_constant)


def _type_matches(value, kind):
    return {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "boolean": lambda: type(value) is bool,
        "integer": lambda: type(value) is int,
        "number": lambda: type(value) is int or (type(value) is float and math.isfinite(value)),
        "null": lambda: value is None,
    }[kind]()


def _validate_structure(value, schema, root, path, errors):
    """Small validator for the exact keyword subset in our shipped schema.

    This is intentionally not advertised as a general JSON Schema engine.
    A conventional Draft 2020-12 validator may also validate the schema file.
    """
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise RuntimeError(f"Unsupported schema reference: {ref}")
        return _validate_structure(value, root["$defs"][ref.split("/")[-1]], root, path, errors)
    kinds = schema.get("type")
    if kinds is not None:
        kinds = kinds if isinstance(kinds, list) else [kinds]
        if not any(_type_matches(value, kind) for kind in kinds):
            errors.append(issue("type", path, f"Expected {' or '.join(kinds)}."))
            return
    if "const" in schema and value != schema["const"]:
        errors.append(issue("const", path, f"Must equal {schema['const']!r}."))
    if "enum" in schema and value not in schema["enum"]:
        errors.append(issue("enum", path, f"Must be one of {schema['enum']!r}."))
    if isinstance(value, dict):
        for field in schema.get("required", []):
            if field not in value:
                errors.append(issue("required", f"{path}.{field}", "Required field is missing."))
        properties = schema.get("properties", {})
        for field, item in value.items():
            if field in properties:
                _validate_structure(item, properties[field], root, f"{path}.{field}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(issue("unknown_field", f"{path}.{field}", "Unknown field is forbidden."))
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(issue("min_items", path, "Too few items."))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(issue("max_items", path, "Too many items."))
        for index, item in enumerate(value):
            if "items" in schema:
                _validate_structure(item, schema["items"], root, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            errors.append(issue("min_length", path, "Must contain non-whitespace text."))
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(issue("pattern", path, "Does not match the required format."))
    elif type(value) in (int, float):
        if type(value) is float and not math.isfinite(value):
            errors.append(issue("finite", path, "Number must be finite."))
        elif "minimum" in schema and value < schema["minimum"]:
            errors.append(issue("minimum", path, f"Must be at least {schema['minimum']}."))
        elif "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(issue("exclusive_minimum", path, f"Must exceed {schema['exclusiveMinimum']}."))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(issue("maximum", path, f"Must be at most {schema['maximum']}."))


def _index_unique(items, field, path, errors):
    result = {}
    for index, item in enumerate(items):
        name = item[field]
        if name in result:
            errors.append(issue("duplicate_id", f"{path}[{index}].{field}", f"Duplicate ID {name!r}."))
        result[name] = item
    return result


def _semantic_identity(record, path, errors):
    evidence = record["evidence_kind"]
    branch = record["contour_branch"]
    if evidence == "silhouette":
        allowed = set(BRANCH_AXIS)
    else:
        allowed = {evidence}
    if branch not in allowed:
        errors.append(issue("evidence_branch_mismatch", path, "Evidence kind and contour branch disagree."))
    if record["identity_state"] in {"verified", "conditional"} and not record["identity_evidence"]:
        errors.append(issue("missing_identity_evidence", path + ".identity_evidence", "Identified records require an explicit evidence note."))
    if record["identity_evidence"] is not None and not record["identity_evidence"].strip():
        errors.append(issue("empty_identity_evidence", path + ".identity_evidence", "Evidence must not be blank."))
    if record["geometry_use_allowed"] and record["identity_state"] != "verified":
        errors.append(issue("unverified_geometry_use", path, "Conditional or unresolved identity cannot authorize geometry use."))
    if evidence == "soft_shading" and record["geometry_use_allowed"]:
        errors.append(issue("shading_is_not_geometry", path, "Soft shading is not a physical edge or vertex and cannot authorize geometry use."))


def lint_document(document):
    """Return all structural issues, or semantic issues if structure is valid.

    Native decoding and identity evidence remain human/upstream assertions.
    Optional source-file checks in verify_source_files check bytes and headers,
    not native decoding, physical identity, or whether the 3D model is correct.
    """
    errors = []
    schema = load_json(SCHEMA_PATH)
    _validate_structure(document, schema, schema, "$", errors)
    if errors:
        return errors
    frames = _index_unique(document["frames"], "frame_id", "$.frames", errors)
    observations = _index_unique(document["observations"], "observation_id", "$.observations", errors)
    projections = _index_unique(document["projections"], "projection_id", "$.projections", errors)
    _index_unique(document["comparisons"], "comparison_id", "$.comparisons", errors)
    for group in ("observations", "projections"):
        for index, record in enumerate(document[group]):
            path = f"$.{group}[{index}]"
            _semantic_identity(record, path, errors)
            source = record["source"]
            frame = frames.get(source["frame_id"])
            if frame is None:
                errors.append(issue("unknown_frame", path + ".source.frame_id", "Frame has no registry entry."))
            elif any(source[key] != frame[key] for key in SOURCE_FIELDS):
                errors.append(issue("source_registry_mismatch", path + ".source", "All source metadata must exactly match the frame registry."))
    for index, observation in enumerate(document["observations"]):
        path = f"$.observations[{index}]"
        x, y = observation["source_xy"]
        dimensions = observation["source"]["actual_dimensions"]
        if not (0 <= x < dimensions["width_px"] and 0 <= y < dimensions["height_px"]):
            errors.append(issue("source_point_out_of_bounds", path + ".source_xy", "Point is outside native source image bounds."))
        point = observation["point_identity"]
        if point["state"] == "not_asserted":
            if point["physical_point_id"] is not None or point["evidence"] is not None:
                errors.append(issue("implicit_point_identity", path + ".point_identity", "An unasserted 3D point identity must have null ID and evidence."))
        elif (observation["evidence_kind"] != "physical_vertex" or
              observation["identity_state"] != "verified" or
              not point["physical_point_id"] or not point["evidence"]):
            errors.append(issue("unverified_point_identity", path + ".point_identity", "Only an explicitly verified physical vertex with evidence may assert a 3D point ID."))
        if observation["evidence_kind"] == "physical_vertex" and point["state"] != "verified":
            errors.append(issue("vertex_requires_identity", path, "A physical vertex requires separately verified point identity; sample order is insufficient."))
        for name in ("physical_point_id", "evidence"):
            if point[name] is not None and not point[name].strip():
                errors.append(issue("empty_point_identity", path + ".point_identity." + name, "Must not be blank."))
    for index, projection in enumerate(document["projections"]):
        path = f"$.projections[{index}]"
        _index_unique(projection["polylines"], "polyline_id", path + ".polylines", errors)
        used_segments = set()
        for line_index, line in enumerate(projection["polylines"]):
            line_path = f"{path}.polylines[{line_index}]"
            count = len(line["vertices_xy"]) - 1
            if len(line["segment_ids"]) != count or len(line["segment_visibility"]) != count:
                errors.append(issue("segment_array_length", line_path, "Exactly one segment ID and visibility label are required per consecutive vertex pair."))
            for segment_id in line["segment_ids"]:
                if segment_id in used_segments:
                    errors.append(issue("duplicate_segment_id", line_path, "Segment IDs must be unique within the named projection."))
                used_segments.add(segment_id)
            for start, end in zip(line["vertices_xy"], line["vertices_xy"][1:]):
                if math.dist(start, end) <= EPSILON_PX:
                    errors.append(issue("degenerate_segment", line_path, "Zero-length or numerically degenerate segments are forbidden."))
    for index, comparison in enumerate(document["comparisons"]):
        path = f"$.comparisons[{index}]"
        observation = observations.get(comparison["observation_id"])
        projection = projections.get(comparison["projection_id"])
        if observation is None or projection is None:
            errors.append(issue("unknown_target", path, "Both observation_id and projection_id must name existing records; automatic selection is forbidden."))
            continue
        for key in ("object_id", "semantic_part", "contour_branch", "evidence_kind", "source"):
            if observation[key] != projection[key]:
                errors.append(issue("association_mismatch", path + "." + key, "Source and projection must have exactly matching frame, object, part, branch, and evidence type."))
        if comparison["method"] == "directed_cross_section":
            if comparison["segment_id"] is not None:
                errors.append(issue("unexpected_segment", path, "Directed branch comparisons do not choose a nearest named segment."))
            branch = observation["contour_branch"]
            expected_axis = BRANCH_AXIS.get(branch)
            if expected_axis is None and branch != "physical_edge":
                errors.append(issue("unsupported_branch", path, "Only a named silhouette branch or physical edge supports directed cross-section diagnostics."))
            if comparison["cross_section_axis"] is None or (expected_axis and comparison["cross_section_axis"] != expected_axis):
                errors.append(issue("wrong_cross_section_axis", path, "upper/lower require fixed x; left/right require fixed y; physical_edge requires an explicit axis."))
        else:
            if comparison["cross_section_axis"] is not None:
                errors.append(issue("unexpected_axis", path, "Named-segment Euclidean distance requires null cross_section_axis."))
            if (observation["evidence_kind"] != "physical_edge" or
                    projection["evidence_kind"] != "physical_edge" or
                    observation["identity_state"] != "verified" or
                    projection["identity_state"] != "verified"):
                errors.append(issue("physical_edge_identity_required", path, "Euclidean distance is allowed only for an explicitly verified physical_edge identity on both sides."))
            segment_ids = {sid for line in projection["polylines"] for sid in line["segment_ids"]}
            if comparison["segment_id"] not in segment_ids:
                errors.append(issue("unknown_named_segment", path + ".segment_id", "Name an existing physical-edge segment explicitly; automatic nearest-segment selection is forbidden."))
    # A repeated physical_point_id must denote the same named physical feature.
    points = {}
    for index, observation in enumerate(document["observations"]):
        point = observation["point_identity"]
        if point["state"] != "verified":
            continue
        name = point["physical_point_id"]
        identity = (observation["object_id"], observation["semantic_part"], observation["evidence_kind"])
        if name in points and points[name] != identity:
            errors.append(issue("conflicting_point_identity", f"$.observations[{index}].point_identity", "The same physical point ID cannot name different objects or semantic parts."))
        points[name] = identity
    return errors


def _image_dimensions(data):
    """Read PNG/JPEG dimensions without claiming to decode pixels."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33:
        if data[12:16] != b"IHDR" or struct.unpack(">I", data[8:12])[0] != 13:
            raise ValueError("Invalid PNG IHDR.")
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        offset = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while offset < len(data):
            if data[offset] != 0xFF:
                raise ValueError("Invalid JPEG marker boundary.")
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in {0xD9, 0xDA}:
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            if offset + 2 > len(data):
                break
            length = struct.unpack(">H", data[offset:offset + 2])[0]
            if length < 2 or offset + length > len(data):
                raise ValueError("Truncated JPEG segment.")
            if marker in sof:
                if length < 8:
                    raise ValueError("Invalid JPEG SOF.")
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return width, height
            offset += length
    raise ValueError("Unsupported or malformed image header; only PNG/JPEG header checks are implemented.")


def verify_source_files(document, source_root):
    """Optional byte/hash/header checks; never certifies native pixel decoding."""
    root = Path(source_root).resolve()
    errors, checked = [], []
    for index, frame in enumerate(document["frames"]):
        path = f"$.frames[{index}]"
        file_path = root / frame["source_filename"]
        try:
            resolved = file_path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                raise ValueError("Source filename escapes the specified source root.")
            data = resolved.read_bytes()
            if hashlib.sha256(data).hexdigest() != frame["source_sha256"]:
                errors.append(issue("source_hash_mismatch", path, "Actual file bytes do not match the declared SHA-256."))
                continue
            width, height = _image_dimensions(data)
            if {"width_px": width, "height_px": height} != frame["actual_dimensions"]:
                errors.append(issue("source_dimensions_mismatch", path, "Actual image-header dimensions do not match declared dimensions."))
                continue
            checked.append(frame["frame_id"])
        except (OSError, ValueError) as error:
            errors.append(issue("source_file_unverified", path, str(error)))
    return errors, {"mode": "sha256_and_png_jpeg_header_dimensions", "checked_frame_ids": checked,
                    "native_pixel_decode_independently_verified": False}


def _segments(projection):
    for line in projection["polylines"]:
        for index, (start, end) in enumerate(zip(line["vertices_xy"], line["vertices_xy"][1:])):
            yield line["segment_ids"][index], start, end, line["segment_visibility"][index]


def _directed_cross_section(source_xy, projection, axis):
    fixed = 0 if axis == "x" else 1
    variable = 1 - fixed
    coordinate = source_xy[fixed]
    intersections = []
    hidden_support = False
    for segment_id, start, end, visibility in _segments(projection):
        # Deliberately no tolerance here: even slightly out-of-support is rejected.
        if not min(start[fixed], end[fixed]) <= coordinate <= max(start[fixed], end[fixed]):
            continue
        if visibility != "visible":
            hidden_support = True
            continue
        delta = end[fixed] - start[fixed]
        if delta == 0:
            return {"status": "rejected", "reason": "ambiguous_collinear_cross_section", "segment_id": segment_id}
        t = (coordinate - start[fixed]) / delta
        target = [start[i] + t * (end[i] - start[i]) for i in range(2)]
        intersections.append((target, segment_id))
    if not intersections:
        return {"status": "rejected", "reason": "unsupported_visible_cross_section" if hidden_support else "unsupported_cross_section"}
    first = intersections[0][0]
    if any(math.dist(first, target) > EPSILON_PX for target, _ in intersections[1:]):
        return {"status": "rejected", "reason": "ambiguous_multiple_visible_intersections"}
    residual = first[variable] - source_xy[variable]
    return {"status": "scored", "target_xy": first, "residual_px": residual,
            "matched_segment_ids": [segment for _, segment in intersections],
            "residual_sign_convention": "projected_y_minus_source_y" if axis == "x" else "projected_x_minus_source_x"}


def _named_segment_distance(source_xy, projection, segment_id):
    for name, start, end, visibility in _segments(projection):
        if name != segment_id:
            continue
        if visibility != "visible":
            return {"status": "rejected", "reason": "named_segment_not_visible"}
        vector = [end[i] - start[i] for i in range(2)]
        length_squared = sum(value * value for value in vector)
        t = sum((source_xy[i] - start[i]) * vector[i] for i in range(2)) / length_squared
        # Clamping applies to this explicitly named finite segment only.
        t = max(0.0, min(1.0, t))
        target = [start[i] + t * vector[i] for i in range(2)]
        return {"status": "scored", "target_xy": target,
                "residual_px": math.dist(source_xy, target),
                "matched_segment_ids": [name], "segment_parameter": t,
                "residual_sign_convention": "unsigned_named_finite_segment_euclidean_distance"}
    raise AssertionError("Lint must verify the named segment before scoring.")


def score_document(document, source_root=None):
    """Lint first, then diagnose only explicitly authorized named associations."""
    errors = lint_document(document)
    source_check = {"mode": "metadata_consistency_only", "checked_frame_ids": [],
                    "native_pixel_decode_independently_verified": False}
    if not errors and source_root is not None:
        errors, source_check = verify_source_files(document, source_root)
    if errors:
        raise ValidationError(errors)
    observations = {x["observation_id"]: x for x in document["observations"]}
    projections = {x["projection_id"]: x for x in document["projections"]}
    rows = []
    grouped = defaultdict(list)
    for comparison in document["comparisons"]:
        observation = observations[comparison["observation_id"]]
        projection = projections[comparison["projection_id"]]
        row = {"comparison_id": comparison["comparison_id"],
               "observation_id": observation["observation_id"],
               "projection_id": projection["projection_id"],
               "source_xy": observation["source_xy"],
               "uncertainty_px": observation["uncertainty_px"],
               "diagnostic_type": DIAGNOSTIC}
        if observation["visibility"] != "visible":
            result = {"status": "excluded", "reason": "source_sample_not_visible"}
        elif observation["identity_state"] != "verified" or projection["identity_state"] != "verified":
            result = {"status": "excluded", "reason": "identity_not_verified"}
        elif not observation["geometry_use_allowed"] or not projection["geometry_use_allowed"]:
            result = {"status": "excluded", "reason": "geometry_use_not_allowed"}
        elif comparison["method"] == "directed_cross_section":
            result = _directed_cross_section(observation["source_xy"], projection, comparison["cross_section_axis"])
        else:
            result = _named_segment_distance(observation["source_xy"], projection, comparison["segment_id"])
        row.update(result)
        if result["status"] == "scored":
            row["absolute_error_px"] = abs(result["residual_px"])
            row["error_over_declared_uncertainty"] = result["residual_px"] / observation["uncertainty_px"]
        rows.append(row)
        key = (observation["source"]["frame_id"], observation["object_id"],
               observation["semantic_part"], observation["contour_branch"],
               projection["projection_id"], comparison["method"], comparison["cross_section_axis"])
        grouped[key].append(row)
    groups = []
    for key, members in sorted(grouped.items(), key=lambda item: repr(item[0])):
        residuals = [r["residual_px"] for r in members if r["status"] == "scored"]
        counts = Counter(r["status"] for r in members)
        summary = dict(zip(("frame_id", "object_id", "semantic_part", "contour_branch", "projection_id", "method", "cross_section_axis"), key))
        summary.update({"diagnostic_type": DIAGNOSTIC, "requested_count": len(members),
                        "scored_count": counts["scored"], "rejected_count": counts["rejected"],
                        "excluded_count": counts["excluded"],
                        "statistics": None if not residuals else {
                            "mean_residual_px": statistics.fmean(residuals),
                            "median_absolute_error_px": statistics.median(abs(r) for r in residuals),
                            "max_absolute_error_px": max(abs(r) for r in residuals),
                            "rms_error_px": math.sqrt(statistics.fmean(r * r for r in residuals)),
                        }})
        groups.append(summary)
    counts = Counter(row["status"] for row in rows)
    return {"status": DIAGNOSTIC, "input_dataset_id": document["dataset_id"],
            "dataset_kind": document["dataset_kind"], "lint_ok": True,
            "source_verification": source_check, "model_validation": "not_performed",
            "no_3d_point_correspondence_inferred": True,
            "counts": {"requested": len(rows), "scored": counts["scored"],
                       "rejected": counts["rejected"], "excluded": counts["excluded"]},
            "rows": rows, "groups": groups,
            "limitations": [
                "All statistics are conditional_screen_space_diagnostic only, never a model pass or model validation.",
                "Native decoding, branch labels, object identity, visibility, and geometry-use permission are supplied assertions; lint does not prove them.",
                "No cross-frame or 3D correspondence follows from sample order, proximity, or a small residual.",
                "No camera or geometry fitting, rendering, hull fallback, nearest-object selection, or occlusion inference is performed.",
                "Uncertainty is a declared pixel scale, not an estimated variance; normalized errors have no asserted statistical significance.",
            ]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("lint", "score"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--source-root", type=Path, help="Also verify source bytes' SHA-256 and PNG/JPEG header dimensions; this does not decode pixels.")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout.")
    args = parser.parse_args(argv)
    try:
        document = load_json(args.input)
        errors = lint_document(document)
        source_check = {"mode": "metadata_consistency_only", "checked_frame_ids": [],
                        "native_pixel_decode_independently_verified": False}
        if not errors and args.source_root is not None:
            errors, source_check = verify_source_files(document, args.source_root)
        if errors:
            raise ValidationError(errors)
        if args.command == "lint":
            report = {"status": "metadata_lint_ok", "model_validation": "not_performed", "source_verification": source_check, "errors": []}
            code = 0
        else:
            report = score_document(document, args.source_root)
            code = 0 if report["counts"]["scored"] and not report["counts"]["rejected"] else 3
    except ValidationError as error:
        report, code = {"status": "input_rejected", "errors": error.issues, "model_validation": "not_performed"}, 2
    except (OSError, ValueError) as error:
        report, code = {"status": "input_rejected", "errors": [issue("input_error", "$", str(error))], "model_validation": "not_performed"}, 2
    text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

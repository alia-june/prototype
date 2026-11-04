/* Resolved display packet. Governing source files remain in the sibling pilot. */
globalThis.REFERENCE_OCCURRENCE_INSPECTOR_DATA = {
  "schema": "strmdocx-reference-occurrence-inspector-data/1",
  "snapshot_created": "2026-11-01",
  "role": "read_only_resolved_display_packet",
  "source_files": [
    {
      "role": "machine_contract",
      "path": "../reference-occurrence-pilot-20261101/reference_occurrence_contract.json",
      "bytes": 3838,
      "sha256": "a5a22653b719a9057dbc226751a946fdffb6beb463392ad0f7c9b8a02a126bda"
    },
    {
      "role": "pilot_fixture",
      "path": "../reference-occurrence-pilot-20261101/reference_occurrence_fixture.json",
      "bytes": 2569,
      "sha256": "b605410ead9f1bf40c58b66c397269e9e4ffa6289ca1697b8f4c6f8cc890c7a5"
    }
  ],
  "contract": {
    "contract_id": "strmdocx:reference-occurrence-pilot:0.1",
    "contract_version": "0.1",
    "status": "bounded_fixture_specific_research_contract",
    "fixture_format": "strmdocx-reference-occurrence/0.1-pilot",
    "root_schema": {
      "required_fields": [
        "format",
        "pilot_id",
        "targets",
        "relationships",
        "metadata",
        "occurrences",
        "views"
      ],
      "allowed_fields": [
        "format",
        "pilot_id",
        "targets",
        "relationships",
        "metadata",
        "occurrences",
        "views"
      ]
    },
    "record_schemas": {
      "target": {
        "collection": "targets",
        "id_prefix": "target:",
        "required_fields": ["id", "kind", "role", "payload", "payload_sha256"],
        "allowed_fields": ["id", "kind", "role", "payload", "payload_sha256"]
      },
      "relationship": {
        "collection": "relationships",
        "id_prefix": "relationship:",
        "required_fields": ["id", "kind", "meaning", "operation_ref", "input_ref", "result_ref"],
        "allowed_fields": ["id", "kind", "meaning", "operation_ref", "input_ref", "result_ref"]
      },
      "metadata": {
        "collection": "metadata",
        "id_prefix": "metadata:",
        "required_fields": ["id", "kind", "scope", "provenance"],
        "allowed_fields": ["id", "kind", "scope", "provenance"]
      },
      "occurrence": {
        "collection": "occurrences",
        "id_prefix": "occurrence:",
        "required_fields": ["id", "kind", "target_ref", "relationship_ref", "metadata_ref"],
        "allowed_fields": ["id", "kind", "target_ref", "relationship_ref", "metadata_ref"]
      },
      "view": {
        "collection": "views",
        "id_prefix": "view:",
        "required_fields": ["id", "kind", "purpose", "order_semantics", "occurrence_refs"],
        "allowed_fields": ["id", "kind", "purpose", "order_semantics", "occurrence_refs"]
      }
    },
    "policies": {
      "reject_native_null": true,
      "reject_unknown_fields": true,
      "reject_duplicate_ids_globally": true,
      "reject_duplicate_occurrence_refs_within_view": true,
      "all_views_use_same_occurrence_set": true,
      "view_order_implies_ownership": false,
      "reverse_view_mutates_history": false,
      "occurrences_are_reference_only": true
    },
    "digest": {
      "algorithm": "sha256",
      "payload_canonicalization": "json-sort-keys-compact-utf8"
    },
    "limits": {
      "max_document_bytes": 1048576,
      "max_collection_records": 4096,
      "max_views": 128,
      "max_occurrence_refs_per_view": 4096,
      "max_string_characters": 8192,
      "max_errors": 128
    },
    "expected_profile": {
      "pilot_id": "pilot:reference-occurrence:001",
      "target_ids": ["target:B0", "target:T1", "target:B1"],
      "relationship_ids": ["relationship:R1"],
      "metadata_ids": ["metadata:M1"],
      "occurrence_bindings": {
        "occurrence:O0": {
          "target_ref": "target:B0",
          "relationship_ref": "relationship:R1",
          "metadata_ref": "metadata:M1"
        },
        "occurrence:O1": {
          "target_ref": "target:T1",
          "relationship_ref": "relationship:R1",
          "metadata_ref": "metadata:M1"
        },
        "occurrence:O2": {
          "target_ref": "target:B1",
          "relationship_ref": "relationship:R1",
          "metadata_ref": "metadata:M1"
        }
      },
      "view_orders": {
        "view:V0": ["occurrence:O0", "occurrence:O1", "occurrence:O2"],
        "view:V1": ["occurrence:O2", "occurrence:O1", "occurrence:O0"]
      },
      "transformation": {
        "target_ref": "target:T1",
        "relationship_ref": "relationship:R1",
        "metadata_ref": "metadata:M1",
        "input_ref": "target:B0",
        "result_ref": "target:B1",
        "operation": "append_text",
        "argument": "!"
      },
      "relationship_meaning": "transforms_input_to_result",
      "metadata_scope": "whole_block",
      "source_text": "abc",
      "result_text": "abc!"
    }
  },
  "fixture": {
    "format": "strmdocx-reference-occurrence/0.1-pilot",
    "pilot_id": "pilot:reference-occurrence:001",
    "targets": [
      {
        "id": "target:B0",
        "kind": "target",
        "role": "immutable_text_block",
        "payload": {
          "encoding": "utf-8",
          "text": "abc"
        },
        "payload_sha256": "990307a424d0be4cf3bd865183686d80324f8f087716a50793defc349fe9b9fb"
      },
      {
        "id": "target:T1",
        "kind": "target",
        "role": "transformation",
        "payload": {
          "operation": "append_text",
          "argument": "!",
          "input_ref": "target:B0",
          "result_ref": "target:B1",
          "scope_ref": "metadata:M1"
        },
        "payload_sha256": "2d31bbe940783a0dd811a1fe49b20b249c85fe32367211c035199620c2ae1999"
      },
      {
        "id": "target:B1",
        "kind": "target",
        "role": "immutable_text_block",
        "payload": {
          "encoding": "utf-8",
          "text": "abc!"
        },
        "payload_sha256": "a222f66a099dbe4758ed8ae19171491e51350e83f867979e294d1a61a7701c4d"
      }
    ],
    "relationships": [
      {
        "id": "relationship:R1",
        "kind": "relationship",
        "meaning": "transforms_input_to_result",
        "operation_ref": "target:T1",
        "input_ref": "target:B0",
        "result_ref": "target:B1"
      }
    ],
    "metadata": [
      {
        "id": "metadata:M1",
        "kind": "metadata",
        "scope": "whole_block",
        "provenance": "Approved bounded reference-occurrence pilot fixture, 2026-11-01"
      }
    ],
    "occurrences": [
      {
        "id": "occurrence:O0",
        "kind": "occurrence",
        "target_ref": "target:B0",
        "relationship_ref": "relationship:R1",
        "metadata_ref": "metadata:M1"
      },
      {
        "id": "occurrence:O1",
        "kind": "occurrence",
        "target_ref": "target:T1",
        "relationship_ref": "relationship:R1",
        "metadata_ref": "metadata:M1"
      },
      {
        "id": "occurrence:O2",
        "kind": "occurrence",
        "target_ref": "target:B1",
        "relationship_ref": "relationship:R1",
        "metadata_ref": "metadata:M1"
      }
    ],
    "views": [
      {
        "id": "view:V0",
        "kind": "view",
        "purpose": "chronological_inspection",
        "order_semantics": "source_transformation_result",
        "occurrence_refs": ["occurrence:O0", "occurrence:O1", "occurrence:O2"]
      },
      {
        "id": "view:V1",
        "kind": "view",
        "purpose": "reverse_inspection",
        "order_semantics": "result_transformation_source_without_mutation",
        "occurrence_refs": ["occurrence:O2", "occurrence:O1", "occurrence:O0"]
      }
    ]
  }
};

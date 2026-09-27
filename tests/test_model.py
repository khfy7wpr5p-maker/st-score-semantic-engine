def test_package_exposes_schema_versions():
    import st_score_semantic_engine as semantic

    assert semantic.SNAPSHOT_SCHEMA_VERSION == "st-semantic-snapshot-v1"
    assert semantic.REPORT_SCHEMA_VERSION == "st-semantic-validation-report-v1"

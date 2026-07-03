from osteo_target_gwas.config import (
    get_scoring_weights,
    load_data_sources,
    load_default_config,
)


def test_default_config_loads() -> None:
    config = load_default_config()

    assert config


def test_data_sources_load() -> None:
    registry = load_data_sources()

    assert registry["data_sources"]


def test_default_config_required_sections_exist() -> None:
    config = load_default_config()

    expected_sections = {
        "column_mappings",
        "qc_thresholds",
        "locus_settings",
        "scoring_weights",
        "penalties",
    }

    assert expected_sections <= set(config)


def test_scoring_weights_sum_to_one_before_penalties() -> None:
    config = load_default_config()
    weights = get_scoring_weights(config)

    assert sum(weights.values()) == 1.0


def test_data_source_entries_contain_required_metadata_fields() -> None:
    registry = load_data_sources()
    required_fields = {
        "name",
        "description",
        "expected_file_format",
        "required_columns",
        "optional_columns",
        "url_placeholder",
        "licence_note",
        "local_path",
    }

    for source in registry["data_sources"]:
        assert required_fields <= set(source)
        assert source["required_columns"]

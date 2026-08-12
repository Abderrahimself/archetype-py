"""Tests for reading Python sources whose encoding is not plain UTF-8."""

from __future__ import annotations

from pathlib import Path

from archetype.analysis.imports import build_import_graph


def _make_project(tmp_path: Path, *, api_source: bytes) -> Path:
    project_path = tmp_path / "project"
    package_path = project_path / "myapp"
    package_path.mkdir(parents=True)
    (package_path / "__init__.py").write_bytes(b"")
    (package_path / "db.py").write_bytes(b"value = 1\n")
    (package_path / "api.py").write_bytes(api_source)
    return project_path


def test_build_import_graph_accepts_utf8_bom(tmp_path: Path) -> None:
    project_path = _make_project(tmp_path, api_source=b"\xef\xbb\xbfimport myapp.db\n")

    graph = build_import_graph(project_path)

    assert ("myapp.api", "myapp.db") in graph.edges()


def test_build_import_graph_accepts_pep263_encoding_declaration(tmp_path: Path) -> None:
    project_path = _make_project(
        tmp_path,
        api_source=b"# -*- coding: latin-1 -*-\n# caf\xe9\nimport myapp.db\n",
    )

    graph = build_import_graph(project_path)

    assert ("myapp.api", "myapp.db") in graph.edges()


def test_build_import_graph_still_reads_plain_utf8(tmp_path: Path) -> None:
    project_path = _make_project(
        tmp_path,
        api_source=b"# caf\xc3\xa9\nimport myapp.db\n",
    )

    graph = build_import_graph(project_path)

    assert ("myapp.api", "myapp.db") in graph.edges()

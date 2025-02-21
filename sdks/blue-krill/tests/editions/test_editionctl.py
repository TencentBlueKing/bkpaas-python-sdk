# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import json
from pathlib import Path
from textwrap import dedent

import pytest
from toml.decoder import TomlDecodeError

from blue_krill.editions.editionctl import (
    Configuration,
    DirectorySyncer,
    EditionConf,
    EditionFileMigrator,
    EditionMetaData,
    ReadOnlyCopyLinker,
    load_configuration,
    reset_project,
)


class TestLoadConfiguration:
    def test_nonexistent_file(self, tmp_path):
        settings_path = tmp_path / "nonexistent_file.toml"
        with pytest.raises(FileNotFoundError):
            load_configuration(settings_path)

    def test_invalid_format(self, tmp_path):
        settings_path = tmp_path / "editionctl.toml"
        with open(settings_path, "w") as fp:
            fp.write("{abc}")

        with pytest.raises(TomlDecodeError):
            load_configuration(settings_path)

    def test_normal(self, tmp_path):
        settings_path = tmp_path / "editionctl.toml"
        with open(settings_path, "w") as fp:
            fp.write(
                dedent(
                    """
                    project_root = ''

                    [[editions]]
                    name = "te"

                    [[editions]]
                    name = "ee"
                    """
                )
            )

        config = load_configuration(settings_path)
        assert config is not None


class TestEditionMetaData:
    def test_normal(self, tmp_path):
        meta_data = EditionMetaData("my_edition", tmp_path, "default")
        assert not meta_data.metadata_path.exists()
        assert not meta_data.gitignore_path.exists()

        (tmp_path / "foo").write_text("")
        meta_data.add_files([Path("foo")])
        meta_data.save()

        assert meta_data.metadata_path.exists()
        assert meta_data.gitignore_path.exists()

    def test_from_existed_project(self, tmp_path):
        metadata_path = tmp_path / EditionMetaData.default_metadata_path
        metadata_path.write_text(json.dumps({"edition_name": "my_edition", "external_files": []}))
        meta_data = EditionMetaData.from_existed_project(tmp_path)
        assert meta_data is not None


class TestEditionFileMigrator:
    @pytest.fixture(autouse=True)
    def setup_dirs(self, tmp_path):
        (tmp_path / "project").mkdir(parents=True)
        (tmp_path / "project" / "project.txt").write_text("")
        (tmp_path / "project" / "project_2.txt").write_text("")

        (tmp_path / "editions" / "e1").mkdir(parents=True)
        (tmp_path / "editions" / "e1" / "e1.txt").write_text("")
        (tmp_path / "editions" / "e2").mkdir(parents=True)

    @pytest.fixture
    def config(self, tmp_path):
        editions_root = tmp_path / "editions"
        return Configuration(
            project_root=tmp_path / "project",
            editions_root=editions_root,
            editions=[
                EditionConf(name="e1", rel_directory="e1"),
                EditionConf(name="e2", rel_directory="e2"),
            ],
        )

    @pytest.mark.parametrize(
        ("edition_name", "expected_files"),
        [
            ("e1", {"project.txt", "project_2.txt", "e1.txt", ".gitignore", "edition-metadata.json"}),
            ("e2", {"project.txt", "project_2.txt", ".gitignore", "edition-metadata.json"}),
        ],
    )
    def test_migrate(self, config, edition_name, expected_files):
        EditionFileMigrator(config, edition_name).migrate()

        names = [f.name for f in config.get_project_root().iterdir()]
        assert set(names) == expected_files

    def test_change_edition(self, config):
        EditionFileMigrator(config, "e1").migrate()

        # check files was synced
        names = [f.name for f in config.get_project_root().iterdir()]
        assert set(names) == {"project.txt", "project_2.txt", "e1.txt", ".gitignore", "edition-metadata.json"}

        EditionFileMigrator(config, "e2").migrate()
        names = [f.name for f in config.get_project_root().iterdir()]
        assert set(names) == {"project.txt", "project_2.txt", ".gitignore", "edition-metadata.json"}

    def test_reset_project(self, config):
        EditionFileMigrator(config, "e1").migrate()

        # check files was synced
        names = [f.name for f in config.get_project_root().iterdir()]
        assert set(names) == {"project.txt", "project_2.txt", "e1.txt", ".gitignore", "edition-metadata.json"}

        reset_project(config)
        names = [f.name for f in config.get_project_root().iterdir()]
        assert set(names) == {"project.txt", "project_2.txt"}


class TestDirectorySyncer:
    @pytest.fixture(autouse=True)
    def setup_dirs(self, tmp_path):
        (tmp_path / "project").mkdir(parents=True)
        (tmp_path / "project" / "project.txt").write_text("")
        (tmp_path / "project" / "project_2.txt").write_text("")

        (tmp_path / "editions" / "e1").mkdir(parents=True)
        (tmp_path / "editions" / "e1" / "e1.txt").write_text("")

    def test_sync(self, tmp_path):
        result = DirectorySyncer(ReadOnlyCopyLinker()).sync_files(
            source_dir=tmp_path / "editions" / "e1",
            target_dir=tmp_path / "project",
            delete_if_not_in_source_files=[],
        )

        # check files was synced
        files = list((tmp_path / "project").iterdir())
        names = [f.name for f in files]
        assert set(names) == {"project.txt", "project_2.txt", "e1.txt"}

        assert len(result.added_files) == 1
        assert len(result.added_files_relative) == 1
        assert len(result.deleted_files) == 0

    def test_sync_with_delete_files(self, tmp_path):
        result = DirectorySyncer(ReadOnlyCopyLinker()).sync_files(
            source_dir=tmp_path / "editions" / "e1",
            target_dir=tmp_path / "project",
            delete_if_not_in_source_files=[Path("project.txt")],
        )

        # check files was synced
        files = list((tmp_path / "project").iterdir())
        names = [f.name for f in files]
        assert set(names) == {"project_2.txt", "e1.txt"}

        assert len(result.added_files) == 1
        assert len(result.added_files_relative) == 1
        assert len(result.deleted_files) == 1

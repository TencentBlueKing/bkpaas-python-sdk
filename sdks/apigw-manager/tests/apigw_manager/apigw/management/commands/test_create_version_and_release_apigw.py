# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
from datetime import datetime

import pytest
import yaml
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from apigw_manager.apigw.management.commands.create_version_and_release_apigw import Command


@pytest.fixture()
def default_command_flags(definition_file):
    return {
        "define": [],
        "file": str(definition_file),
        "namespace": "",
        "title": "",
        "comment": "",
        "generate_sdks": False,
        "no_pub": False,
    }


@pytest.fixture()
def fetcher(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def releaser(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def resource_sync_manager(mocker):
    manager = mocker.MagicMock()
    manager.get.return_value = {}
    return manager


@pytest.fixture()
def datetime_now():
    return datetime.now()


@pytest.fixture()
def command(mocker, fetcher, releaser, resource_sync_manager, datetime_now):
    command = Command()
    command.Fetcher = mocker.MagicMock(return_value=fetcher)
    command.Releaser = mocker.MagicMock(return_value=releaser)
    command.ResourceSignatureManager = mocker.MagicMock(return_value=resource_sync_manager)
    command.now_func = mocker.MagicMock(return_value=datetime_now)
    return command


@pytest.fixture()
def fake_resource_version():
    return {
        "name": "testing",
        "version": "1.0.0",
        "title": "testing",
        "comment": "for testing purposes",
    }


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        (None, "None"),
        ("1.0.0", "1.0.0"),
        ("1.0.1", "1.0.1"),
        ("v1.0.0", "1.0.0"),
    ],
)
def test_parse_version_from_definition(command, version, expected):
    result = command._parse_version_from_definition({"version": version})

    assert str(result) == expected


@pytest.mark.parametrize(
    "version",
    [
        "dev",
        "invalid-version",
    ],
)
def test_parse_version_from_definition__error(command, version):
    with pytest.raises(InvalidVersion):
        command._parse_version_from_definition({"version": version})


@pytest.mark.parametrize(
    ("resource_version", "expected"),
    [
        (None, "None"),
        ({}, "None"),
        ({"version": "1.0.0"}, "1.0.0"),
        ({"version": "v1.0.0"}, "1.0.0"),
        ({"version": "dev"}, "None"),
    ],
)
def test_parse_version_from_resource_version(command, resource_version, expected):
    result = command._parse_version_from_resource_version(resource_version)

    assert str(result) == expected


@pytest.mark.parametrize(
    ("defined_version", "expected"),
    [
        (None, "0.0.1"),
        ("1.0.0", "1.0.0"),
        ("v1.0.1", "1.0.1"),
    ],
)
def test_fix_defined_version(command, defined_version, expected):
    result = command._fix_defined_version(defined_version and parse_version(defined_version))
    assert str(result) == expected


@pytest.mark.parametrize(
    ("defined_version", "latest_version", "is_dirty", "expected"),
    [
        ("1.0.0", None, False, True),
        ("1.0.1", "1.0.0", False, True),
        ("1.0.1", "1.0.1", True, True),
        ("1.0.1", "1.0.1", False, False),
        ("1.0.1", "1.0.1+1", False, False),
    ],
)
def test_should_create_resource_version(mocker, command, defined_version, latest_version, is_dirty, expected):
    manager = mocker.MagicMock(is_dirty=mocker.MagicMock(return_value=is_dirty))
    result = command._should_create_resource_version(
        manager,
        "test",
        parse_version(defined_version),
        latest_version and parse_version(latest_version),
    )
    assert result is expected


@pytest.mark.parametrize(
    ("defined_version", "resource_version_exists", "expected"),
    [
        ("1.0.1", False, "1.0.1"),
        ("0.0.1", False, "0.0.1"),
        ("1.0.1+1", False, "1.0.1+1"),
        ("1.0.1", True, "1.0.1+{build_metadata}"),
        ("1.0.1+1", True, "1.0.1+{build_metadata}"),
    ],
)
def test_get_version_to_be_created(
        command,
        datetime_now,
        defined_version,
        resource_version_exists,
        expected,
):
    result = command._get_version_to_be_created(
        parse_version(defined_version),
        resource_version_exists,
    )

    build_metadata = datetime_now.strftime("%Y%m%d%H%M%S")
    assert str(result) == expected.format(build_metadata=build_metadata)


class TestHandle:
    def test_handle_version_not_change(
            self,
            command,
            fetcher,
            releaser,
            faker,
            definition_file,
            resource_sync_manager,
            fake_resource_version,
            default_command_flags,
    ):
        definition_file.write(yaml.dump(fake_resource_version))
        stage = faker.pystr()

        fetcher.latest_resource_version.return_value = fake_resource_version
        releaser.release.return_value = {
            "version": fake_resource_version["version"],
            "resource_version_name": fake_resource_version["name"],
            "resource_version_title": faker.pystr(),
            "stage_names": [stage],
        }
        resource_sync_manager.is_dirty.return_value = False

        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_not_called()
        releaser.release.assert_called_once_with(
            version=fake_resource_version["version"],
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
            stage_names=stage,
        )

    def test_handle_version_not_change_but_dirty(
            self,
            command,
            fetcher,
            releaser,
            faker,
            definition_file,
            resource_sync_manager,
            fake_resource_version,
            default_command_flags,
    ):
        definition_file.write(yaml.dump(fake_resource_version))
        stage = faker.pystr()
        fetcher.latest_resource_version.return_value = fake_resource_version
        fetcher.list_resource_versions.return_value = {"count": 1}

        current_version = command._get_version_to_be_created(parse_version(fake_resource_version["version"]), True)

        releaser.release.return_value = {
            "version": str(current_version),
            "resource_version_name": fake_resource_version["name"],
            "resource_version_title": faker.pystr(),
            "stage_names": [stage],
        }
        releaser.create_resource_version.return_value = {
            "version": str(current_version),
            "title": fake_resource_version["title"],
            "comment": fake_resource_version["comment"],
        }
        resource_sync_manager.is_dirty.return_value = True

        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_any_call(
            version=str(current_version),
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )
        releaser.release.assert_called_once_with(
            version=str(current_version),
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
            stage_names=stage,
        )

    def test_handle_version_changed(
            self,
            command,
            fetcher,
            releaser,
            faker,
            definition_file,
            fake_resource_version,
            default_command_flags,
    ):
        defined_version = "1.0.0-alpha2"
        definition_file.write(
            yaml.dump(
                {
                    "version": defined_version,
                    "title": fake_resource_version["title"],
                    "comment": fake_resource_version["comment"],
                }
            )
        )

        latest_version = "1.0.0-alpha1"
        fetcher.latest_resource_version.return_value = dict(fake_resource_version, version=latest_version)
        fetcher.list_resource_versions.return_value = {"count": 0}

        releaser.create_resource_version.return_value = dict(
            fake_resource_version,
            version=defined_version,
        )
        stage = faker.pystr()
        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_any_call(
            version=defined_version,
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )
        releaser.release.assert_any_call(
            version=defined_version,
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
            stage_names=stage,
        )

    def test_handle_version_not_set(
            self,
            command,
            fetcher,
            releaser,
            faker,
            definition_file,
            resource_sync_manager,
            fake_resource_version,
            default_command_flags,
    ):
        definition_file.write(
            yaml.dump(
                {
                    "title": fake_resource_version["title"],
                    "comment": fake_resource_version["comment"],
                }
            )
        )

        stage = faker.pystr()
        fetcher.latest_resource_version.return_value = fake_resource_version
        fetcher.list_resource_versions.return_value = {"count": 1}

        defined_version = command._get_version_to_be_created(parse_version("0.0.1"), True)

        releaser.release.return_value = {
            "version": str(defined_version),
            "resource_version_name": faker.pystr(),
            "resource_version_title": faker.pystr(),
            "stage_names": [stage],
        }

        releaser.create_resource_version.return_value = {
            "version": str(defined_version),
            "title": fake_resource_version["title"],
            "comment": fake_resource_version["comment"],
        }

        resource_sync_manager.is_dirty.return_value = False
        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_any_call(
            version=str(defined_version),
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )
        releaser.release.assert_called_once_with(
            version=str(defined_version),
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
            stage_names=stage,
        )

    def test_handle_without_release(
            self,
            command,
            fetcher,
            releaser,
            faker,
            definition_file,
            resource_sync_manager,
            fake_resource_version,
            default_command_flags,
    ):
        definition_file.write(yaml.dump(fake_resource_version))
        stage = faker.pystr()

        default_command_flags["no_pub"] = True

        fetcher.latest_resource_version.return_value = fake_resource_version

        resource_sync_manager.is_dirty.return_value = False

        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_not_called()

        releaser.releaser.release.assert_not_called()

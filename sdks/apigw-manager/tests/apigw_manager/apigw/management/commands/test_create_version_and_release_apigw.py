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
from apigw_manager.apigw.management.commands.create_version_and_release_apigw import Command
from packaging.version import parse as parse_version


@pytest.fixture()
def default_command_flags(definition_file):
    return {
        "define": [],
        "file": str(definition_file),
        "namespace": "",
        "title": "",
        "comment": "",
        "generate_sdks": False,
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
    "version, expected",
    [
        (None, "None"),
        ("1.0.0", "1.0.0"),
        ("1.0.1", "1.0.1"),
        ("v1.0.0", "1.0.0"),
    ],
)
def test_get_version_from_definition(command, version, expected):
    result = command.get_version_from_definition({"version": version})

    assert str(result) == expected


@pytest.mark.parametrize(
    "resource_version, expected",
    [
        (None, "None"),
        ({}, "None"),
        ({"version": "1.0.0"}, "1.0.0"),
        ({"version": "v1.0.0"}, "1.0.0"),
    ],
)
def test_get_version_from_resource_version(command, resource_version, expected):
    result = command.get_version_from_resource_version(resource_version)

    assert str(result) == expected


@pytest.mark.parametrize(
    "current, latest, expected_current_version, expected_latest_version",
    [
        (None, None, "0.0.1", "?"),
        (None, "1.0.0", "1.0.0+{build_metadata}", "1.0.0"),
        ("1.0.1", "1.0.0", "1.0.1", "1.0.0"),
        ("1.0.1", None, "1.0.1", "?"),
        ("1.0.1", "1.0.1", "1.0.1+{build_metadata}", "1.0.1"),
        ("1.0.1", "1.0.1+1", "1.0.1+{build_metadata}", "1.0.1+1"),
        ("1.0.1", "1.0.2", "1.0.1+{build_metadata}", "1.0.2"),
    ],
)
def test_fix_version(command, current, latest, expected_current_version, expected_latest_version, datetime_now):
    current_version, latest_version = command.fix_version(
        current and parse_version(current),
        latest and parse_version(latest),
    )

    build_metadata = datetime_now.strftime("%Y%m%d%H%M%S")
    assert str(current_version) == expected_current_version.format(build_metadata=build_metadata)
    assert str(latest_version) == expected_latest_version.format(build_metadata=build_metadata)


def test_generate_sdks_with_false_flag(command, fake_resource_version, releaser):
    command.generate_sdks(releaser, fake_resource_version, False)
    releaser.generate_sdks.assert_not_called()


def test_generate_sdks(command, fake_resource_version, releaser):
    command.generate_sdks(releaser, fake_resource_version, True)
    releaser.generate_sdks.assert_called_once_with(resource_version=fake_resource_version["version"])


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
        definition_file.write(yaml.dump({"version": fake_resource_version["version"]}))
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
            stage_names=stage,
            version=fake_resource_version["version"],
            resource_version_name=fake_resource_version["name"],
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
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
        definition_file.write(
            yaml.dump(
                {
                    "version": fake_resource_version["version"],
                    "title": fake_resource_version["title"],
                    "comment": fake_resource_version["comment"],
                }
            )
        )
        stage = faker.pystr()
        fake_resource_version["name"] = faker.pystr()
        fetcher.latest_resource_version.return_value = fake_resource_version

        parsed_fake_version = parse_version(fake_resource_version["version"])
        current_version, _ = command.fix_version(parsed_fake_version, parsed_fake_version)
        assert current_version > parsed_fake_version

        releaser.release.return_value = {
            "version": str(current_version),
            "resource_version_name": fake_resource_version["name"],
            "resource_version_title": faker.pystr(),
            "stage_names": [stage],
        }
        releaser.create_resource_version.return_value = {
            "version": str(current_version),
            "name": fake_resource_version["name"],
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
            stage_names=stage,
            version=str(current_version),
            resource_version_name=fake_resource_version["name"],
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
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
        current_version = "1.0.1"
        definition_file.write(
            yaml.dump(
                {
                    "version": current_version,
                    "title": fake_resource_version["title"],
                    "comment": fake_resource_version["comment"],
                }
            )
        )
        latest_version = "1.0.0"
        fetcher.latest_resource_version.return_value = {
            "version": latest_version,
            **fake_resource_version,
        }
        releaser.create_resource_version.return_value = dict(
            fake_resource_version,
            version=current_version,
        )
        stage = faker.pystr()
        command.handle(stage=stage, **default_command_flags)

        releaser.create_resource_version.assert_any_call(
            version=current_version,
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )
        releaser.release.assert_any_call(
            stage_names=stage,
            version=current_version,
            resource_version_name=fake_resource_version["name"],
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )

    def test_handle_version_not_set(
        self,
        command,
        fetcher,
        releaser,
        faker,
        resource_sync_manager,
        fake_resource_version,
        default_command_flags,
    ):
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
            stage_names=stage,
            version=fake_resource_version["version"],
            resource_version_name=fake_resource_version["name"],
            title=fake_resource_version["title"],
            comment=fake_resource_version["comment"],
        )

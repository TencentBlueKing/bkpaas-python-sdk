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
import pytest

from apigw_manager.apigw.management.commands.create_version_and_release_apigw import Command


@pytest.fixture()
def fetcher(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def releaser(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def default_command_flags():
    return {
        "define": [],
        "file": None,
        "namespace": "",
    }


@pytest.fixture()
def command(mocker, fetcher, releaser):
    command = Command()
    command.Fetcher = mocker.MagicMock(return_value=fetcher)
    command.Releaser = mocker.MagicMock(return_value=releaser)
    return command


@pytest.mark.parametrize(
    "resource_version,title,expected",
    [
        (None, "v2", True),
        ({"title": "v1"}, "v2", True),
        ({"title": "v2"}, "v2", False),
    ],
)
def test_should_create_resource_version(command, resource_version, title, expected):
    assert command._should_create_resource_version(resource_version, title) == expected


def test_handle_title_not_change(command, fetcher, releaser, faker, default_command_flags):
    title = faker.pystr()
    name = faker.pystr()
    fetcher.latest_resource_version.return_value = {"title": title, "name": name}
    releaser.release.return_value = {
        "resource_version_name": faker.pystr(),
        "resource_version_title": faker.pystr(),
        "stage_names": [faker.pystr()],
    }

    comment = faker.pystr()
    stage = faker.pystr()
    command.handle(title=title, comment=comment, stage=stage, **default_command_flags)

    releaser.create_resource_version.assert_not_called()
    releaser.release.assert_called_once_with(
        resource_version_name=name,
        comment=comment,
        stage_names=stage,
    )


def test_handle_title_changed(command, fetcher, releaser, faker, default_command_flags):
    resource_version_name = faker.pystr()
    fetcher.latest_resource_version.return_value = {"title": faker.pystr()}
    releaser.create_resource_version.return_value = {"name": resource_version_name}

    title = faker.pystr()
    comment = faker.pystr()
    stage = faker.pystr()
    command.handle(title=title, comment=comment, stage=stage, **default_command_flags)

    releaser.create_resource_version.assert_any_call(title=title, comment=comment)
    releaser.release.assert_any_call(
        resource_version_name=resource_version_name,
        comment=comment,
        stage_names=stage,
    )


def test_handle_title_not_specified(command, fetcher, releaser, faker, default_command_flags):
    resource_version_name = faker.pystr()
    releaser.create_resource_version.return_value = {"name": resource_version_name}

    comment = faker.pystr()
    stage = faker.pystr()
    command.handle(title=None, comment=comment, stage=stage, **default_command_flags)

    releaser.create_resource_version.assert_called()
    with pytest.raises(AssertionError):
        releaser.create_resource_version.assert_any_call(title=None, comment=comment)

    releaser.release.assert_any_call(
        resource_version_name=resource_version_name,
        comment=comment,
        stage_names=stage,
    )


def test_handle_from_definition_file(command, fetcher, releaser, tmp_path, faker):
    fetcher.latest_resource_version.return_value = {"title": faker.pystr(), "name": faker.pystr()}
    resource_version_name = faker.pystr()
    releaser.create_resource_version.return_value = {"name": resource_version_name}

    file = tmp_path / "definition.yaml"
    file.write_text('release: {"title": "test", "comment": "update"}')

    stage = faker.pystr()
    command.handle(
        title=None,
        comment=None,
        stage=stage,
        file=file,
        define=[],
        namespace="release",
    )
    releaser.create_resource_version.assert_any_call(
        title="test",
        comment="update",
    )
    releaser.release.assert_any_call(
        resource_version_name=resource_version_name,
        comment="update",
        stage_names=stage,
    )

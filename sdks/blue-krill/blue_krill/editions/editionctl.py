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
import abc
import fnmatch
import json
import logging
import os
import shutil
import stat
import sys
import time
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from textwrap import dedent
from typing import Any, Collection, Dict, Iterator, List, Optional, Set, Type

import click
import toml
from pydantic import BaseModel, ValidationError
from toml.decoder import TomlDecodeError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Set up logging as a console output
hdr = logging.StreamHandler()
hdr.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(hdr)

__version__ = '0.1.0'

# The default file name of config file
DEFAULT_CONFIG_FILE_NAME = 'editionctl.toml'


class FileLinker(abc.ABC):
    @abc.abstractmethod
    def link(self, src_file: PathLike, dst_file: PathLike):
        pass

    @abc.abstractmethod
    def unlink(self, dst_file: PathLike):
        pass


class CopyLinker(FileLinker):
    """Directly copy"""

    def link(self, src_file, dst_file):
        shutil.copyfile(src_file, dst_file, follow_symlinks=False)

    def unlink(self, dst_file):
        Path(dst_file).unlink()


class ReadOnlyCopyLinker(FileLinker):
    """CopyLinker, make sure dst-file is read only"""

    read_only_mode = stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH
    writable_mode = stat.S_IWRITE | stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH

    def set_file_permission(self, path: Path, mode):
        file = Path(path)
        if file.exists():
            file.chmod(mode)

    def link(self, src_file, dst_file):
        # make sure file is writable before copy
        self.set_file_permission(dst_file, self.writable_mode)
        shutil.copyfile(src_file, dst_file, follow_symlinks=False)
        # make sure file is read-only to avoid unexpected modifies
        self.set_file_permission(dst_file, self.read_only_mode)

    def unlink(self, dst_file):
        # Avoid windows cannot delete read-only files
        self.set_file_permission(dst_file, self.writable_mode)
        Path(dst_file).unlink()


class SymbolLinker(FileLinker):
    """Create symbol link from src_file to dst_file"""

    def link(self, src_file, dst_file):
        src = Path(src_file).absolute()
        dst = Path(dst_file).absolute()
        if dst.exists():
            if src.samefile(dst):
                return

            dst.unlink()

        dst.symlink_to(src)

    def unlink(self, dst_file):
        Path(dst_file).unlink()


def get_linker(type_: str) -> FileLinker:
    type_map: Dict[str, Type[FileLinker]] = {
        "default": ReadOnlyCopyLinker,
        "copy": CopyLinker,
        "symbol-link": SymbolLinker,
    }
    return type_map[type_]()


@click.group()
@click.option('--log-level', default="INFO", type=click.Choice(['DEBUG', "INFO", "WARNING", "ERROR", "CRITICAL"]))
@click.option(
    '--settings-path',
    required=False,
    help='Path fo config file, by default editionctl will try to use "editionctl.toml" in current directory',
)
@click.pass_context
def main(ctx, settings_path, log_level):
    logger.setLevel(getattr(logging, log_level))

    # Read and set command configuration
    if not settings_path:
        settings_path = Path.cwd() / DEFAULT_CONFIG_FILE_NAME

    ctx.ensure_object(dict)
    ctx.obj['settings_path'] = settings_path


class EditionConf(BaseModel):
    """Edition config object

    :param name: name of edition
    :param rel_directory: relative directory path of edition, default to `name`
    """

    name: str
    rel_directory: Optional[str]

    def get_rel_directory(self) -> str:
        return self.rel_directory or self.name


class Configuration(BaseModel):
    """The monolith config object for editionctl tool

    :param project_root: if not given, use current directory by default
    :param editions_root: if not given, use `project_root` by default
    :param linker_type: "default" or "symbol-link"
    """

    project_root: Optional[Path]
    editions_root: Optional[Path]
    linker_type: Optional[str]
    editions: List[EditionConf]

    def get_project_root(self) -> Path:
        return self.project_root or Path.cwd()

    def get_editions_root(self) -> Path:
        return self.editions_root or self.get_project_root()

    def get_linker_type(self) -> str:
        return self.linker_type or 'default'

    def get_edition(self, name: str) -> EditionConf:
        """Get edition conf object by name"""
        for obj in self.editions:
            if obj.name == name:
                return obj
        raise KeyError(f'Edition with name: {name} not found')

    def get_edition_directory(self, name: str) -> PathLike:
        """Get edition's directory"""
        rel_path = self.get_edition(name).get_rel_directory()
        return self.get_editions_root() / rel_path


def load_configuration(settings_path: PathLike, **overwrites) -> Configuration:
    """Load configuration from a settings file

    :raises: FileNotFoundError, TomlDecodeError, ValidationError(pydantic)
    """
    settings_data = toml.load(settings_path)
    settings_data.update(overwrites)
    return Configuration(**settings_data)


def get_configuration_or_quit(settings_path: PathLike, **overwrites) -> Configuration:
    """Get configuration object or abort execution"""
    try:
        return load_configuration(settings_path, **overwrites)
    except FileNotFoundError:
        logger.critical('Settings file: "%s" not found, exit not.', settings_path)
        sys.exit(1)
    except TomlDecodeError as e:
        logger.critical('Settings file: "%s" is not a valid TOML file, detail: %s', settings_path, e)
        sys.exit(1)
    except ValidationError as e:
        logger.critical('Settings file: "%s" is not a valid TOML file, detail: %s', settings_path, e)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        logger.critical('Unable to process settings file, error detail: %s', settings_path, e)
        sys.exit(1)


@main.command()
@click.argument("edition_name_in_pos", required=False)
@click.option("--edition-name", required=False)
@click.option("--linker-type", required=False)
@click.pass_context
def activate(ctx, edition_name_in_pos, edition_name, linker_type):
    """Try to active a given edition.

    In the beginning, the plan was to using "namespace packages". But after some experiments,
    we found that solution is too difficult and fragile to implement because we need our namespace
    packages to be nested.

    So currently we are using a simpler(and stupidier) approach: sync all source files under the
    specified edition directory to the main package.
    """
    settings = {}
    # if linker_type has been set, overwrite the settings linker_type
    if linker_type:
        settings["linker_type"] = linker_type

    config = get_configuration_or_quit(ctx.obj['settings_path'], **settings)

    edition_name = edition_name_in_pos or edition_name
    if not edition_name:
        logger.critical('Must provide edtion name via position argument or "--edition-name"')
        sys.exit(1)

    try:
        migrator = EditionFileMigrater(config, edition_name)
        migrator.migrate()
    except RuntimeError as err:
        logger.exception("unable to finish the migration: %s", err)
    except ConfigurationError as err:
        logger.critical("Configuration error: %s", err)
    else:
        logger.info(f"Edition {edition_name} activated, linker is {config.get_linker_type()}")


# Exceptions start


class BaseCommandException(Exception):
    pass


class ConfigurationError(BaseCommandException):
    """Error caused by configuration error"""


class MetadataNotFound(BaseCommandException):
    """Can not found a metadata file in given project root"""


class InvalidMetadataFile(BaseCommandException):
    """Can not found a metadata file in given project root"""


# Exceptions end


class EditionMetaData:
    """The metadata for project edition, it was maintained by editionctl automatically."""

    default_gitignore_path = ".gitignore"
    default_metadata_path = "edition-metadata.json"

    def __init__(self, edition_name: str, project_root: PathLike, linker_type: str):
        self.edition_name = edition_name
        self.project_root = Path(project_root)
        self.metadata_path = self.project_root / self.default_metadata_path
        self.gitignore_path = self.project_root / self.default_gitignore_path
        self.external_files: List[Dict[str, Any]] = []
        self.linker_type = linker_type

    @classmethod
    def from_existed_project(cls, project_root: PathLike):
        """Generate a metadata object from an existed project"""
        metadata_path = Path(project_root) / cls.default_metadata_path
        if not metadata_path.exists():
            raise MetadataNotFound()

        try:
            with open(metadata_path, "r") as fp:
                data = json.loads(fp.read())
                result = cls(
                    edition_name=data["edition_name"],
                    project_root=project_root,
                    linker_type=data.get("linker_type", "default"),
                )
                result.external_files = data["external_files"]
                return result
        except Exception as e:
            logger.exception(f"Unable to load metadata file: {e}")
            raise InvalidMetadataFile("metadata file is invalid")

    def add_files(self, relative_paths: Collection[Path]):
        """Add new files to metadata

        :param relative_path: Relative path of file
        """
        for rel_path in relative_paths:
            filepath = self.project_root / rel_path
            stats = filepath.stat()
            self.external_files.append(
                {"file": str(rel_path), "size": int(stats.st_size), "mtime": int(stats.st_mtime)}
            )

    def save(self):
        """Save the current metadata to project"""
        logger.debug("Writing metadata file...")
        with open(self.metadata_path, "w") as fp:
            content = json.dumps(
                {
                    "edition_name": self.edition_name,
                    "linker_type": self.linker_type,
                    "external_files": self.external_files,
                },
                indent=4,
            )
            fp.write(content)

        # Also write .gitignore file in project_root to avoid push extra edition-specified content
        # by accident
        with open(self.gitignore_path, "w") as fp:
            fp.write(
                "# This file is written by editionctl\n{}".format(
                    "\n".join(obj["file"] for obj in self.external_files)
                )
            )

    def list_managed_files(self) -> Iterator[Path]:
        """Generate all files managed by current metadata"""
        for file_obj in self.external_files:
            yield self.project_root / file_obj["file"]

        yield self.gitignore_path
        yield self.metadata_path


class EditionFileMigrater:
    """The file migrater"""

    def __init__(self, config: Configuration, edition_name: str):
        self.config = config
        self.edition_name = edition_name
        self.linker = get_linker(config.get_linker_type())

    def get_edition_conf(self) -> EditionConf:
        try:
            return self.config.get_edition(self.edition_name)
        except KeyError as e:
            raise RuntimeError('Can not read edition config: %s', e)

    def migrate(self):
        """Migration edition specified files to project root directory

        :raises: ConfigurationError
        """
        # Check if edition directory exists, so we could stop at the very beginning.
        edition_dir = self.config.get_edition_directory(self.edition_name)
        if not edition_dir.exists():
            logger.critical(f"Edition directory: {edition_dir} does not exists, please check your files.")
            raise ConfigurationError('Wrong edition dir')

        last_metadata = load_current_metadata(self.config)
        if last_metadata and self.should_reset(last_metadata):
            reset_project(self.config)

        delete_files = []
        if last_metadata:
            delete_files = [Path(f['file']) for f in last_metadata.external_files]

        result = DirectorySyncer(self.linker).sync_files(
            source_dir=edition_dir,
            target_dir=self.config.get_project_root(),
            delete_if_not_in_source_files=delete_files,
        )

        metadata = EditionMetaData(self.edition_name, self.config.get_project_root(), self.config.get_linker_type())
        metadata.add_files(result.added_files_relative)
        metadata.save()

    def should_reset(self, last_metadata: EditionMetaData):
        """If the migrator should reset all migrated states"""
        if last_metadata.edition_name != self.edition_name:
            return True
        if last_metadata.linker_type != self.config.get_linker_type():
            return True
        return False


@main.command()
@click.pass_context
def reset(ctx):
    """Reset activated edition"""
    config = get_configuration_or_quit(ctx.obj['settings_path'])
    reset_project(config)


def reset_project(config: Configuration):
    """Reset all migration states.

    - Remove metadata and related files
    - Unlink all migarated files(from metadata file)
    """
    metadata = load_current_metadata(config)
    if metadata is None:
        logger.info('No metadata can be found, resetting aborted')
        return

    logger.info('Resetting project.')
    for filepath in metadata.list_managed_files():
        logger.debug(f"Unlinking file {filepath}.")
        try:
            filepath.unlink()
        except FileNotFoundError:
            pass


def load_current_metadata(config: Configuration) -> Optional[EditionMetaData]:
    """Get the last metadata"""
    try:
        return EditionMetaData.from_existed_project(config.get_project_root())
    except MetadataNotFound:
        return None


@dataclass
class SyncResult:
    """Result of one directory sync process"""

    added_files_relative: Set[Path] = field(default_factory=set)
    added_files: Set[Path] = field(default_factory=set)
    deleted_files: Set[Path] = field(default_factory=set)


class DirectorySyncer:
    """A simple directory syncer"""

    ignore_patterns = ('*.pyc', '*.pyo', 'CVS', 'tmp', '.git', '.svn', '__pycache__')

    def __init__(self, file_linker: FileLinker):
        self.file_linker = file_linker

    def should_ignore(self, name) -> bool:
        """Should ignore this file/directory or not"""
        return any(fnmatch.fnmatch(name, p) for p in self.ignore_patterns)

    def sync_files(
        self, source_dir: Path, target_dir: Path, delete_if_not_in_source_files: Optional[Collection[Path]] = None
    ) -> SyncResult:
        """Sync files in `source_dir` to `target_dir`, return absolute path of all synced files

        :param source_dir: Source directory
        :param target_dir: Target directory
        :param delete_if_not_in_source_files: When files in this list were not presented in current source directory,
            remove the file if it was in target directory, all path must be relative.
        :returns: All synced file paths
        """
        delete_files = delete_if_not_in_source_files or set()
        delete_files = set(delete_files)

        result = SyncResult()
        for root, dirs, files in os.walk(source_dir, followlinks=False):
            # Ignore dirs and files which should be ignored
            # See: https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk
            dirs[:] = [d for d in dirs if not self.should_ignore(d)]
            files = [f for f in files if not self.should_ignore(f)]

            rel_path = root[len(str(source_dir)) :].lstrip(os.path.sep)
            dst_path = target_dir / rel_path
            if not dst_path.exists():
                dst_path.mkdir()

            for filename in files:
                src_file = Path(root) / filename
                # Ignore symbolic links
                if os.path.islink(src_file):
                    continue
                dst_file = dst_path / filename

                rel_file = Path(rel_path) / filename
                logger.debug(f"Linking file {rel_file}...")
                self.file_linker.link(src_file, dst_file)
                result.added_files.add(dst_file)
                result.added_files_relative.add(rel_file)

        # Remove files if them were not provided in source directory
        if delete_files:
            for file_path in delete_files:
                if file_path.is_absolute():
                    continue
                if file_path not in result.added_files_relative:
                    logger.debug('Delete file %s.', file_path)
                    try:
                        self.file_linker.unlink(target_dir / file_path)
                    except FileNotFoundError:
                        pass
                    result.deleted_files.add(file_path)
        return result


@main.command()
@click.pass_context
def info(ctx):
    """Print current edition information"""
    config = get_configuration_or_quit(ctx.obj['settings_path'])
    try:
        metadata = EditionMetaData.from_existed_project(config.get_project_root())
    except MetadataNotFound:
        logger.critical("No metadata file found in project root, please activate the edition first.")
        return

    logger.info(f"current edition is {metadata.edition_name}, linker is {metadata.linker_type}")


@main.command()
@click.pass_context
def help(ctx):
    """Print version info"""
    logger.info(f"current version: {__version__}")
    logger.info("Example config file:")
    print(
        dedent(
            '''
        # 存放主版本源码文件目录，留空默认为当前目录
        # project_root = 'src/'
        # 存放各版本特殊源码文件的目录，留空默认等于 `project_root`
        # editions_root = 'editions/'
        # 版本文件复制方式，可选值："default"（只读文件拷贝） / "symbol-link"（软连接），默认为 "default"
        # linker_type = 'default'

        # 定义各版本名称与源码相对路径
        [[editions]]
        # 必选：版本名称
        name = "TE"
        # 源码在 `editions_root` 里的相对路径，默认与 `name` 相等
        rel_directory = 'te'

        # 定义多个版本
        [[editions]]
        name = "EE"
        # 源码在 `editions_root` 里的相对路径，默认与 `name` 相等
        rel_directory = 'ee'
    '''
        )
    )


@main.command()
@click.pass_context
def develop(ctx):
    """Enter develop mode, auto trigger edition activate procedure after files under current
    edtion directory have been modified.
    """
    config = get_configuration_or_quit(ctx.obj['settings_path'])
    project_root = config.get_project_root()
    try:
        metadata = EditionMetaData.from_existed_project(project_root)
    except MetadataNotFound:
        logger.critical("No metadata file found in project root, please activate the edition first.")
        return

    package_path = config.get_edition_directory(metadata.edition_name)
    event_handler = EditionDevelopEventHandler(config, metadata.edition_name)
    observer = Observer()
    observer.schedule(event_handler, str(package_path), recursive=True)
    logger.info(f"Start watching {package_path} directory for edition {metadata.edition_name}...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class EditionDevelopEventHandler(FileSystemEventHandler):
    """Handler will auto re-activate edition when it's content changes"""

    def __init__(self, config: Configuration, edition_name: str):
        self.config = config
        self.edition_name = edition_name
        super().__init__()

    def on_any_event(self, event):
        logger.debug(f"Event {event} detected, will re-activate project edtion")

        logger.info("Going to re-activate edtion...")
        migrator = EditionFileMigrater(self.config, self.edition_name)
        try:
            migrator.migrate()
        except RuntimeError:
            logger.critical("unable to finish the migration")
        logger.info(f"Edition {self.edition_name} re-activated, linker is {self.config.get_linker_type()}")

        logger.info("Inform project dev server to reload.")


if __name__ == "__main__":
    main()

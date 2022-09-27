#!/usr/bin/env python3

import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile

import click

from special_zip import custom_mesh_skin_base_zip

home_dir = Path(os.path.expanduser('~'))
pref_file = home_dir / '.tm_mesh2skin.preferences'

def load_preferences():
    if pref_file.exists():
        return json.loads(pref_file.read_text())
    default_prefs = {
        "description": "Add keys from preference fields to the root of this JSON document with an appropriate type",
        "preference fields": {
            "tm_data_dir": {"example": "c:\\users\\username\\Documents\\Trackmania", "type": "string"},
        },
        "tm_data_dir": autodetect_tm_dir(),
    }
    pref_file.write_text(json.dumps(default_prefs))
    return default_prefs


def autodetect_tm_dir(must_exist=True):
    default_tm = home_dir / 'Documents' / 'Trackmania'
    if not must_exist or default_tm.exists():
        return default_tm
    return None


def error_tm_data_dir():
    print(f"""
Error: Cannot find Trackmania data dir. Autodetect checked {autodetect_tm_dir(must_exist=False)}

Options:
1. set it manually using the --tm-data-dir option (see --help).
2. You set `tm_data_dir` in {str(pref_file)}
""")
    sys.exit(1)


@click.command()
@click.argument('mesh_file')
@click.argument('skin_name', required=False)
@click.option('--any-file', is_flag=True, help='Do not check the file extension')
@click.option('--tm-data-dir', required=False, help='The trackmania user data folder; usually c:\\users\\name\\Documents\\Trackmania. Will be auto-detected by default')
def create_custom_mesh(mesh_file, skin_name, any_file, tm_data_dir):
    mesh_file_p = Path(mesh_file)
    if not (any_file or mesh_file.lower().endswith('.mesh.gbx')):
        print('Error: does not end in .Mesh.Gbx. Exiting... (note: use --any-file to skip this check)')
        return
    if not mesh_file_p.exists():
        print('Error: mesh file does not exist at: ' + mesh_file_p)
        return
    mesh_suffix = '.'.join(mesh_file.split('.')[-2:])

    prefs = load_preferences()
    if not tm_data_dir:
        auto_dir = autodetect_tm_dir()
        tm_data_dir = prefs.get('tm_data_dir', auto_dir) or auto_dir

    tm_data_path = Path(tm_data_dir or ".should-not-exist.99966662222")
    if not tm_data_dir or not tm_data_path.exists():
        return error_tm_data_dir()

    if not skin_name:
        skin_name = mesh_file_p.name.removesuffix(f'.{mesh_suffix}')

    destination = tm_data_dir / 'Skins' / 'Models' / 'HelmetPilot' / skin_name
    mesh_dest = destination / 'Player.Mesh.Gbx'
    zip_dest = destination.with_suffix('.zip')

    print(f"""
Creating skin `{skin_name}` in `{destination}`.
  Zip File:  {zip_dest}
  Mesh File: {mesh_dest}
    """)

    destination.mkdir(exist_ok=True)
    mesh_dest.write_bytes(mesh_file_p.read_bytes())
    zip_dest.write_bytes(custom_mesh_skin_base_zip)
    with ZipFile(zip_dest, 'r') as zip:
        zip.extractall(destination)
    print("Done.")

if __name__ == "__main__":
    create_custom_mesh()

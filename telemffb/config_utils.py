#
# This file is part of the TelemFFB distribution (https://github.com/walmis/TelemFFB).
# Copyright (c) 2023 Valmantas Palikša.
# Copyright (c) 2023 Micah Frisby
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import telemffb.globals as G
import telemffb.utils as utils
import telemffb.xmlutils as xmlutils

import json
import os
from PyQt6.QtWidgets import QMessageBox, QPushButton
from configobj import ConfigObj
import textwrap


def convert_system_settings(sys_dict):
    map_dev_dict = {
        "logging_level": "logLevel",
        "telemetry_timeout": "telemTimeout",
    }

    map_sys_dict = {
        "ignore_auto_updates": "ignoreUpdate",
        "msfs_enabled": "enableMSFS",
        "dcs_enabled": "enableDCS",
        "il2_enabled": "enableIL2",
        "il2_telem_port": "portIL2",
        "il2_cfg_validation": "validateIL2",
        "il2_path": "pathIL2",
    }

    def_dev_dict, def_sys_dict = G.system_settings.defaults, G.system_settings.defaults

    sys_dict = utils.sanitize_dict(sys_dict)
    for (
        key,
        value,
    ) in sys_dict.items():  # iterate through the values in the ini user config
        if (
            key in map_dev_dict
        ):  # check if the key is in the new device specific settings
            new_key = map_dev_dict.get(
                key, None
            )  # get the translated key name from the map dictionary
            if (
                new_key is None
            ):  # should never be none since we already checked it existed.. but just in case..
                continue
            def_dev_dict[new_key] = (
                value  # write the old value to the new dictionary with the new key
            )

        elif (
            key in map_sys_dict
        ):  # elif check if the key is in the new system global settings
            new_key = map_sys_dict.get(
                key, None
            )  # get the translated key name from the map dictionary
            if (
                new_key is None
            ):  # should never be none since we already checked it existed.. but just in case..
                continue
            def_sys_dict[new_key] = (
                value  # write the old value to the new dictionary with the new key
            )

    for k, v in def_sys_dict.items():
        G.system_settings.setValue(k, v)

    for k, v in def_dev_dict.items():
        G.system_settings.setValue(k, v, instance=G.device_type)


def config_to_dict(section, name, value, isim="", device=G.device_type, new_ac=False):
    classes = [
        "PropellerAircraft",
        "JetAircraft",
        "TurbopropAircraft",
        "Glider",
        "Helicopter",
        "HPGHelicopter",
        "SASHelicopter",
    ]
    sim = ""
    cls = ""
    model = ""
    match section:
        case "system":
            sim = "Global"
        case "DCS":
            sim = "DCS"
        case "IL2":
            sim = "IL2"
        case "MSFS":
            sim = "MSFS"

    if "." in section:
        subsection = section.split(".")
        if (
            subsection[1] in classes
        ):  # Make sure it is actually a sim/class section and not a regex aircraft section
            ssim = subsection[0]
            cls = subsection[1]
            match ssim:
                case "DCS":
                    sim = "DCS"
                case "IL2":
                    sim = "IL2"
                case "MSFS":
                    sim = "MSFS"

    # if isim is present, is a new aircraft and user has responded with the sim information, add as new model
    if isim != "":
        model = section
        sim = isim
        cls = ""

    # if sim is still blank here, must be a default model section in the user config
    if sim == "":
        model = section
        sim = "any"
        cls = ""

    data_dict = {
        "name": name,
        "value": value,
        "sim": sim,
        "class": cls,
        "model": model,
        "device": device,
        "new_ac": new_ac,
    }
    # print(data_dict)
    return data_dict


def select_sim_for_conversion(window, aircraft_name):
    msg_box = QMessageBox(window)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setText(
        f"Please select the simulator to which '{aircraft_name}' from your user configuration belongs:"
    )
    msg_box.setWindowTitle("Simulator Selection")

    msfs_button = QPushButton("MSFS")
    dcs_button = QPushButton("DCS")
    il2_button = QPushButton("IL2")

    msg_box.addButton(msfs_button, QMessageBox.ButtonRole.YesRole)
    msg_box.addButton(dcs_button, QMessageBox.ButtonRole.NoRole)
    msg_box.addButton(il2_button, QMessageBox.ButtonRole.NoRole)

    result = msg_box.exec()

    if result == 0:  # MSFS button
        return "MSFS"
    elif result == 1:  # DCS button
        return "DCS"
    elif result == 2:  # IL2 button
        return "IL2"
    else:
        return None


def convert_settings(cfg, usr, window=None):
    differences = []
    defaultconfig = ConfigObj(cfg)
    userconfig = ConfigObj(usr, raise_errors=False)

    def_params = {
        section: utils.sanitize_dict(defaultconfig[section])
        for section in defaultconfig
    }
    try:
        usr_params = {
            section: utils.sanitize_dict(userconfig[section]) for section in userconfig
        }
    except Exception:
        QMessageBox.warning(
            window,
            "Conversion Error",
            "There was an error converting the config.  Please inspect the .ini config for syntax issues.\n\nMake sure all settings fall under a [section] and there are no spaces in any setting name",
        )
        return False

    sys = userconfig.get("system", None)
    for section in usr_params:
        if section == "system":
            convert_system_settings(usr_params[section])
            continue
        if section in def_params:
            # Compare common keys with different values
            for key, value in usr_params[section].items():
                if key in def_params[section] and def_params[section][key] != value:
                    value = 0 if value == "not_configured" else value
                    valuestring = str(value)
                    dif_item = config_to_dict(section, key, valuestring)
                    differences.append(dif_item)

            # Identify keys that exist only in the user configuration
            for key, value in usr_params[section].items():
                if key not in def_params[section]:
                    value = 0 if value == "not_configured" else value
                    valuestring = str(value)
                    dif_item = config_to_dict(section, key, valuestring)
                    differences.append(dif_item)
                    differences.append(dif_item)
        else:
            # All keys in the user configuration section are new
            # non matching sections must be new aircraft

            sim = select_sim_for_conversion(window, section)
            for key, value in usr_params[section].items():
                value = 0 if value == "not_configured" else value
                valuestring = str(value)
                if key == "type":
                    dev = "any"
                else:
                    dev = G.device_type
                dif_item = config_to_dict(
                    section, key, valuestring, isim=sim, device=dev, new_ac=True
                )
                differences.append(dif_item)

    xmlutils.write_converted_to_xml(differences)
    return True


def autoconvert_config(main_window, cfg, usr):
    if G.child_instance:
        return
    if usr is not None:
        ans = QMessageBox.information(
            main_window,
            "Important TelemFFB Update Notification",
            textwrap.dedent(
                f"""
                The 'ini' config file type is now deprecated.
            
                This version of TelemFFB uses a new UI-driven config model.
            
                It appears you are using a user override file ({usr}).  Would you
                like to auto-convert that file to the new config model?
            
                If you choose no, you may also perform the conversion from
                the Utilities menu.
            
                Proceeding will convert the config and re-name your
                existing user config to '{os.path.basename(usr)}.legacy'
            """
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if ans == QMessageBox.StandardButton.No:
            return
        if not os.path.isfile(usr):
            QMessageBox.warning(
                main_window,
                "Error",
                f"Legacy override file {usr} was passed at runtime for auto-conversion, but the file does not exist",
            )
            return
        # perform the conversion
        if not convert_settings(cfg=cfg, usr=usr, window=main_window):
            return False
        try:
            os.rename(usr, f"{usr}.legacy")
        except OSError:
            ans = QMessageBox.warning(
                main_window,
                "Warning",
                f'The legacy backup file for "{usr}" already exists, would you like to replace it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ans == QMessageBox.StandardButton.Yes:
                os.replace(usr, f"{usr}.legacy")

        QMessageBox.information(
            main_window,
            "Conversion Completed",
            """
            The conversion is complete.
            
            If you are utilizing multiple VPforce FFB enabled devices, please set up the auto-launch capabilities in the system settings menu.
            
            To avoid unnecessary log messages, please remove any '-c' or '-o' arguments from your startup shortcut as they are no longer supported""",
        )

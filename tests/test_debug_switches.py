"""The debug_* switches in telemffb.globals: each makes the app behave as a
user without that piece would see it, without touching the real machine.

* debug_ignore_rhino_devices - no VPforce device is enumerated.
* debug_hide_directlink - the DirectLink DLL is never loaded.
* debug_force_first_launch - settings and userconfig live in a sandbox the
  user-launched instance wipes, so every launch is a first launch.
"""
import os
import sys
import warnings
from unittest.mock import MagicMock

import pytest

import telemffb.globals as G
import telemffb.hw.ffb_dinput as ffb_dinput
import telemffb.hw.ffb_rhino as ffb_rhino_module
from telemffb.hw.ffb_rhino import FFBRhino

# see test_device_recovery.py: pre-import simconnect quietly before main
if sys.platform == "win32" and "simconnect" not in sys.modules:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ResourceWarning)
        import simconnect  # noqa: F401

try:    import main as main_module
except Exception:  # winreg is Windows-only
    main_module = None

pytestmark = [pytest.mark.unit]


class TestIgnoreRhinoDevices:
    def test_nothing_is_enumerated_and_hid_is_never_asked(self, monkeypatch):
        hid_enumerate = MagicMock(return_value=[])
        monkeypatch.setattr(ffb_rhino_module.hid, 'enumerate', hid_enumerate)
        monkeypatch.setattr(G, 'debug_ignore_rhino_devices', True)
        assert FFBRhino.enumerate() == []
        assert FFBRhino.enumerate(0x2055) == []
        hid_enumerate.assert_not_called()

    def test_off_by_default(self):
        assert G.debug_ignore_rhino_devices is False


class TestHideDirectLink:
    def test_the_bridge_reads_as_not_installed_without_loading_a_dll(self, monkeypatch):
        cdll = MagicMock()
        monkeypatch.setattr(ffb_dinput.ctypes, 'CDLL', cdll)
        monkeypatch.setattr(G, 'debug_hide_directlink', True)
        available, reason = ffb_dinput.bridge_availability(dll_path='anything.dll')
        assert not available
        assert 'not installed' in reason
        assert ffb_dinput.bridge_status(dll_path='anything.dll').installed is False
        cdll.assert_not_called()

    def test_off_by_default(self):
        assert G.debug_hide_directlink is False


@pytest.mark.skipif(main_module is None, reason="main.py requires winreg (Windows-only)")
class TestForceFirstLaunch:
    @pytest.fixture
    def sandbox(self, tmp_path, monkeypatch):
        monkeypatch.setenv('TEMP', str(tmp_path))
        monkeypatch.setattr(G, 'debug_force_first_launch', True)
        path = tmp_path / 'TelemFFB-first-launch'
        path.mkdir()
        (path / 'settings.ini').write_text('[General]\npidJoystick=2055\n')
        return path

    def _args(self, monkeypatch, child):
        monkeypatch.setattr(G, 'args', MagicMock(child=child), raising=False)

    def test_the_user_launched_instance_starts_from_nothing(self, sandbox, monkeypatch):
        self._args(monkeypatch, child=False)
        settings = main_module._open_system_settings()
        assert os.path.normcase(settings.fileName()) == \
            os.path.normcase(str(sandbox / 'settings.ini'))
        assert settings.value('pidJoystick') is None

    def test_a_child_keeps_what_the_master_set_up(self, sandbox, monkeypatch):
        self._args(monkeypatch, child=True)
        settings = main_module._open_system_settings()
        assert str(settings.value('pidJoystick')) == '2055'

    def test_userconfig_goes_to_the_sandbox(self, sandbox, monkeypatch):
        for name in ('dev_build', 'beta_build'):
            monkeypatch.setattr(G, name, False)
        monkeypatch.setattr(G, 'userconfig_rootpath', None, raising=False)
        monkeypatch.setattr(G, 'userconfig_path', None, raising=False)
        monkeypatch.setattr(G, 'defaults_path', None, raising=False)
        main_module._setup_config_paths()
        assert os.path.normcase(G.userconfig_path) == \
            os.path.normcase(str(sandbox / 'userconfig_v2.xml'))

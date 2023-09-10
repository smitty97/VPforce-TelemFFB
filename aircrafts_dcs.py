# 
# This file is part of the TelemFFB distribution (https://github.com/walmis/TelemFFB).
# Copyright (c) 2023 Valmantas Palikša.
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
 
import math
from random import randint
import time
from typing import List, Dict
from ffb_rhino import HapticEffect, FFBReport_SetCondition
import utils
import logging
import random
from aircraft_base import AircraftBase, effects, HPFs, LPFs
import json
import socket

#unit conversions (to m/s)
knots = 0.514444
kmh = 1.0/3.6
deg = math.pi/180


class Aircraft(AircraftBase):
    """Base class for Aircraft based FFB"""
    ####
    #### Beta effects - set to 1 to enable
    deceleration_effect_enable = 0
    deceleration_effect_enable_areyoureallysure = 0
    deceleration_max_force = 0.5
    ###
    buffeting_intensity : float = 0.2               # peak AoA buffeting intensity  0 to disable
    buffet_aoa : float          = 10.0              # AoA when buffeting starts
    stall_aoa : float           = 15.0              # Stall AoA
    wind_effect_enabled : int = 0

    engine_rumble : int = 0                         # Engine Rumble - Disabled by default - set to 1 in config file to enable
    
    runway_rumble_intensity : float = 1.0           # peak runway intensity, 0 to disable

    gun_vibration_intensity : float = 0.12          # peak gunfire vibration intensity, 0 to disable
    cm_vibration_intensity : float = 0.12           # peak countermeasure release vibration intensity, 0 to disable
    weapon_release_intensity : float = 0.12         # peak weapon release vibration intensity, 0 to disable
    weapon_effect_direction: int = 45               # Affects the direction of force applied for gun/cm/weapon release effect, Set to -1 for random direction
    
    speedbrake_motion_intensity : float = 0.12      # peak vibration intensity when speed brake is moving, 0 to disable
    speedbrake_buffet_intensity : float = 0.15      # peak buffeting intensity when speed brake deployed,  0 to disable

    spoiler_motion_intensity: float = 0.0  # peak vibration intensity when spoilers is moving, 0 to disable
    spoiler_buffet_intensity: float = 0.15  # peak buffeting intensity when spoilers deployed,  0 to disable
    
    gear_motion_intensity : float = 0.12      # peak vibration intensity when gear is moving, 0 to disable
    gear_buffet_intensity : float = 0.15      # peak buffeting intensity when gear down during flight,  0 to disable
    
    flaps_motion_intensity : float = 0.12      # peak vibration intensity when flaps are moving, 0 to disable
    flaps_buffet_intensity : float = 0.0      # peak buffeting intensity when flaps are deployed,  0 to disable
    
    canopy_motion_intensity : float = 0.12      # peak vibration intensity when canopy is moving, 0 to disable
    canopy_buffet_intensity : float = 0.0      # peak buffeting intensity when canopy is open during flight,  0 to disable

    afterburner_effect_intensity = 0.0      # peak intensity for afterburner rumble effect
    jet_engine_rumble_intensity = 0      # peak intensity for jet engine rumble effect
    jet_engine_rumble_freq = 45             # base frequency for jet engine rumble effect (Hz)

    ####
    #### Beta effects - set to 1 to enable
    gforce_effect_invert_force = 0  # case where "180" degrees does not equal "away from pilot"
    gforce_effect_enable = 0
    gforce_effect_enable_areyoureallysure = 0
    gforce_effect_curvature = 2.2
    gforce_effect_max_intensity = 1.0
    gforce_min_gs = 1.5  # G's where the effect starts playing
    gforce_max_gs = 5.0  # G limit where the effect maxes out at strength defined in gforce_effect_max_intensity

    ###
    ### AoA reduction force effect
    ###
    aoa_reduction_effect_enabled = 0
    aoa_reduction_max_force = 0.0
    critical_aoa_start = 22
    critical_aoa_max = 25

    pedal_spring_mode = 0    ## 0=DCS Default | 1=spring disabled (Heli)), 2=spring enabled at %100 (FW)
    elevator_droop_force = 0

    trim_workaround = False

    ####
    ####
    def __init__(self, name : str, **kwargs):
        super().__init__(name, **kwargs)

        self._jet_rumble_is_playing = 0
        self.spring_x = FFBReport_SetCondition(parameterBlockOffset=0)
        self.spring_y = FFBReport_SetCondition(parameterBlockOffset=1)

    def on_telemetry(self, telem_data : dict):
        ## Generic Aircraft Telemetry Handler
        """when telemetry frame is received, aircraft class receives data in dict format

        :param new_data: New telemetry data
        :type new_data: dict
        """

        try:
            j = json.loads(telem_data["MechInfo"])
            out = utils.flatten_dict(j, "", "_")
            for k, v in out.items():
                telem_data[k] = v
            del telem_data["MechInfo"]
        except:
            pass

        if not "AircraftClass" in telem_data:
            telem_data["AircraftClass"] = "GenericAircraft"   #inject aircraft class into telemetry

        self._telem_data = telem_data
        if telem_data.get("N") == None:
            return

        self._decel_effect(telem_data)
        self._update_buffeting(telem_data)
        self._update_runway_rumble(telem_data)
        self._update_cm_weapons(telem_data)
        self._update_ffb_forces(telem_data)
        self._update_speed_brakes(telem_data.get("speedbrakes_value"), telem_data.get("TAS"))
        self._update_landing_gear(telem_data.get("gear_value"), telem_data.get("TAS"))
        self._update_flaps(telem_data.get("Flaps"))
        self._update_canopy(telem_data.get("Canopy"))
        self._update_spoiler(telem_data.get("Spoilers"), telem_data.get("TAS"))
        self._update_jet_engine_rumble(telem_data)
        if self.is_joystick():
            self._update_stick_position(telem_data)
        if self.is_pedals():
            self.override_pedal_spring(telem_data)

    def on_event(self, event, *args):
        logging.info(f"on_event: {event}")
        if event == "Stop":
            effects.clear()

    def on_timeout(self):
        super().on_timeout()

    def send_commands(self, cmds):
        cmds = "\n".join(cmds)
        if not getattr(self, "_socket", None):
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        
        self._socket.sendto(bytes(cmds, "utf-8"), ("127.0.0.1", 34381))

    def override_pedal_spring(self, telem_data):

        ## 0=spring disabled + damper enabled, 1=spring enabled at %100 (overriding DCS) + damper
        if self.pedal_spring_mode == 0:
            return
        elif self.pedal_spring_mode == 1:
            self.spring_x.positiveCoefficient = 0
            self.spring_x.negativeCoefficient = 0
        elif self.pedal_spring_mode == 2:
            self.spring_x.positiveCoefficient = 4096
            self.spring_x.negativeCoefficient = 4096
        spring = effects["pedal_spring"].spring()

        spring.effect.setCondition(self.spring_x)
        # effects["damper"].damper(512, 512).start()
        spring.start(override=True)

    def _update_stick_position(self, telem_data):
        if not self.trim_workaround: return
        if not ("StickX" in telem_data and "StickY" in telem_data): return

        input_data = HapticEffect.device.getInput()
        x, y = input_data.axisXY()
        telem_data["X"] = x
        telem_data["Y"] = y

        self.spring_x.positiveCoefficient = 4096
        self.spring_x.negativeCoefficient = 4096
        self.spring_y.positiveCoefficient = 4096
        self.spring_y.negativeCoefficient = 4096

        # trim signal needs to be slow to avoid positive feedback
        lp_y = LPFs.get("y", 5)
        lp_x = LPFs.get("x", 5)

        # estimate trim from real stick position and virtual stick position
        offs_x = lp_x.update(telem_data['StickX'] - x + lp_x.value)
        offs_y = lp_y.update(telem_data['StickY'] - y + lp_y.value)
        
        self.spring_x.cpOffset = utils.clamp_minmax(round(offs_x * 4096), 4096)
        self.spring_y.cpOffset = utils.clamp_minmax(round(offs_y * 4096), 4096)

        spring = effects["trim_spring"].spring()
        # upload effect parameters to stick
        spring.effect.setCondition(self.spring_x)
        spring.effect.setCondition(self.spring_y)
        # ensure effect is started
        spring.start(override=True)

        # override DCS input and set our own values
        self.send_commands([f"LoSetCommand(2001, {y - offs_y})", 
                            f"LoSetCommand(2002, {x - offs_x})"])
                   

class PropellerAircraft(Aircraft):
    """Generic Class for Prop/WW2 aircraft"""

    engine_max_rpm = 2700                           # Assume engine RPM of 2700 at 'EngRPM' = 1.00 for aircraft not exporting 'ActualRPM' in lua script
    max_aoa_cf_force : float = 0.2 # CF force sent to device at %stall_aoa
    rpm_scale : float = 45
    pedal_spring_mode = 2    ## 0=DCS Default | 1=spring disabled + damper enabled, 2=spring enabled at %100 (overriding DCS) + damper
    jet_engine_rumble_intensity = 0

    # run on every telemetry frame
    def on_telemetry(self, telem_data):
        ## Propeller Aircraft Telemetry Handler
        if telem_data.get("N") == None:
            return
        telem_data["AircraftClass"] = "PropellerAircraft"   #inject aircraft class into telemetry
        if not "ActualRPM" in telem_data:
            rpm = telem_data.get("EngRPM", 0)
            if isinstance(rpm, list):
                rpm = [(x / 100) * self.engine_max_rpm for x in rpm]
            else:
                rpm = (rpm / 100) * self.engine_max_rpm
            telem_data["ActualRPM"] = rpm # inject ActualRPM into telemetry

        super().on_telemetry(telem_data)
        
        if self.is_joystick():
            self.override_elevator_droop(telem_data)

        if self.engine_rumble or self._engine_rumble_is_playing: # if _engine_rumble_is_playing is true, check if we need to stop it
            self._update_engine_rumble(telem_data["ActualRPM"])
        
        self._update_wind_effect(telem_data)
        self._update_aoa_effect(telem_data)
        self._gforce_effect(telem_data)



class JetAircraft(Aircraft):
    """Generic Class for Jets"""
    #flaps_motion_intensity = 0.0

    _ab_is_playing = 0
    pedal_spring_mode = 2    ## 0=DCS Default | 1=spring disabled + damper enabled, 2=spring enabled at %100 (overriding DCS) + damper

    jet_engine_rumble_intensity = 0.05
    afterburner_effect_intensity = 0.2
    
    # run on every telemetry frame
    def on_telemetry(self, telem_data):
        ## Jet Aircraft Telemetry Handler
        if telem_data.get("N")== None:
            return
        telem_data["AircraftClass"] = "JetAircraft"   #inject aircraft class into telemetry
        super().on_telemetry(telem_data)

        if self.afterburner_effect_intensity > 0:
            self._update_ab_effect(telem_data)
        if self.aoa_reduction_effect_enabled:
            self._aoa_reduction_force_effect(telem_data)
        if self.gforce_effect_enable:
            super()._gforce_effect(telem_data)

class Helicopter(Aircraft):
    """Generic Class for Helicopters"""
    buffeting_intensity = 0.0

    etl_start_speed = 6.0 # m/s
    etl_stop_speed = 22.0 # m/s
    etl_effect_intensity = 0.2 # [ 0.0 .. 1.0]
    etl_shake_frequency = 14.0 # value has been deprecated in favor of rotor RPM calculation
    overspeed_shake_start = 70.0 # m/s
    overspeed_shake_intensity = 0.2
    heli_engine_rumble_intensity = 0.12
    pedal_spring_mode = 1    ## 0=DCS Default | 1=spring disabled + damper enabled, 2=spring enabled at %100 (overriding DCS) + damper


    def on_telemetry(self, telem_data):
        self.speedbrake_motion_intensity = 0.0
        ## Helicopter Aircraft Telemetry Handler
        if telem_data.get("N") == None:
            return
        telem_data["AircraftClass"] = "Helicopter"   #inject aircraft class into telemetry
        super().on_telemetry(telem_data)

        self._calc_etl_effect(telem_data)
        if self.engine_rumble:
            self._update_heli_engine_rumble(telem_data)

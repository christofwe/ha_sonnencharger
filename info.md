[![Validate with hassfest](https://github.com/RustyDust/ha_sonnencharger/actions/workflows/hassfest.yml/badge.svg)](https://github.com/RustyDust/ha_sonnencharger/actions/workflows/hassfest.yml)
# ha_sonnencharger
HomeAssistant integration to provide sensors for the Sonnencharger (Etrel ITCH) wallbox

## sensor schema
All sensors added to HomeAssistant by this integration are grouped using the following scheme:

`sensor.sonnencharger_<serial>_conn<port>_l<phase>_<sensor>`

The following sensors are provided:

| sensor | function | type | unit |
|---|---|---|---|
| `active_session_duration` | active session duration | int | s |
| `active_session_imported_energy` | active session imported energy | float | W |
| `ev_max_phase_current` | max phase current used by BEV| float | A |
| `ev_max_power` | max power sent to BEV | float | kW |
| `ev_required_energy` | EV required energy | float | kW |
| `l1_active_power` | active power (L1) | float | kW |
| `l1_current` | active current (L1) | float | A |
| `l1_ln_voltage` | L-N voltage (L1) | float | V |
| `l1_phase` | real phase number of phase L1 | int | |
| `l2_active_power` | active Power (L2) | float | kW |
| `l2_current` | active current (L2) | float | A |
| `l2_ln_voltage` | L-N voltage (L2) | float | V |
| `l2_phase` | real phase number of phase L2 | int | |
| `l3_active_power` | active Power (L3) | float | kW |
| `l3_current` | active current (L3) | float | A |
| `l3_ln_voltage` | L-N voltage (L3) | float | V |
| `l3_phase` | real phase number of phase L3 | int | |
| `max_current` | max current supported by charger | float | A |
| `net_frequency` | net frequency | float | Hz |
| `num_phases` | number of available phases | int | |
| `power_factor` | ratio (imported power) / (charged power) | float | |
| `session_departure_time` | end time of last session (Unix seconds) | int | s |
| `session_id` | session id | string | |
| `state` | current charger state | string | |
| `state_numeric` | current charger state code | int | |
| `target_current` | target current for current charge | float | A |
| `total_active_power` | total active charging power (L1+L2+L3)| float | kW |
| `type` | type of cable to vehicle | string | |
| `type_numeric` | type of cable to vehicle (numeric code) | int | |
| `vehicle_connected_phases` | number of phases connected to vehicle | string | |
| `vehicle_connected_phases_code` | number of phases connected to vehicle (numeric code) | int | |

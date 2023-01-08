import traceback
import threading
import time

from .const import *
from .mappings import FriendlyMap, DeviceMap, UnitMap

from homeassistant.helpers import config_validation as cv

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass
)

from sonnencharger import sonnencharger

from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
    CONF_SCAN_INTERVAL,
)

async def async_setup_entry(hass, config_entry, async_add_entities):
  """Set up the sensor platform."""
  LOGGER.info('SETUP_ENTRY')

  sc_host   = config_entry.data.get(CONF_IP_ADDRESS)
  sc_port   = config_entry.data.get(CONF_PORT)
  sc_update = config_entry.data.get(CONF_SCAN_INTERVAL)
  sc_debug  = config_entry.data.get(ATTR_SONNEN_DEBUG)

  LOGGER.info("{0} - INTERVAL: {1}".format(DOMAIN, sc_update))

  def _internal_setup(_sc_host,_sc_port):
    return sonnencharger(_sc_host,_sc_port)

  Charger = await hass.async_add_executor_job(_internal_setup, sc_host, sc_port)

  charger_sysinfo = await hass.async_add_executor_job(Charger.get_sysinfo)
  serial  = charger_sysinfo["serial"]

  sensor = SonnenChargerSensor(id = "sensor.{0}_{1}".format(DOMAIN, serial))
  async_add_entities([sensor])

  monitor = SonnenChargerMonitor(hass, Charger, sensor, async_add_entities, sc_update, sc_debug)
  hass.data[DOMAIN][config_entry.entry_id] = {"monitor": monitor}
  monitor.start()

  def _stop_monitor(_event):
    monitor.stopped = True
    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, _stop_monitor)
    LOGGER.info('Init done')
    return True

class SonnenChargerSensor(SensorEntity):
  def __init__(self, id, name = None):
    self._attributes  = {}
    self._state       = "NOTRUN"
    self.entity_id    = id
    if name is None:
      name        = id
    self._name  = name
    LOGGER.info("Create Sensor {0}".format(id))

  def set_state(self, state):
    """Set the state."""
    if self._state == state:
      return
    self._state = state
    try:
      self.schedule_update_ha_state()
    except:
      LOGGER.error("Failing sensor: "+self.name)

  def set_attributes(self, attributes):
    """Set the state attributes."""
    self._attributes = attributes

  @property
  def unique_id(self) -> str:
    """Return the unique ID for this sensor."""
    return self.entity_id

  @property
  def should_poll(self):
    """Only poll to update phonebook, if defined."""
    return False

  @property
  def device_state_attributes(self):
    """Return the state attributes."""
    return self._attributes

  @property
  def state(self):
    """Return the state of the device."""
    return self._state

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  def update(self):
      LOGGER.info("update "+self.entity_id)
      """Update the phonebook if it is defined."""

  @property
  def unit_of_measurement(self):
    """Return the unit of measurement."""
    return self._attributes.get("unit_of_measurement", None)

  @property
  def device_class(self):
    """Return the device_class."""
    return self._attributes.get("device_class", None)

  @property
  def state_class(self):
    """Return the unit of measurement."""
    return self._attributes.get("state_class", None)


class SonnenChargerMonitor:
  def __init__(self, hass, charger, sensor, async_add_entities, updateInterval, debug_mode):
      self.hass               = hass
      self.latestData         = {}
      self.disabledSensors    = [""]

      self.stopped            = False
      self.sensor             = sensor
      self.charger:           sonnencharger = charger
      self.meterSensors       = {}
      self.updateInterval     = updateInterval
      self.async_add_entities = async_add_entities
      self.debug              = debug_mode

  def start(self):
    threading.Thread(target=self.watcher).start()

  def updateData(self):
    try:
      self.latestData["sys_info"]   = self.charger.get_sysinfo()
      self.latestData["connectors"] = self.charger.get_connectors()
    except:
      e = traceback.format_exc()
      LOGGER.error(e)
      return

  def setupEntities(self):
    self.updateData()
    self.AddOrUpdateEntities()

  def watcher(self):
    LOGGER.info('Start Watcher Thread:')

    while not self.stopped:
      try:
        self.updateData()
        self.AddOrUpdateEntities()
        self.sensor.set_attributes(self.latestData["sys_info"])
      except:
        e = traceback.format_exc()
        LOGGER.error(e)

      if self.updateInterval is None:
        self.updateInterval = DEFAULT_SCAN_INTERVAL

      time.sleep(max(1, self.updateInterval))

  def _AddOrUpdateEntity(self, id, friendlyname, value, unit, device_class):
    if id in self.meterSensors:
      sensor = self.meterSensors[id]
      sensor.set_state(value)
    else:
      sensor = SonnenChargerSensor(id, friendlyname)
      sensor.set_attributes(
        {
          "unit_of_measurement":  unit,
          "device_class":         device_class,
          "friendly_name":        friendlyname,
          "state_class":          "measurement"
        }
      )
      self.async_add_entities([sensor])
      self.meterSensors[id] = sensor

  def AddOrUpdateEntities(self):
    sysinfo     = self.latestData["sys_info"]
    connectors  = self.latestData["connectors"]

    serial = sysinfo['serial']
    prefix = "sensor.{}_{}_".format(DOMAIN, serial)

    for connector in connectors:
      for entity in connectors[connector]:
        self._AddOrUpdateEntity(
          id            = "{}conn{}_{}".format(prefix, connector, entity),
          friendlyname  = FriendlyMap[entity] if entity in FriendlyMap else entity,
          value         = connectors[connector][entity],
          unit          = UnitMap[entity] if entity in UnitMap else '',
          device_class  = DeviceMap[entity] if entity in DeviceMap else SensorDeviceClass.POWER
      )

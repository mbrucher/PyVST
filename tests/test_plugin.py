#!/usr/bin/env python

from pyvst import *

def test_load():
  plugin = VSTPlugin("again.dll")

def test_check_magic():
  plugin = VSTPlugin("again.dll")
  assert plugin._VSTPlugin__effect.magic == (ord("V") << 24) + (ord("s") << 16) + (ord("t") << 8) + ord("P")

def test_basic_info():
  plugin = VSTPlugin("again.dll")
  assert plugin.get_name() == "Gain"
  assert plugin.get_vendor() == "Steinberg Media Technologies"
  assert plugin.get_product() == "Gain"

def test_open_close():
  plugin = VSTPlugin("again.dll")
  plugin.open()
  plugin.close()
  
def test_resume_suspend():
  plugin = VSTPlugin("again.dll")
  plugin.resume()
  plugin.suspend()

def test_properties():
  plugin = VSTPlugin("again.dll")
  plugin.open()

  assert plugin.number_of_programs == 1
  assert plugin.number_of_parameters == 1
  assert plugin.number_of_inputs == 2
  assert plugin.number_of_outputs == 2

def test_parameters():
  plugin = VSTPlugin("again.dll")
  plugin.set_parameter(1, 0.)
  assert plugin.get_parameter(1) == 0.
  plugin.set_parameter(1, 1.)
  assert plugin.get_parameter(1) == 1.

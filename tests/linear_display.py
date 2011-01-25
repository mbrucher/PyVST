#!/usr/bin/env python

import matplotlib.pyplot as pyplot
import numpy

from pyvst import *

SampleRate = 96000
Samples = 2**21

def raise_gui(plugin):
  import wx

  app = wx.App()
  frame = wx.Frame(None, -1, "Plugin editor")

  plugin.open_edit(frame.GetHandle())
  rect = plugin.get_erect()
  frame.SetClientSize((rect.right, rect.bottom))
  frame.Show()
  app.MainLoop()

def display(plugin, type):
  input1 = numpy.random.randn(Samples).astype(numpy.float32)
  input2 = input1[::-1].flatten()
  output = numpy.zeros((plugin.number_of_outputs, Samples), dtype=type)

  for i in range(Samples/2048):
    plugin.process([input1[i*2048:(i+1)*2048], input2[i*2048:(i+1)*2048]] * (plugin.number_of_inputs / 2), output[:, i*2048:(i+1)*2048])

  return (input1, input2), output

def plot(inputs, outputs):
  x= SampleRate * numpy.arange(Samples/2.) / Samples
  pyplot.figure()
  a = pyplot.subplot(2, 2, 1)
  a.grid(True)
  pyplot.title("Input L")
  pyplot.loglog(x, numpy.abs(numpy.fft.fft(inputs[0])[:Samples/2]))
  #pyplot.plot(inputs[0])
  a = pyplot.subplot(2, 2, 2)
  a.grid(True)
  pyplot.title("Input R")
  pyplot.loglog(x, numpy.abs(numpy.fft.fft(inputs[1])[:Samples/2]))
  #pyplot.plot(inputs[1])

  a = pyplot.subplot(2, 2, 3)
  a.grid(True)
  pyplot.title("Output L")
  pyplot.loglog(x, numpy.abs(numpy.fft.fft(outputs[0])[:Samples/2]))
  #pyplot.plot(outputs[0])
  a = pyplot.subplot(2, 2, 4)
  a.grid(True)
  pyplot.title("Output R")
  pyplot.loglog(x, numpy.abs(numpy.fft.fft(outputs[1])[:Samples/2]))
  #pyplot.plot(outputs[1])

import sys

if len(sys.argv) > 1:
  plugin = VSTPlugin(sys.argv[1])
else:
  plugin = VSTPlugin("again.dll")

plugin.open()
plugin.set_sample_rate(SampleRate)
plugin.set_block_size(2048)

if plugin.has_editor():
  raise_gui(plugin)

dump_effect_properties(plugin)

plugin.resume()

if plugin.can_process_double():
  print "Testing with doubles (64bits)"
  inputs, outputs = display(plugin, numpy.float64)
else:
  print "Testing with floats (32bits)"
  inputs, outputs = display(plugin, numpy.float32)
plot(inputs, outputs)
pyplot.show()

plugin.suspend()

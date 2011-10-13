#!/usr/bin/env python

import time

import matplotlib.pyplot as pyplot
import numpy

from pyvst import *

SampleRate = 96000
Samples = 2000000
FreqMax = 20000

def raise_gui(plugin):
  import wx

  app = wx.App()
  frame = wx.Frame(None, -1, "Plugin editor")

  plugin.open_edit(frame.GetHandle())
  rect = plugin.get_erect()
  frame.SetClientSize((rect.right, rect.bottom))
  frame.Show()
  app.MainLoop()
  plugin.close_edit()

def display(plugin, type):
  t = numpy.arange(Samples, dtype=type) / SampleRate

  input1 = numpy.sin(numpy.pi * (SampleRate * FreqMax / Samples * (t + .1)) * t)
  input2 = input1[::-1].flatten()
  output = numpy.zeros((plugin.number_of_outputs, Samples), dtype=type)

  start = time.time()
  for i in range(Samples/2048):
    plugin.process([input1[i*2048:(i+1)*2048], input2[i*2048:(i+1)*2048]], output[:, i*2048:(i+1)*2048])
  print "Elapsed time:", (time.time() - start)

  return (input1, input2), output

def plot(inputs, outputs, NFFT = 8192, noverlap = 1024):
  pyplot.figure()
  a = pyplot.subplot(2, len(outputs), 1)
  pyplot.title("Input L")
  pyplot.specgram(inputs[0], NFFT = NFFT, Fs = SampleRate, noverlap = noverlap )
  #pyplot.plot(inputs[0])
  if len(outputs) > 1:
    a = pyplot.subplot(2, 2, 2)
    pyplot.title("Input R")
    pyplot.specgram(inputs[1], NFFT = NFFT, Fs = SampleRate, noverlap = noverlap )
    #pyplot.plot(inputs[1])

  a = pyplot.subplot(2, len(outputs), len(outputs) + 1)
  pyplot.title("Output L")
  pyplot.specgram(outputs[0], NFFT = NFFT, Fs = SampleRate, noverlap = noverlap )
  #pyplot.plot(outputs[0])
  if len(outputs) > 1:
    a = pyplot.subplot(2, 2, 4)
    pyplot.title("Output R")
    pyplot.specgram(outputs[1], NFFT = NFFT, Fs = SampleRate, noverlap = noverlap )
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

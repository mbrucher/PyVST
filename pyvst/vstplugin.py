#!/usr/bin/env python

import numpy
from ctypes import CDLL, POINTER

from aeffect import *

kVstVersion = 2400

class VstAEffectFlags(object):
  effFlagsHasEditor     = 1 << 0
  effFlagsCanReplacing  = 1 << 4
  effFlagsProgramChunks = 1 << 5
  effFlagsIsSynth       = 1 << 8
  effFlagsNoSoundInStop = 1 << 9
  effFlagsCanDoubleReplacing = 1 << 12

class AEffectOpcodes(object):
  effOpen = 0
  effClose = 1

  effSetProgram = 2
  effGetProgram = 3
  effSetProgramName = 4
  effGetProgramName = 5

  effGetParamLabel = 6
  effGetParamDisplay = 7
  effGetParamName = 8

  effSetSampleRate = 10
  effSetBlockSize = 11
  effMainsChanged = 12

  effEditGetRect = 13
  effEditOpen = 14
  effEditClose = 15

  effEditIdle = 19
 
  effGetChunk = 23
  effSetChunk = 24
 
  effNumOpcodes = 25

class AEffectXOpcodes(object):
  effProcessEvents = 25
  effCanBeAutomated = 26
  effString2Parameter = 27

  effGetProgramNameIndexed = 29
 
  effGetInputProperties = 33
  effGetOutputProperties = 34
  effGetPlugCategory = 35

  effOfflineNotify = 38
  effOfflinePrepare = 39
  effOfflineRun = 40
  effProcessVarIo = 41
  effSetSpeakerArrangement = 42

  effSetBypass = 44
  effGetEffectName = 45

  effGetVendorString = 47
  effGetProductString = 48
  effGetVendorVersion = 49
  effVendorSpecific = 50
  effCanDo = 51
  effGetTailSize = 52

  effGetParameterProperties = 56
  effGetVstVersion = 58

  effEditKeyDown = 59
  effEditKeyUp = 60
  effSetEditKnobMode = 61

  effGetMidiProgramName = 62
  effGetCurrentMidiProgram = 63
  effGetMidiProgramCategory = 64
  effHasMidiProgramsChanged = 65
  effGetMidiKeyName = 66
 
  effBeginSetProgram = 67
  effEndSetProgram = 68

  effGetSpeakerArrangement = 69
  effShellGetNextPlugin = 70

  effStartProcess = 71
  effStopProcess = 72
  effSetTotalSampleToProcess = 73
  effSetPanLaw = 74
 
  effBeginLoadBank = 75
  effBeginLoadProgram = 76

  effSetProcessPrecision = 77
  effGetNumMidiInputChannels = 78
  effGetNumMidiOutputChannels = 79

class AudioMasterOpcodes(object):
  audioMasterAutomate = 0
  audioMasterVersion = 1
  audioMasterCurrentId = 2
  audioMasterIdle = 3

def basic_callback(effect, opcode, index, value, ptr, opt):
  """
  Basic callback
  """
  if opcode == AudioMasterOpcodes.audioMasterVersion:
    return kVstVersion
  return 0

class VSTPlugin(object):
  """
  An actual VST plugin wrapper
  """
  def __init__(self, filename, audio_callback = basic_callback):
    """
    Constructor
    Parameters:
      filename is the name of the plugin to load
      audio_callback is the Python function to call (optional)
    """
    self.__lib = CDLL(filename)
    self.__callback = audiomaster_callback(audio_callback)

    try:
      self.__lib.VSTPluginMain.argtypes = [audiomaster_callback, ]
      self.__lib.VSTPluginMain.restype = POINTER(AEffect)
      self.__effect = self.__lib.VSTPluginMain(self.__callback).contents
    except AttributeError:
      self.__lib.main.argtypes = [audiomaster_callback, ]
      self.__lib.main.restype = POINTER(AEffect)
      self.__effect = self.__lib.main(self.__callback).contents

    self.__populate_methods()
  
  def __populate_methods(self):
    self.dispatcher = create_dispatcher_proc(self.__effect.dispatcher)
    self.__process_replacing = create_process_proc(self.__effect.processReplacing)
    if(self.__effect.processDoubleReplacing):
      self.__process_double_replacing = create_process_double_proc(self.__effect.processDoubleReplacing)
    self.__set_param = create_set_param_proc(self.__effect.setParameter)
    self.__get_param = create_get_param_proc(self.__effect.getParameter)

  def open(self):
    return self.dispatcher(byref(self.__effect), AEffectOpcodes.effOpen, 0, 0, None, 0)

  def close(self):
    return self.dispatcher(byref(self.__effect), AEffectOpcodes.effClose, 0, 0, None, 0)

  def open_edit(self, window = None):
    return self.dispatcher(byref(self.__effect), AEffectOpcodes.effEditOpen, 0, 0, window, 0)

  def close_edit(self):
    return self.dispatcher(byref(self.__effect), AEffectOpcodes.effEditClose, 0, 0, None, 0)
  
  def get_erect(self):
    rect = POINTER(ERect)()
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effEditGetRect, 0, 0, byref(rect), 0)
    return rect.contents
    
  def set_sample_rate(self, sample_rate):
	  return self.dispatcher(byref(self.__effect), AEffectOpcodes.effSetSampleRate, 0, 0, None, sample_rate)

  def set_block_size(self, block_size):
	  return self.dispatcher(byref(self.__effect), AEffectOpcodes.effSetBlockSize, 0, block_size, None, 0)

  def process_replacing(self, inputs, outputs):
    f4ptr = POINTER(c_float)
    float_input_pointers = (f4ptr*len(inputs))(*[row.ctypes.data_as(f4ptr) for row in inputs])
    float_output_pointers = (f4ptr*len(outputs))(*[row.ctypes.data_as(f4ptr) for row in outputs])
    self.__process_replacing(byref(self.__effect), float_input_pointers, float_output_pointers, len(inputs[0]))

  def process_double_replacing(self, inputs, outputs):
    d4ptr = POINTER(c_double)
    double_input_pointers = (d4ptr*len(inputs))(*[row.ctypes.data_as(d4ptr) for row in inputs])
    double_output_pointers = (d4ptr*len(outputs))(*[row.ctypes.data_as(d4ptr) for row in outputs])
    self.__process_double_replacing(byref(self.__effect), double_input_pointers, double_output_pointers, len(inputs[0]))

  def process(self, inputs, outputs):
    if inputs[0].dtype == numpy.float32:
      self.process_replacing(inputs, outputs)
    else:
      self.process_double_replacing(inputs, outputs)
    
  def set_parameter(self, index, value):
    return self.__set_param(byref(self.__effect), index, value)
  
  def get_parameter(self, index):
    return self.__get_param(byref(self.__effect), index)

  def get_name(self):
    name = c_char_p('\0' * VstStringConstants.kVstMaxEffectNameLen)
    self.dispatcher(byref(self.__effect), AEffectXOpcodes.effGetEffectName, 0, 0, name, 0.)
    return name.value

  def get_vendor(self):
    name = c_char_p('\0' * VstStringConstants.kVstMaxVendorStrLen)
    self.dispatcher(byref(self.__effect), AEffectXOpcodes.effGetVendorString, 0, 0, name, 0.)
    return name.value

  def get_product(self):
    name = c_char_p('\0' * VstStringConstants.kVstMaxProductStrLen)
    self.dispatcher(byref(self.__effect), AEffectXOpcodes.effGetProductString, 0, 0, name, 0.)
    return name.value

  def get_number_of_programs(self):
    return self.__effect.numPrograms

  number_of_programs = property(get_number_of_programs)
  
  def get_number_of_parameters(self):
    return self.__effect.numParams

  number_of_parameters = property(get_number_of_parameters)

  def get_number_of_inputs(self):
    return self.__effect.numInputs

  number_of_inputs = property(get_number_of_inputs)

  def get_number_of_outputs(self):
    return self.__effect.numOutputs

  number_of_outputs = property(get_number_of_outputs)

  def get_program_name_indexed(self, index):
    name = c_char_p('\0' * VstStringConstants.kVstMaxProgNameLen)
    if self.dispatcher(byref(self.__effect), AEffectXOpcodes.effGetProgramNameIndexed, index, 0, name, 0.):
      raise IndexError("No program with this index (%d)" % index)
    return name.value

  def set_program(self, index):
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effSetProgram, index, 0, None, 0.)

  def get_program_name(self):
    name = c_char_p('\0' * VstStringConstants.kVstMaxProgNameLen)
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effGetProgramName, 0, 0, name, 0.)
    return name.value

  def get_parameter_name(self, index):
    name = c_char_p('\0' * VstStringConstants.kVstMaxParamStrLen)
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effGetParamName, index, 0, name, 0.)
    return name.value

  def get_parameter_label(self, index):
    name = c_char_p('\0' * VstStringConstants.kVstMaxParamStrLen)
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effGetParamLabel, index, 0, name, 0.)
    return name.value

  def get_parameter_display(self, index):
    name = c_char_p('\0' * VstStringConstants.kVstMaxParamStrLen)
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effGetParamDisplay, index, 0, name, 0.)
    return name.value

  def suspend(self):
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effMainsChanged, 0, 0, None, 0.)

  def resume(self):
    self.dispatcher(byref(self.__effect), AEffectOpcodes.effMainsChanged, 0, 1, None, 0.)

  def can_process_double(self):
    return (self.__effect.flags & VstAEffectFlags.effFlagsCanDoubleReplacing) == VstAEffectFlags.effFlagsCanDoubleReplacing

  def has_editor(self):
    return (self.__effect.flags & VstAEffectFlags.effFlagsHasEditor) == VstAEffectFlags.effFlagsHasEditor
    
def dump_effect_properties(effect):
  """
  Dump on the screen every thing about the effect properties
  """
  print "Plugin name:", effect.get_name()
  print "Vendor name:", effect.get_vendor()
  print "Product name:", effect.get_product()
  
  print "numPrograms = %d\nnumParams = %d\nnumInputs = %d\nnumOutputs = %d\n"% (effect.number_of_programs, effect.number_of_parameters, effect.number_of_inputs, effect.number_of_outputs)

  for program_index in range(effect.number_of_programs):
    try:
      program_name = effect.get_program_name_indexed(program_index)
      effect.set_program(program_index)
      program_name = effect.get_program_name()
      print "Program %03d: %s" % (program_index, program_name)
    except:
      pass

  for param_index in range(effect.number_of_parameters):
    param_name = effect.get_parameter_name(param_index)
    param_display = effect.get_parameter_display(param_index)
    param_label = effect.get_parameter_label(param_index)
    value = effect.get_parameter(param_index)
    print "Param %03d: %s [%s %s] (normalized = %f)" % (param_index, param_name, param_display, param_label, value)
    

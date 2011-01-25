#!/usr/bin/env python

class VstStringConstants(object):
  kVstMaxProgNameLen = 24
  kVstMaxParamStrLen = 8
  kVstMaxVendorStrLen = 64
  kVstMaxProductStrLen = 64
  kVstMaxEffectNameLen = 32

from ctypes import *

class AEffect(Structure):
  _fields_ = [
                    ('magic', c_int),
                    ('dispatcher', c_void_p),
                    ('process', c_void_p),
                    ('setParameter', c_void_p),
                    ('getParameter', c_void_p),
                    ('numPrograms', c_int),
                    ('numParams', c_int),
                    ('numInputs', c_int),
                    ('numOutputs', c_int),
                    ('flags', c_int),
                    ('resvd1', c_void_p),
                    ('resvd2', c_void_p),
                    ('initialDelay', c_int),
                    ('realQualities', c_int),
                    ('offQualities', c_int),
                    ('ioRatio', c_float),
                    ('object', c_void_p),
                    ('user', c_void_p),
                    ('uniqueID', c_int),
                    ('version', c_int),
                    ('processReplacing', c_void_p),
                    ('processDoubleReplacing', c_void_p),
                    ]

class ERect(Structure):
  _fields_ = [
                    ('top', c_short),
                    ('left', c_short),
                    ('bottom', c_short),
                    ('right', c_short),
             ]

audiomaster_callback = CFUNCTYPE(c_void_p, POINTER(AEffect), c_int, c_int, c_long, c_void_p, c_float)

def create_dispatcher_proc(pointer):
  prototype = CFUNCTYPE(c_void_p, POINTER(AEffect), c_int, c_int, c_long, c_void_p, c_float)
  return prototype(pointer)

def create_process_proc(pointer):
  prototype = CFUNCTYPE(None, POINTER(AEffect), POINTER(POINTER(c_float)), POINTER(POINTER(c_float)), c_int)
  return prototype(pointer)

def create_process_double_proc(pointer):
  prototype = CFUNCTYPE(None, POINTER(AEffect), POINTER(POINTER(c_double)), POINTER(POINTER(c_double)), c_int)
  return prototype(pointer)

def create_set_param_proc(pointer):
  prototype = CFUNCTYPE(None, POINTER(AEffect), c_int, c_float)
  return prototype(pointer)

def create_get_param_proc(pointer):
  prototype = CFUNCTYPE(c_float, POINTER(AEffect), c_int)
  return prototype(pointer)

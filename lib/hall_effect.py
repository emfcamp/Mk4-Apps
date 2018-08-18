"""Library for sleep related functions"""

import machine


_adc = None
def hall_effect_adc():
    global _adc
    if not _adc:
        _adc = machine.ADC(machine.ADC.ADC_HALLEFFECT)
    return _adc

def get_flux():
    return hall_effect_adc().convert() # todo: convert this into something meaningful



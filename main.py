# Copyright 2018
#
# Ahmet Can Mert <ahmetcanmert@sabanciuniv.edu>
# Hasan Azgin    <hasanazgin@sabanciuniv.edu>
# Ercan Kalali   <ercankalali@sabanciuniv.edu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mcm import *

# bit_size_signed: bit-size of signed input variable
# coefficients   : list of UNSIGNED coefficients

# Input
bit_size_signed = 8
constants       = [4,8,9,5748,25,22,87,974,11,44,86746874,212454575487857]

# MCM operation
[MAPPED, POWER2, SHIFTED, NOT_MAPPED, CONSTANTS] = dsp_mapping(bit_size_signed,constants)

# print information
print "--------------------------------------------"
print
print "Input bit size :",bit_size_signed
print "Input constants:",constants
print
print str(len(CONSTANTS))+" constants are generated using "+str(len(MAPPED))+" DSP blocks."
print
print "Constants generated:"
for i in range(len(MAPPED)):
    print "* DSP #"+str(i)+":",MAPPED[i]
print
print "Constants as power-of-two:", [y[1] for y in POWER2]
print "Constants shifted        :", [(str(z[1])+" from "+str(z[0])) for z in SHIFTED]
print "Constants not mapped     :", NOT_MAPPED
print
print "--------------------------------------------"

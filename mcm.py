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

import math
import itertools
import sys

from generatemodule import *

sys.setrecursionlimit(10000)

# This function checks if given coefficients can be mapped on DSP
def cost_calculation(x, coefficients):
    cost = 0
    coefficient_num = len(coefficients)

    if (coefficient_num != 0):
        for i in range(coefficient_num):
            if(coefficients[i] != 0):
                cost += coeff_cost(coefficients[i])

        cost = cost + x * (coefficient_num - coefficients.count(0) - 1)

        if(cost > 24):
            dsp_map = 0
        else:
            dsp_map = 1
    return dsp_map

# This function makes partitioning
def getNextGroup(coefficients, coefficient_num, maxCpD, minND, x, DSP_list, check_combination, combination_counter, level):
    coefficients.sort(reverse=True)
    combination_arr = (list((itertools.combinations(coefficients, maxCpD))))

    if(check_combination == 1):
        for idx in range(combination_counter[level]):
            combination_arr.remove(combination_arr[0])

    if(coefficient_num >= maxCpD):
        for idx in range(len(combination_arr)):
            i = combination_arr[idx]

            dsp_map = cost_calculation(x, i)

            if(dsp_map == 1):
                DSP_list.append(i)
                for j in range(len(i)):
                    coefficients.remove(i[j])

                coefficient_num = coefficient_num-maxCpD

                return getNextGroup(coefficients, coefficient_num, maxCpD, minND, x, DSP_list, 0, combination_counter, level+1)
            else:
                if(i == combination_arr[len(combination_arr)-1]):
                    combination_counter[level-1] = combination_counter[level-1] + 1

                    if(len(DSP_list) > 0):
                        DSP_list_last = DSP_list[len(DSP_list)-1]
                        DSP_list.remove(DSP_list_last)

                        for j in range(len(DSP_list_last)):
                            coefficients.insert(j,DSP_list_last[j])
                            coefficient_num = coefficient_num+maxCpD

                        combination_counter[level] = 0

                        return getNextGroup(coefficients, coefficient_num, maxCpD, minND, x, DSP_list, 1, combination_counter, level-1)
                else:
                    a = 1 # DUMMY CASE

    return DSP_list, coefficient_num

# This function calculates the cost of a coefficient
def coeff_cost(c):
    c_temp = c
    n = 0

    while (c_temp % 2 == 0):
        c_temp = c_temp / 2

    # cost = len(bin(c_temp)[2:]) # Bit size of odd coefficient # THIS IS NOT CORRECT
    cost = int(math.ceil(math.log(c_temp,2))) # Bit size of odd coefficient

    c_temp = c_temp - 1

    if (c_temp == 0):
        n = 0
    else:
        while (c_temp % 2 == 0):
            n = n + 1
            c_temp =c_temp / 2

    cost = cost - n # Subtract rewiring cost

    return cost

# This function calculates the bit-length of the odd-coefficient
def output_cost(c):
    c_temp = int(c)

    while (c_temp % 2 == 0):
        c_temp = c_temp / 2

    c_temp = c_temp - 1

    if (c_temp != 0):
        while (c_temp % 2 == 0):
            c_temp =c_temp / 2

    cost = len(bin(c_temp)[2:]) # Subtract rewiring cost
    # cost = int(math.ceil(math.log(c_temp,2))) # Subtract rewiring cost

    return cost

# This function checks if one input can be obtained from other input using shift operation
def shift_check(a,b):
    c1 = max(a,b)
    c2 = min(a,b)

    num = (c1/(c2*1.0))

    if(num.is_integer()):
        num = int(num)
        return num != 0 and ((num & (num - 1)) == 0)
    else:
        return False

# This function performs map operation of coefficients on DSP blocks
def dsp_mapping(x, coefficients):
    # 'x' is the bit length of input
    # 'coefficients' are constant coefficients

    DSP_list = []       # Coefficients mapped on DSP
    DSP_list_nm = []    # Coefficients cannot mapped on single DSP
    DSP_list_sh = []    # Coefficients only needs a shift operation
    DSP_list_2p = []    # Coefficients as 2^n

    # Removing duplicate elements from the coefficient array
    coefficient_u = list(set(coefficients))

    # Removing '0' in the coefficients
    for i in range(len(coefficient_u)):
        coefficient_u = list(filter(lambda a: a != 0, coefficient_u))

    # List of all necessary coefficients (NOTMAPPED should be removed)
    DSP_list_co = list(sorted(coefficient_u))

    # Will be used to remove redundant constants
    coefficient_array = [(0, 0)] * len(coefficient_u)

    # Calculate costs for each coefficient
    for i in range(len(coefficient_u)):
        coefficient_array[i] = [(coefficient_u[i]), (coeff_cost(coefficient_u[i]))]

    # Update coefficient_num
    coefficient_num = len(coefficient_u)

    combination_counter = []
    coefficients_org = []

    ##############################################
    # C = 2^l * (1 + c*2^n)
    # Cost of this constant: bit_size(1 + c*2^n) - n
    # Output cost of this constant: x + bit_size(1 + c*2^n) - n
    ##############################################
    # Total cost for single constant: c1
    # Total cost for two constants  : x + c1 + c2
    # Total cost for three constants: 2*x + c1 + c2 + c3
    # ...
    # If x > 12, 2*x> 24 -> 2 constants at most
    # If x > 8 , 3*x> 24 -> 3 constants at most
    # If x > 6 , 4*x> 24 -> 4 constants at most
    # If x > 4 , 6*x> 24 -> 6 constants at most
    # If x > 3 , 8*x> 24 -> 8 constants at most
    # If x > 2 , 12*x> 24 -> 12 constants at most
    # If x > 1 , 24*x> 24 -> 24 constants at most
    # ...
    # COST = x*(number of coefficients - 1) + sum(c values)
    ##############################################
    # A input is calculated as for 2 constants:
    # c1 + c2*2^(x+c1)
    # A input is calculated as for 2 constants:
    # c1 + c2*2^(x+c1) + c3*2^(2*x+c1+c2)
    ##############################################

    if(x > 25): # This may be restricted
        # Sort coefficients in increasing (ascending) order in terms of their value
        coefficient_array = sorted(coefficient_array, key=lambda x: x[0])

        # Removes the numbers 2^n
        for i in reversed(range(coefficient_num)):
            if (int(coefficient_array[i][0]) != 0 and ((int(coefficient_array[i][0]) & (int(coefficient_array[i][0]) - 1)) == 0)):
                DSP_list_2p.append([1, int(coefficient_array[i][0])])
                del coefficient_array[i]

        # Update coefficient_num
        coefficient_num = len(coefficient_array)

        # Operation on remaining coefficients
        for i in range(coefficient_num):
            DSP_list_nm.append(int(coefficient_array[i][0]))

        # Call the Verilog function
        writeTop(x, DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm])

        return DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm]

    elif(x > 18): # This may be restricted
        # Sort coefficients in increasing (ascending) order in terms of their value
        coefficient_array = sorted(coefficient_array, key=lambda x: x[0])

        # Removes the numbers 2^n
        for i in reversed(range(coefficient_num)):
            if (int(coefficient_array[i][0]) != 0 and ((int(coefficient_array[i][0]) & (int(coefficient_array[i][0]) - 1)) == 0)):
                DSP_list_2p.append([1, int(coefficient_array[i][0])])
                del coefficient_array[i]

        # Update coefficient_num
        coefficient_num = len(coefficient_array)

        # If a multiple can be obtained from another multiple using shift operation, don't produce it
        for i in reversed(range(coefficient_num)):
            for k in range(len(coefficient_array)):
                if ((shift_check(int(coefficient_array[i][0]), int(coefficient_array[k][0]))) and (int(coefficient_array[i][0]) != int(coefficient_array[k][0]))):
                    DSP_list_sh.append([int(coefficient_array[k][0]), int(coefficient_array[i][0])])
                    del coefficient_array[i]
                    break

        # Update coefficient_num
        coefficient_num = len(coefficient_array)

        # Operation on remaining coefficients
        for i in range(coefficient_num):
            if(output_cost(int(coefficient_array[i][0])) > 17):
                DSP_list_nm.append(int(coefficient_array[i][0]))
            else:
                DSP_list.append(int(coefficient_array[i][0]))

        # Call the Verilog function
        writeTop(x, DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm])

        return DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm]

    elif(x > 12):
        maxCpD = 2
    elif(x>8):
        maxCpD = 3
    elif(x > 6):
        maxCpD = 4
    elif(x > 4):
        maxCpD = 6
    elif(x > 3):
        maxCpD = 8
    elif(x > 2):
        maxCpD = 12
    elif(x > 1):
        maxCpD = 24
    else:
        maxCpD = -1

    # If a coefficient does not map into single DSP, remove it from the list
    for i in reversed(range(coefficient_num)):
        if(output_cost(int(coefficient_array[i][0]))>24):
            DSP_list_nm.append(int(coefficient_array[i][0]))
            del coefficient_array[i]

    coefficient_num = len(coefficient_array)

    # Sort coefficients in increasing (ascending) order in terms of their value
    coefficient_array = sorted(coefficient_array, key=lambda x: x[0])

    # Removes the numbers 2^n
    for i in reversed(range(coefficient_num)):
        if(int(coefficient_array[i][0]) != 0 and ((int(coefficient_array[i][0]) & (int(coefficient_array[i][0]) - 1)) == 0)):
            DSP_list_2p.append([1, int(coefficient_array[i][0])])
            del coefficient_array[i]

    # Update coefficient_num
    coefficient_num = len(coefficient_array)

    # If a multiple can be obtained from another multiple using shift operation, don't produce it
    for i in reversed(range(coefficient_num)):
        for k in range(len(coefficient_array)):
            if((shift_check(int(coefficient_array[i][0]),int(coefficient_array[k][0]))) and (int(coefficient_array[i][0]) != int(coefficient_array[k][0]))):
                DSP_list_sh.append([int(coefficient_array[k][0]),int(coefficient_array[i][0])])
                del coefficient_array[i]
                break

    # Sort coefficients in increasing (ascending) order in terms of their costs
    coefficient_array = sorted(coefficient_array, key=lambda x: x[1])

    # -- CONSTANT_ARRAY for the rest of the operation
    constant_array = [0]*len(coefficient_array)
    for i in range(len(coefficient_array)):
        constant_array[i] = coefficient_array[i][0]

    # Update coefficient_num
    coefficient_num = len(constant_array)

    # Number of minimum DSP
    minND = int(math.ceil(float(coefficient_num) / maxCpD)) + 1

    for i in range(minND):
        combination_counter.append(0)

    for i in range(len(constant_array)):
        coefficients_org.append(constant_array[i])

    [DSP_list, coeff_num] = getNextGroup(constant_array, coefficient_num, maxCpD, minND, x, DSP_list, 0, combination_counter, 0)

    for i in range(minND):
        combination_counter[i] = 0

    while (coeff_num > 0):
        minND = minND + 1
        combination_counter.append(0)
        coefficients_org.append(0)
        constant_array = []

        for i in range(len(coefficients_org)):
            constant_array.append(coefficients_org[i])

        DSP_list = []
        coefficient_num = coefficient_num + 1

        [DSP_list, coeff_num] = getNextGroup(constant_array, coefficient_num, maxCpD, minND, x, DSP_list, 0, combination_counter, 0)

    for i in range(len(DSP_list)):
        DSP_list[i] = list(filter(lambda a: a != 0, DSP_list[i]))

    # Call the Verilog function
    writeTop(x, DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm])

    return DSP_list, DSP_list_2p, DSP_list_sh, DSP_list_nm, [CO for CO in DSP_list_co if CO not in DSP_list_nm]

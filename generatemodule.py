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

# This function generates module inputs/outputs
def multipleCons(m, C):
    #m: input variable bit size
    #C: constant array

    IN_SIZE    = m
    CONST      = [0]*len(C)
    OUT_SIZE   = [0]*len(C)
    C_SIZE     = [0]*len(C)
    X_CONS     = [0]*len(C)


    MODULE_OUT = ['']*len(C)
    DSP_A      = 0
    DSP_C      = ''

    SHIFT  = [0]*len(C)
    SIGN   = ['']*len(C)
    REWIRE = ['']*len(C)
    REWIRE_L = [0]*len(C)

    # Check if inputs are valid (Assuming they are valid inputs)
    for ii in range(len(C)):
        CONST[ii]    = C[ii]
        OUT_SIZE[ii] = m + int(math.ceil(math.log(C[ii],2)))

        l=0
        while(C[ii]%2 == 0):
            l=l+1
            C[ii]=C[ii]/2

        SHIFT[ii] = l

        C_bit = bin(C[ii])[2:]
        C[ii]=C[ii]-1

        # Check the case C is 2^n
        n = 0
        if(C[ii]==0):
            REWIRE[ii] = ''
            REWIRE_L[ii] = 0
        else:
            while(C[ii]%2 == 0):
                n=n+1
                C[ii]=C[ii]/2
            REWIRE[ii] = 'X[' + str(n - 1) + ':0]'
            REWIRE_L[ii] = n

        C_SIZE[ii] = OUT_SIZE[ii] - l - n

        X_CONS[ii] = C[ii]

        if(ii==0):
            DSP_A = DSP_A + X_CONS[ii]
        else:
            DSP_A = DSP_A + X_CONS[ii]*(2**sum(C_SIZE[0:ii]))

        # Sign extension for signed numbers
        s=0
        for i in range(len(C_bit)):
            if(C_bit[i]=='1'):
                s=s+(((2**(i))-1)<<(len(C_bit)-i-1))
        s=s & ((2**(len(C_bit)-1))-1)
        s=('{0:0'+str(len(bin(CONST[ii])[2:])-SHIFT[ii]-1)+'b}').format(s)
        SIGN[ii] = s

    DSP_C = DSP_C + "{" + str(48-max(REWIRE_L)-sum(C_SIZE)) + "'d0,X["+str(max(REWIRE_L)-1)+":0]"

    for ii in range(len(C)):
        kk = len(C) - ii - 1
        DSP_C = DSP_C + ",{1'b0"
        for i in range(len(SIGN[kk])):
            if(SIGN[kk][i]=='1'):
                DSP_C = DSP_C + ",X[" + str(m-1) + "]"
            else:
                DSP_C = DSP_C + ",1'b0"
        DSP_C = DSP_C + ",X[" + str(m-1) + ':' + str(REWIRE_L[kk]) + "]}"
    DSP_C = DSP_C + "}"

    # Module outputs
    for ii in range(len(C)):
        if(ii==0):
            MODULE_OUT[ii] = "X_" + str(CONST[ii]) + " = {P["+str(C_SIZE[ii]-1)+":0],P["+str(sum(C_SIZE)+REWIRE_L[ii]-1)+":"+str(sum(C_SIZE))+"],"
            if(SHIFT[ii] == 0):
                MODULE_OUT[ii] = MODULE_OUT[ii][:-1] + "};"
            else:
                MODULE_OUT[ii] = MODULE_OUT[ii] + str(SHIFT[ii]) + "'d0};"
        else:
            MODULE_OUT[ii] = "X_" + str(CONST[ii]) + " = {P[" + str(C_SIZE[ii]+sum(C_SIZE[0:ii]) - 1) + ":"+str(sum(C_SIZE[0:ii]))+"],P[" + str(sum(C_SIZE) + REWIRE_L[ii] - 1) + ":" + str(sum(C_SIZE)) + "],"
            if (SHIFT[ii] == 0):
                MODULE_OUT[ii] = MODULE_OUT[ii][:-1] + "};"
            else:
                MODULE_OUT[ii] = MODULE_OUT[ii] + str(SHIFT[ii]) + "'d0};"

    INFO = ""
    INFO = INFO + "// Input variable bit size: " + str(IN_SIZE) + "\n"
    for ii in range(len(C)):
        INFO = INFO + "// Constant: " + str(CONST[ii]) + " with output bit size of " + str(OUT_SIZE[ii]) + "\n"
        INFO = INFO + "// The output for this constant is " + MODULE_OUT[ii] + "\n"
    INFO = INFO + "// Input A of DSP: " + str(DSP_A) + "\n"
    INFO = INFO + "// Input C of DSP: " + DSP_C + "\n"

    return  INFO,IN_SIZE,CONST,OUT_SIZE,DSP_A,DSP_C,MODULE_OUT

def writeTop(IN_SIZE_port, MAPPED_port, POWER2_port, SHIFTED_port, NOT_MAPPED_port, COEFFICIENTS_port):
    IN_SIZE      = IN_SIZE_port
    MAPPED       = MAPPED_port
    POWER2       = POWER2_port
    SHIFTED      = SHIFTED_port
    NOT_MAPPED   = NOT_MAPPED_port
    COEFFICIENTS = COEFFICIENTS_port

    M = ""
    M = M + "`timescale 1ns / 1ps \n\n"
    M = M + "// latency is 1 clock cycle \n\n"
    M = M + "module top_module(input clk,\n" + \
            "\t\t\t\t  input signed ["+str(IN_SIZE-1)+":0] X"

    for i in range(len(COEFFICIENTS)):
        M = M + ",\n\t\t\t\t  output signed ["+str(IN_SIZE+int(math.ceil(math.log(COEFFICIENTS[i],2)))-1)+":0] X_"+str(COEFFICIENTS[i])
    M = M + ");\n\n"

    if(len(NOT_MAPPED) != 0):
        for i in range(len(NOT_MAPPED)):
            M = M + "\t// X_" + str(NOT_MAPPED[i]) + " cannot be mapped on DSP\n\n"

    if(len(POWER2) != 0):
        M = M + "\treg ["+str(IN_SIZE-1)+":0] X_temp;\n\n"
        M = M + "\talways @(posedge clk) begin\n" + \
                "\t\tX_temp <= X;\n" + \
                "\tend\n\n"
        for i in range(len(POWER2)):
            if(POWER2[i][1] == 1):
                M = M + "\tassign X_1 = X_temp;\n"
            else:
                M = M + "\tassign X_"+str(POWER2[i][1])+" = (X_temp << "+str(int(math.log(POWER2[i][1],2)))+");\n"

    M = M +"\n"

    for i in range(len(SHIFTED)):
        M = M + "\tassign X_"+str(SHIFTED[i][1])+" = (X_"+str(SHIFTED[i][0])+" << "+str(int(math.log(SHIFTED[i][1]/SHIFTED[i][0],2)))+");\n"

    M = M + "\n"

    for i in range(len(MAPPED)):
        M = M + "\tmblock" + str(i) + " m" + str(i) + " (clk,X"
        for k in range(len(MAPPED[i])):
            M = M + ",X_" + str(MAPPED[i][k])
        M = M + ");\n"

        # Create multiplier blocks
        [INFO, IN_BIT, CONST, OUT_SIZE, DSP_A, DSP_C, MODULE_OUT] = multipleCons(IN_SIZE, MAPPED[i])
        writeModule("mblock"+str(i), INFO, IN_BIT, CONST, OUT_SIZE, DSP_A, DSP_C, MODULE_OUT)

    M = M + "\nendmodule"

    file = open("top_module.v", 'w')
    file.write(M)
    file.close()

    return None

def writeModule(NAME,INFO, IN_SIZE,CONST, OUT_SIZE, DSP_A, DSP_C, MODULE_OUT):

    M = ""
    M = M + "`timescale 1ns / 1ps \n" \
    "\n" \
    +INFO+ \
    "\n" \
    "// P = A*B + C \n" \
    "// A: 25-bit \n" \
    "// B: 18-bit \n" \
    "// C: 48-bit \n" \
    "// P: 48-bit \n" \
    "\n" \
    "// 1-clk latency (only output P is registered)\n" \
    "\n" \
    "module " + NAME + " (\n" \
    "\tinput clk,\n" \
    "\tinput  signed ["+str(IN_SIZE-1)+":0] X,"

    for i in range(len(CONST)):
        M = M + "\n\toutput signed ["+str(OUT_SIZE[i]-1)+":0] X_"+str(CONST[i])+","

    M = M[:-1] + ");\n"

    M = M + "\n" \
	"\twire [29:0] ACOUT;\n" \
	"\twire [17:0] BCOUT;\n" \
	"\twire CARRYCASCOUT;\n" \
	"\twire MULTSIGNOUT;\n" \
	"\twire [47:0] PCOUT;\n" \
	"\twire OVERFLOW;\n" \
	"\twire PATTERNBDETECT;\n" \
	"\twire PATTERNDETECT;\n" \
	"\twire UNDERFLOW;\n" \
	"\twire [3:0] CARRYOUT;\n" \
    "\n" \
	"\twire [29:0] A;\n" \
	"\twire [17:0] B;\n" \
	"\twire [47:0] C;\n" \
	"\twire [47:0] P;\n" \
    "\n" \
	"\tassign A = {5'd0,25'd"+str(DSP_A)+"};\n" \
	"\tassign B = {"+str(18-IN_SIZE)+"'d0,X};\n" \
	"\tassign C = "+DSP_C+";\n" \
	"\n"

    for i in range(len(CONST)):
	    M = M + "\tassign "+MODULE_OUT[i]+"\n"

    M = M + "\n" \
    "\tDSP48E1 #( \n"\
    "\t\t// Feature Control Attributes: Data Path Selection \n" \
    '\t\t.A_INPUT("DIRECT"),               // Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port) \n' \
    '\t\t.B_INPUT("DIRECT"),               // Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port) \n' \
    '\t\t.USE_DPORT("FALSE"),              // Select D port usage (TRUE or FALSE) \n' \
    '\t\t.USE_MULT("MULTIPLY"),            // Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE") \n' \
    '\t\t.USE_SIMD("ONE48"),               // SIMD selection ("ONE48", "TWO24", "FOUR12") \n' \
    "\n" \
    '\t\t// Pattern Detector Attributes: Pattern Detection Configuration \n' \
    '\t\t.AUTORESET_PATDET("NO_RESET"),    // "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH" \n'  \
    '\t\t.MASK(48\'h3fffffffffff),          // 48-bit mask value for pattern detect (1=ignore) \n' \
    '\t\t.PATTERN(48\'h000000000000),       // 48-bit pattern match for pattern detect \n' \
    '\t\t.SEL_MASK("MASK"),                // "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2" \n'  \
    '\t\t.SEL_PATTERN("PATTERN"),          // Select pattern value ("PATTERN" or "C") \n' \
    '\t\t.USE_PATTERN_DETECT("NO_PATDET"), // Enable pattern detect ("PATDET" or "NO_PATDET") \n' \
    "\n" \
    "\t\t// Register Control Attributes: Pipeline Register Configuration \n" \
    "\t\t.ACASCREG(0),                     // Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2) \n" \
    "\t\t.ADREG(0),                        // Number of pipeline stages for pre-adder (0 or 1) \n" \
    "\t\t.ALUMODEREG(0),                   // Number of pipeline stages for ALUMODE (0 or 1) \n" \
    "\t\t.AREG(0),                         // Number of pipeline stages for A (0, 1 or 2) \n" \
    "\t\t.BCASCREG(0),                     // Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2) \n" \
    "\t\t.BREG(0),                         // Number of pipeline stages for B (0, 1 or 2) \n" \
    "\t\t.CARRYINREG(0),                   // Number of pipeline stages for CARRYIN (0 or 1) \n" \
    "\t\t.CARRYINSELREG(0),                // Number of pipeline stages for CARRYINSEL (0 or 1) \n" \
    "\t\t.CREG(0),                         // Number of pipeline stages for C (0 or 1) \n" \
    "\t\t.DREG(0),                         // Number of pipeline stages for D (0 or 1) \n" \
    "\t\t.INMODEREG(1),                    // Number of pipeline stages for INMODE (0 or 1) \n" \
    "\t\t.MREG(0),                         // Number of multiplier pipeline stages (0 or 1) \n" \
    "\t\t.OPMODEREG(0),                    // Number of pipeline stages for OPMODE (0 or 1) \n" \
    "\t\t.PREG(1)                          // Number of pipeline stages for P (0 or 1) \n" \
    "\t) \n" \
    "\tDSP48E1_inst ( \n" \
    "\t\t// Cascade: 30-bit (each) output: Cascade Ports \n" \
    "\t\t.ACOUT(ACOUT),                   // 30-bit output: A port cascade output \n" \
    "\t\t.BCOUT(BCOUT),                   // 18-bit output: B port cascade output \n" \
    "\t\t.CARRYCASCOUT(CARRYCASCOUT),     // 1-bit output: Cascade carry output \n" \
    "\t\t.MULTSIGNOUT(MULTSIGNOUT),       // 1-bit output: Multiplier sign cascade output \n" \
    "\t\t.PCOUT(PCOUT),                   // 48-bit output: Cascade output \n" \
    "\n " \
    "\t\t// Control: 1-bit (each) output: Control Inputs/Status Bits \n" \
    "\t\t.OVERFLOW(OVERFLOW),             // 1-bit output: Overflow in add/acc output \n" \
    "\t\t.PATTERNBDETECT(PATTERNBDETECT), // 1-bit output: Pattern bar detect output \n" \
    "\t\t.PATTERNDETECT(PATTERNDETECT),   // 1-bit output: Pattern detect output \n" \
    "\t\t.UNDERFLOW(UNDERFLOW),           // 1-bit output: Underflow in add/acc output \n" \
    "\n" \
    "\t\t// Data: 4-bit (each) output: Data Ports \n" \
    "\t\t.CARRYOUT(CARRYOUT),             // 4-bit output: Carry output \n" \
    "\t\t.P(P),                           // 48-bit output: Primary data output \n" \
    "\n" \
    "\t\t// Cascade: 30-bit (each) input: Cascade Ports \n" \
    "\t\t.ACIN(30'h0),                     // 30-bit input: A cascade data input \n" \
    "\t\t.BCIN(18'h0),                     // 18-bit input: B cascade input \n" \
    "\t\t.CARRYCASCIN(1'b0),               // 1-bit input: Cascade carry input \n" \
    "\t\t.MULTSIGNIN(1'b0),                // 1-bit input: Multiplier sign input \n" \
    "\t\t.PCIN(48'h0),                     // 48-bit input: P cascade input \n" \
    "\n" \
    "\t\t// Control: 4-bit (each) input: Control Inputs/Status Bits \n" \
    "\t\t.ALUMODE(4'h0),                   // 4-bit input: ALU control input \n" \
    "\t\t.CARRYINSEL(3'h0),                // 3-bit input: Carry select input \n" \
    "\t\t.CLK(clk),                        // 1-bit input: Clock input \n" \
    "\t\t.INMODE(5'b00000),                // 5-bit input: INMODE control input \n" \
    "\t\t.OPMODE(7'b0110101),              // 7-bit input: Operation mode input \n" \
    "\n" \
    "\t\t// Data: 30-bit (each) input: Data Ports \n" \
    "\t\t.A(A),                           // 30-bit input: A data input \n" \
    "\t\t.B(B),                           // 18-bit input: B data input \n" \
    "\t\t.C(C),                           // 48-bit input: C data input \n" \
    "\t\t.CARRYIN(1'b0),                  // 1-bit input: Carry input signal \n" \
    "\t\t.D(25'h0),                       // 25-bit input: D data input \n" \
    "\n" \
    "\t\t// Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs \n" \
    "\t\t.CEA1(1'b0),                     // 1-bit input: Clock enable input for 1st stage AREG \n" \
    "\t\t.CEA2(1'b1),                     // 1-bit input: Clock enable input for 2nd stage AREG \n" \
    "\t\t.CEAD(1'b0),                     // 1-bit input: Clock enable input for ADREG \n" \
    "\t\t.CEALUMODE(1'b0),                // 1-bit input: Clock enable input for ALUMODE \n" \
    "\t\t.CEB1(1'b0),                     // 1-bit input: Clock enable input for 1st stage BREG \n" \
    "\t\t.CEB2(1'b1),                     // 1-bit input: Clock enable input for 2nd stage BREG \n" \
    "\t\t.CEC(1'b1),                      // 1-bit input: Clock enable input for CREG \n" \
    "\t\t.CECARRYIN(1'b0),                // 1-bit input: Clock enable input for CARRYINREG \n" \
    "\t\t.CECTRL(1'b0),                   // 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG \n" \
    "\t\t.CED(1'b0),                      // 1-bit input: Clock enable input for DREG \n" \
    "\t\t.CEINMODE(1'b1),                 // 1-bit input: Clock enable input for INMODEREG \n" \
    "\t\t.CEM(1'b0),                      // 1-bit input: Clock enable input for MREG \n" \
    "\t\t.CEP(1'b1),                      // 1-bit input: Clock enable input for PREG \n" \
    "\t\t.RSTA(1'b0),                     // 1-bit input: Reset input for AREG \n" \
    "\t\t.RSTALLCARRYIN(1'b0),            // 1-bit input: Reset input for CARRYINREG \n" \
    "\t\t.RSTALUMODE(1'b0),               // 1-bit input: Reset input for ALUMODEREG \n" \
    "\t\t.RSTB(1'b0),                     // 1-bit input: Reset input for BREG \n" \
    "\t\t.RSTC(1'b0),                     // 1-bit input: Reset input for CREG \n" \
    "\t\t.RSTCTRL(1'b0),                  // 1-bit input: Reset input for OPMODEREG and CARRYINSELREG \n" \
    "\t\t.RSTD(1'b0),                     // 1-bit input: Reset input for DREG and ADREG \n" \
    "\t\t.RSTINMODE(1'b0),                // 1-bit input: Reset input for INMODEREG \n" \
    "\t\t.RSTM(1'b0),                     // 1-bit input: Reset input for MREG \n" \
    "\t\t.RSTP(1'b0)                      // 1-bit input: Reset input for PREG \n" \
    "\t); \n" \
    "\n" \
    "endmodule" \
    "\n" \

    file = open(NAME+".v", 'w')
    file.write(M)
    file.close()

    return None

############################################################
############################################################
############################################################

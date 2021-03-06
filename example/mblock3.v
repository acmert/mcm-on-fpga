`timescale 1ns / 1ps 

// Input variable bit size: 8
// Constant: 11 with output bit size of 12
// The output for this constant is X_11 = {P[10:0],P[20:20]};
// Constant: 9 with output bit size of 12
// The output for this constant is X_9 = {P[19:11],P[22:20]};
// Input A of DSP: 2053
// Input C of DSP: {25'd0,X[2:0],{1'b0,X[7],X[7],X[7],X[7:3]},{1'b0,X[7],1'b0,X[7],X[7:1]}}

// P = A*B + C 
// A: 25-bit 
// B: 18-bit 
// C: 48-bit 
// P: 48-bit 

// 1-clk latency (only output P is registered)

module mblock3 (
	input clk,
	input  signed [7:0] X,
	output signed [11:0] X_11,
	output signed [11:0] X_9);

	wire [29:0] ACOUT;
	wire [17:0] BCOUT;
	wire CARRYCASCOUT;
	wire MULTSIGNOUT;
	wire [47:0] PCOUT;
	wire OVERFLOW;
	wire PATTERNBDETECT;
	wire PATTERNDETECT;
	wire UNDERFLOW;
	wire [3:0] CARRYOUT;

	wire [29:0] A;
	wire [17:0] B;
	wire [47:0] C;
	wire [47:0] P;

	assign A = {5'd0,25'd2053};
	assign B = {10'd0,X};
	assign C = {25'd0,X[2:0],{1'b0,X[7],X[7],X[7],X[7:3]},{1'b0,X[7],1'b0,X[7],X[7:1]}};

	assign X_11 = {P[10:0],P[20:20]};
	assign X_9 = {P[19:11],P[22:20]};

	DSP48E1 #( 
		// Feature Control Attributes: Data Path Selection 
		.A_INPUT("DIRECT"),               // Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port) 
		.B_INPUT("DIRECT"),               // Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port) 
		.USE_DPORT("FALSE"),              // Select D port usage (TRUE or FALSE) 
		.USE_MULT("MULTIPLY"),            // Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE") 
		.USE_SIMD("ONE48"),               // SIMD selection ("ONE48", "TWO24", "FOUR12") 

		// Pattern Detector Attributes: Pattern Detection Configuration 
		.AUTORESET_PATDET("NO_RESET"),    // "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH" 
		.MASK(48'h3fffffffffff),          // 48-bit mask value for pattern detect (1=ignore) 
		.PATTERN(48'h000000000000),       // 48-bit pattern match for pattern detect 
		.SEL_MASK("MASK"),                // "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2" 
		.SEL_PATTERN("PATTERN"),          // Select pattern value ("PATTERN" or "C") 
		.USE_PATTERN_DETECT("NO_PATDET"), // Enable pattern detect ("PATDET" or "NO_PATDET") 

		// Register Control Attributes: Pipeline Register Configuration 
		.ACASCREG(0),                     // Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2) 
		.ADREG(0),                        // Number of pipeline stages for pre-adder (0 or 1) 
		.ALUMODEREG(0),                   // Number of pipeline stages for ALUMODE (0 or 1) 
		.AREG(0),                         // Number of pipeline stages for A (0, 1 or 2) 
		.BCASCREG(0),                     // Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2) 
		.BREG(0),                         // Number of pipeline stages for B (0, 1 or 2) 
		.CARRYINREG(0),                   // Number of pipeline stages for CARRYIN (0 or 1) 
		.CARRYINSELREG(0),                // Number of pipeline stages for CARRYINSEL (0 or 1) 
		.CREG(0),                         // Number of pipeline stages for C (0 or 1) 
		.DREG(0),                         // Number of pipeline stages for D (0 or 1) 
		.INMODEREG(1),                    // Number of pipeline stages for INMODE (0 or 1) 
		.MREG(0),                         // Number of multiplier pipeline stages (0 or 1) 
		.OPMODEREG(0),                    // Number of pipeline stages for OPMODE (0 or 1) 
		.PREG(1)                          // Number of pipeline stages for P (0 or 1) 
	) 
	DSP48E1_inst ( 
		// Cascade: 30-bit (each) output: Cascade Ports 
		.ACOUT(ACOUT),                   // 30-bit output: A port cascade output 
		.BCOUT(BCOUT),                   // 18-bit output: B port cascade output 
		.CARRYCASCOUT(CARRYCASCOUT),     // 1-bit output: Cascade carry output 
		.MULTSIGNOUT(MULTSIGNOUT),       // 1-bit output: Multiplier sign cascade output 
		.PCOUT(PCOUT),                   // 48-bit output: Cascade output 

 		// Control: 1-bit (each) output: Control Inputs/Status Bits 
		.OVERFLOW(OVERFLOW),             // 1-bit output: Overflow in add/acc output 
		.PATTERNBDETECT(PATTERNBDETECT), // 1-bit output: Pattern bar detect output 
		.PATTERNDETECT(PATTERNDETECT),   // 1-bit output: Pattern detect output 
		.UNDERFLOW(UNDERFLOW),           // 1-bit output: Underflow in add/acc output 

		// Data: 4-bit (each) output: Data Ports 
		.CARRYOUT(CARRYOUT),             // 4-bit output: Carry output 
		.P(P),                           // 48-bit output: Primary data output 

		// Cascade: 30-bit (each) input: Cascade Ports 
		.ACIN(30'h0),                     // 30-bit input: A cascade data input 
		.BCIN(18'h0),                     // 18-bit input: B cascade input 
		.CARRYCASCIN(1'b0),               // 1-bit input: Cascade carry input 
		.MULTSIGNIN(1'b0),                // 1-bit input: Multiplier sign input 
		.PCIN(48'h0),                     // 48-bit input: P cascade input 

		// Control: 4-bit (each) input: Control Inputs/Status Bits 
		.ALUMODE(4'h0),                   // 4-bit input: ALU control input 
		.CARRYINSEL(3'h0),                // 3-bit input: Carry select input 
		.CLK(clk),                        // 1-bit input: Clock input 
		.INMODE(5'b00000),                // 5-bit input: INMODE control input 
		.OPMODE(7'b0110101),              // 7-bit input: Operation mode input 

		// Data: 30-bit (each) input: Data Ports 
		.A(A),                           // 30-bit input: A data input 
		.B(B),                           // 18-bit input: B data input 
		.C(C),                           // 48-bit input: C data input 
		.CARRYIN(1'b0),                  // 1-bit input: Carry input signal 
		.D(25'h0),                       // 25-bit input: D data input 

		// Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs 
		.CEA1(1'b0),                     // 1-bit input: Clock enable input for 1st stage AREG 
		.CEA2(1'b1),                     // 1-bit input: Clock enable input for 2nd stage AREG 
		.CEAD(1'b0),                     // 1-bit input: Clock enable input for ADREG 
		.CEALUMODE(1'b0),                // 1-bit input: Clock enable input for ALUMODE 
		.CEB1(1'b0),                     // 1-bit input: Clock enable input for 1st stage BREG 
		.CEB2(1'b1),                     // 1-bit input: Clock enable input for 2nd stage BREG 
		.CEC(1'b1),                      // 1-bit input: Clock enable input for CREG 
		.CECARRYIN(1'b0),                // 1-bit input: Clock enable input for CARRYINREG 
		.CECTRL(1'b0),                   // 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG 
		.CED(1'b0),                      // 1-bit input: Clock enable input for DREG 
		.CEINMODE(1'b1),                 // 1-bit input: Clock enable input for INMODEREG 
		.CEM(1'b0),                      // 1-bit input: Clock enable input for MREG 
		.CEP(1'b1),                      // 1-bit input: Clock enable input for PREG 
		.RSTA(1'b0),                     // 1-bit input: Reset input for AREG 
		.RSTALLCARRYIN(1'b0),            // 1-bit input: Reset input for CARRYINREG 
		.RSTALUMODE(1'b0),               // 1-bit input: Reset input for ALUMODEREG 
		.RSTB(1'b0),                     // 1-bit input: Reset input for BREG 
		.RSTC(1'b0),                     // 1-bit input: Reset input for CREG 
		.RSTCTRL(1'b0),                  // 1-bit input: Reset input for OPMODEREG and CARRYINSELREG 
		.RSTD(1'b0),                     // 1-bit input: Reset input for DREG and ADREG 
		.RSTINMODE(1'b0),                // 1-bit input: Reset input for INMODEREG 
		.RSTM(1'b0),                     // 1-bit input: Reset input for MREG 
		.RSTP(1'b0)                      // 1-bit input: Reset input for PREG 
	); 

endmodule

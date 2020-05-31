`timescale 1ns / 1ps 

// latency is 1 clock cycle 

module top_module(input clk,
				  input signed [7:0] X,
				  output signed [9:0] X_4,
				  output signed [10:0] X_8,
				  output signed [11:0] X_9,
				  output signed [11:0] X_11,
				  output signed [12:0] X_22,
				  output signed [12:0] X_25,
				  output signed [13:0] X_44,
				  output signed [14:0] X_87,
				  output signed [17:0] X_974,
				  output signed [20:0] X_5748,
				  output signed [34:0] X_86746874);

	// X_212454575487857 cannot be mapped on DSP

	reg [7:0] X_temp;

	always @(posedge clk) begin
		X_temp <= X;
	end

	assign X_8 = (X_temp << 3);
	assign X_4 = (X_temp << 2);

	assign X_44 = (X_11 << 2);
	assign X_22 = (X_11 << 1);

	mblock0 m0 (clk,X,X_86746874);
	mblock1 m1 (clk,X,X_5748,X_87);
	mblock2 m2 (clk,X,X_974,X_25);
	mblock3 m3 (clk,X,X_11,X_9);

endmodule
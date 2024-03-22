`default_nettype none

module shortpath (
    input logic a,
    output logic x,
    input logic clk
);

    logic a_;

    always_ff @(posedge clk) begin
        a_ <= a;
        x <= a_;
    end

endmodule

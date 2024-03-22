`default_nettype none

module multiout (
    input logic a, b,
    output logic w, x, y, z,
    input logic clk
);

    logic a_, b_;

    always_ff @(posedge clk) begin
        a_ <= a;
        b_ <= b;

        w <= a_ ^ b_;
        x <= a_ & b_;
        y <= a_ | b_;
        z <= ~(a_ ^ b_);
    end

endmodule

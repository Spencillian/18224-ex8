`default_nettype none

module reconvergent (
    input logic a, b, c, d, e,
    output logic x,
    input logic clk
);

    logic a_, b_, c_, d_, e_;
    logic tmp1, tmp2;

    assign tmp1 = (a_ & b_);
    assign tmp2 = tmp1 ^ c_;

    always_ff @(posedge clk) begin
        a_ <= a;
        b_ <= b;
        c_ <= c;
        d_ <= d;
        e_ <= e;

        x <= (~tmp1 | d_) & (~tmp2 | e_);
    end

endmodule

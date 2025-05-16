control ig_stg_2(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) tbl_counter_port;

    action user_port(bit <1> user_port){
        tbl_counter_port.count();
        meta.user_port = user_port;
        ig_tm_md.ucast_egress_port = 10;
    }
    table ingress_port_tbl {
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            @defaultonly NoAction;
            user_port;
        }
        counters = tbl_counter_port;
        size = 256;
        const default_action = NoAction();
        
    }
    apply {
        ingress_port_tbl.apply();
    }
}
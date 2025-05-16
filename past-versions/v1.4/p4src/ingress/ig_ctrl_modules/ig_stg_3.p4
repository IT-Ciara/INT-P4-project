typedef bit<1> ig_is_sdn_trace_index_t;

control ig_stg_3(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    ig_is_sdn_trace_index_t is_sdn_trace_index = 0;
    Counter<bit<64>, ig_is_sdn_trace_index_t>(1<<1, CounterType_t.PACKETS_AND_BYTES) is_sdn_trace_counter;
    DirectCounter<bit<64>> (CounterType_t.PACKETS_AND_BYTES) is_sdn_trace_tbl_counter;
    
    action send_to_cpu(ig_is_sdn_trace_index_t stats_idx){
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE;
        is_sdn_trace_index = stats_idx;
        is_sdn_trace_tbl_counter.count();
        meta.sdn_trace = 1;
    }
    table is_sdn_tbl {
        key = {
            hdr.ethernet.src_addr: exact;
        }
        actions = {
            send_to_cpu;
        }
        size = 100;
        counters = is_sdn_trace_tbl_counter;
    }

    apply {
        is_sdn_tbl.apply();
        is_sdn_trace_counter.count(is_sdn_trace_index);
    }
}

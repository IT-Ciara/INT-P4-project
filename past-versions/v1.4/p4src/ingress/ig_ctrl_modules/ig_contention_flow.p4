typedef bit<2> contention_flow_stats_index_t;

control ig_contention_flow(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    contention_flow_stats_index_t contention_flow_stats_index = 0;
    // Counter<bit<64>, contention_flow_stats_index_t>(CONTENTION_FLOW_STATS_SIZE, CounterType_t.PACKETS_AND_BYTES) tbl_contention_flow_counter;

    Counter<bit<64>, contention_flow_stats_index_t>(1<<2, CounterType_t.PACKETS_AND_BYTES) tbl_contention_flow_counter;

    action drop(contention_flow_stats_index_t stats_idx){
        meta.dropped = 1;
        ig_dprsr_md.drop_ctl = 1;
        contention_flow_stats_index = stats_idx;
    }

    action update_flows_counter(contention_flow_stats_index_t stats_idx){
        contention_flow_stats_index = stats_idx;
    }

    table contention_flow_tbl {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.ethernet.dst_addr : exact;
            hdr.ethernet.ether_type: exact;
            hdr.outer_vlan.vid : exact;
            hdr.ipv4.src_addr : exact;
            hdr.ipv4.dst_addr : exact;
        }
        actions = {
            drop;
            update_flows_counter;
        }
        size = 512;
    }

    apply {
        contention_flow_tbl.apply();
        tbl_contention_flow_counter.count(contention_flow_stats_index);
    }
}

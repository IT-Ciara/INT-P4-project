
control ig_stg_4(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) drop_counter;

    action drop(){
        meta.dropped = 1;
        ig_dprsr_md.drop_ctl = 1;
        drop_counter.count();
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
        }
        counters = drop_counter;
        size = 512;
    }

    apply {
        contention_flow_tbl.apply();
    }
}



ig_intr_md.ingress_port
hdr.ethernet.dst_addr
hdr.ethernet.ether_type
hdr.outer_vlan.vid
hdr.ipv4.src_addr
hdr.ipv4.dst_addr
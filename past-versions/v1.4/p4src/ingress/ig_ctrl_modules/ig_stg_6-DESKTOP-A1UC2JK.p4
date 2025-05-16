typedef bit<2> ig_flow_mirror_stats_index_t;

control ig_flow_mirror(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    action set_mirror_type() {
        ig_dprsr_md.mirror_type = MIRROR_TYPE_I2E;
        meta.pkt_type = PKT_TYPE_MIRROR;
    }

    action set_normal_pkt() {
        hdr.bridged_md.setValid();
        hdr.bridged_md.pkt_type = PKT_TYPE_NORMAL;
    }

    action set_md(PortId_t egress_port, bit<1> ing_mir, MirrorId_t ing_ses, bit<1> egr_mir, MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
    }

    //Tables
    table  ig_flow_mirror_tcp_tbl {
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.outer_vlan.vid: exact;
            hdr.ipv4.protocol: exact;
            hdr.tcp.dst_port: exact;    
        }
        actions = {
            set_md;
        }
        size = 200;
    }
    table ig_flow_mirror_udp_tbl {
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.outer_vlan.vid: exact;
            hdr.ipv4.protocol: exact;
            hdr.udp.dst_port: exact;    
        }
        actions = {
            set_md;
        }
        size = 200;
    }

    apply{
        if(ig_intr_md.resubmit_flag == 0 ){
            if(ig_flow_mirror_tcp_tbl.apply().miss){
                ig_flow_mirror_udp_tbl.apply();
            }
        }

        if(meta.do_ing_mirroring == 1){
            set_mirror_type();
        }

        set_normal_pkt();
    }

}
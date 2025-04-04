control eg_flow_mirror(
    inout eg_hdrs_t hdr,
    inout eg_metadata_t meta,
    in egress_intrinsic_metadata_t eg_intr_md,
    in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t eg_oport_md
) {
    action set_mirror(){
        meta.egr_mir_ses = hdr.bridged_md.egr_mir_ses;
        meta.pkt_type = PKT_TYPE_MIRROR;
        eg_dprsr_md.mirror_type = MIRROR_TYPE_E2E;
    }

    apply { 
        if (hdr.bridged_md.do_egr_mirroring==1){
            set_mirror();
        }
    }
}
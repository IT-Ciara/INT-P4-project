control EgressDeparser(packet_out pkt,
    /* User */
    inout eg_hdrs_t                       hdr,
    in    eg_metadata_t                      meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md)
{  
    Mirror() mirror; 
    apply{
        if(eg_dprsr_md.mirror_type == 2){ 
            if (eg_dprsr_md.mirror_type == MIRROR_TYPE_E2E) {
                mirror.emit<mirror_h>(meta.egr_mir_ses, {meta.pkt_type});
            }
        }
        pkt.emit(hdr);
    }
}
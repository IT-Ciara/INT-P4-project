control IngressDeparser(packet_out pkt,
    /* User */
    inout ig_hdrs_t                       hdr,
    in    ig_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md)
{   
    Mirror() mirror;
    apply {
        if (ig_dprsr_md.mirror_type == MIRROR_TYPE_I2E) {
            mirror.emit<mirror_h>(meta.ing_mir_ses, {meta.pkt_type});
        }

        pkt.emit(hdr);
    }
}
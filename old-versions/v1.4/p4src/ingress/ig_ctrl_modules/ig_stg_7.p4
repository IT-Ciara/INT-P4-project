
control ig_stg_7(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    action set_polka_md() {
        meta.has_polka = 1;
    }
    table  ig_polka_type_tbl {
        key = {
            hdr.ethernet.ether_type: exact;
        }
        actions = {
            set_polka_md;
        }
        size = 5;
    }

    apply{
        ig_polka_type_tbl.apply();
    }

}
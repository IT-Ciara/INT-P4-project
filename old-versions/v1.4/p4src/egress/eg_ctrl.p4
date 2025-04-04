#include "eg_ctrl_modules/eg_flow_mirror.p4"

control Egress(
    /* User */
    inout eg_hdrs_t                          hdr,
    inout eg_metadata_t                         meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md)
{   
    apply {
        eg_flow_mirror.apply(hdr, meta, eg_intr_md, eg_prsr_md, eg_dprsr_md, eg_oport_md);
    }
}
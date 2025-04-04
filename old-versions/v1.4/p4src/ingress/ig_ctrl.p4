// #include "ig_ctrl_modules/ig_save_tstamp.p4" // Module that saves the timestamp in the int shim header
// #include "ig_actions/ig_actions.p4" // Actions used in the ingress pipeline
#include "ig_ctrl_modules/ig_stg_2.p4" // Module that processes the ingress port
#include "ig_ctrl_modules/ig_stg_3.p4" // Module that checks if the packet is an SDN trace
#include "ig_ctrl_modules/ig_stg_4.p4" // Module that checks if the packet is part of a contention flow
#include "ig_ctrl_modules/ig_stg_5.p4" // Module that checks if the packet is part of a loop
#include "ig_ctrl_modules/ig_stg_6.p4" // Module that mirrors the packet
#include "ig_ctrl_modules/ig_stg_7.p4" // Module that processes the egress port
#include "ig_ctrl_modules/ig_stg_8.p4" // Module that processes the egress port

control Ingress(
    /* User */
    inout ig_hdrs_t                       hdr,
    inout ig_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{   
    apply {
        ig_stg_2.apply(hdr, meta, ig_intr_md, ig_tm_md);
        // if (meta.user_port == 1) {
        //     ig_stg_3.apply(hdr, meta, ig_intr_md, ig_tm_md);
        //     if (meta.sdn_trace == 0 && meta.dropped == 0) {
        //         ig_stg_4.apply(hdr, meta, ig_intr_md, ig_dprsr_md, ig_tm_md);
        //         if (meta.port_loop == 0 && meta.vlan_loop == 0) {
        //             ig_stg_5.apply(hdr, meta, ig_intr_md, ig_dprsr_md, ig_tm_md);
        //             ig_stg_6.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md, ig_tm_md);
        //         }
        //     }
        // } else if (meta.user_port == 0) {
        //     ig_stg_7.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md, ig_tm_md);
        //     if (meta.has_polka ==1 || meta.stg_8 == 1) {
        //         ig_stg_8.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md, ig_tm_md);
        //     }
        // }

    }
}
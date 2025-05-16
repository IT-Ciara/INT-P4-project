#include "ig_ctrl_modules/ig_save_tstamp.p4" // Module that saves the timestamp in the int shim header
#include "ig_ctrl_modules/ig_ingress_port.p4" // Module that processes the ingress port
#include "ig_ctrl_modules/ig_is_sdn_trace.p4" // Module that checks if the packet is an SDN trace
#include "ig_ctrl_modules/ig_contention_flow.p4" // Module that checks if the packet is part of a contention flow
#include "ig_ctrl_modules/ig_loop.p4" // Module that checks if the packet is part of a loop
#include "ig_ctrl_modules/ig_flow_mirror.p4" // Module that mirrors the packet
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
        // ig_save_tstamp.apply(hdr, ig_intr_md, ig_tm_md);
        ig_ingress_port.apply(hdr, meta, ig_intr_md, ig_tm_md);
        if(meta.user_flag == 1) {
            ig_is_sdn_trace.apply(hdr, meta, ig_intr_md, ig_tm_md);
            ig_contention_flow.apply(hdr, meta, ig_intr_md, ig_dprsr_md, ig_tm_md);
            if(meta.dropped == 0) {
                ig_loop.apply(hdr, meta, ig_intr_md, ig_dprsr_md, ig_tm_md);
                ig_flow_mirror.apply(hdr, meta, ig_intr_md,ig_prsr_md, ig_dprsr_md, ig_tm_md);
            }
        }    
    }
}
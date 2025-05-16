
control ig_save_tstamp(
    inout ig_hdrs_t hdr,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    action save_tstamp(){
        hdr.custom_int_shim.setValid();
        /* Add the timestamp to the int shim header */
        hdr.custom_int_shim.ingress_mac_tstamp = ig_intr_md.ingress_mac_tstamp;
        /* Temp Int shim header for testing */
        hdr.custom_int_shim.full_int_stack = 0;
        hdr.custom_int_shim.full_mtu = 0;
        hdr.custom_int_shim.reserved = 0;
        hdr.custom_int_shim.int_count = 0;
        hdr.custom_int_shim.next_hdr = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = 0x0601;
        //Temp. This is just to forward the traffic 
        ig_tm_md.ucast_egress_port = 1;
    }
    apply {
        save_tstamp();
    }
}
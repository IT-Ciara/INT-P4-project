struct ig_metadata_t {
    bit<1> user_flag;
    bit<1> dropped;
    bit<1> polka;
    bit<1> port_loop;
    bit<1> vlan_loop;
    bit<1> mirror;

    // Mirror metadata
    bit<1> do_ing_mirroring;  // Enable ingress mirroring
    bit<1> do_egr_mirroring;  // Enable egress mirroring
    MirrorId_t ing_mir_ses;   // Ingress mirror session ID
    MirrorId_t egr_mir_ses;   // Egress mirror session ID
    pkt_type_t pkt_type;

}
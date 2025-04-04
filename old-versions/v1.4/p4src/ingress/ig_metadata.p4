struct ig_metadata_t {
    bit<1> user_port; //Stage 2
    bit<1> sdn_trace; //Stage 3
    bit<1> dropped; //Stage 4
    bit<1> port_loop; //Stage 5
    bit<1> vlan_loop; //Stage 5
    //l4 port 
    bit<16> l4_dst_port;

    // Mirror metadata. Stage 6 
    bit<1> do_ing_mirroring;  // Enable ingress mirroring
    bit<1> do_egr_mirroring;  // Enable egress mirroring
    MirrorId_t ing_mir_ses;   // Ingress mirror session ID
    MirrorId_t egr_mir_ses;   // Egress mirror session ID
    pkt_type_t pkt_type;

    
    bit<1> copy; //Stage 6
    bit<1> normal; //Stage 6
    //Stage 7
    bit<1> has_polka;
    bit<1> stg_8;
}
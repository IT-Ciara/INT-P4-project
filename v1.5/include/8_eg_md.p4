struct eg_metadata_t{
    //===== Ig Metadata header =====//
    bit<8> md_type;
    bit<48> ig_tstamp;
    bit<1> endpoint;
    //==== MIRRORING ====//
    bit<1> do_ing_mirroring;  // Enable ingress mirroring
    bit<1> do_egr_mirroring;  // Enable egress mirroring
    MirrorId_t ing_mir_ses;   // Ingress mirror session ID
    MirrorId_t egr_mir_ses;   // Egress mirror session ID
    pkt_type_t pkt_type;
    PortId_t output_port; // Egress port
    // ====== Stage 11: Polka - Destination Endpoint? ======
    bit<1> edge_node_md; // 1 if destination endpoint, 0 otherwise
    bit<1>temp;
    //====== Stage 10: No Polka - Destination Endpoint? ======
    bit<32> high_upper;
    bit<32> high_lower;
    bit<32> low_upper;
    bit<32> low_lower;   
}
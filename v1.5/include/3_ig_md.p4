//================ I N G R E S S   M E T A D A T A ============================
struct ig_metadata_t{
    bit<1> user_port; // ====== Stage 1: User Port? ======
    bit<1> has_polka;
    bit<1> core_node;

    //Polka
    bit<128> polka_routeid; // Polka route ID

    //======== MIRRORING ==========//
    bit<1> do_ing_mirroring;  // Enable ingress mirroring
    bit<1> do_egr_mirroring;  // Enable egress mirroring
    MirrorId_t ing_mir_ses;   // Ingress mirror session ID
    MirrorId_t egr_mir_ses;   // Egress mirror session ID
    pkt_type_t pkt_type;

    //===Stage 9: Port Mirror?===//
    bit<1> eval_port_mirror;
}
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
//========================== R E G I S T E R S ==============================
// ====== Stage 11: Polka - Destination Endpoint? ======
    Register<bit<1>,bit<1>>(size=1,initial_value=0) edge_node; 
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_high_upper;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_high_lower;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_low_upper;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_low_lower;

//===================== R E G I S T E R   A C T I O N S =====================
    RegisterAction<bit<1>,bit<1>,bit<1>>(edge_node) is_edge_node = {void apply(inout bit<1> value, out bit<1> rv) {
            rv = value;}}; 
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_high_upper) read_high_upper = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_high_lower) read_high_lower = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_low_upper) read_low_upper = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_low_lower) read_low_lower = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
//========================== C O U N T E R S ================================

//============================ A C T I O N S ================================
    action rm_ig_md(){
        hdr.ig_metadata.setInvalid();  
    }
    action rm_md(){
        hdr.bridged_md.setInvalid();
        hdr.mirror_md.setInvalid();
        rm_ig_md();
    }    
    //===========MIRRORING=================//
    action set_mirror(){
        meta.egr_mir_ses = hdr.bridged_md.egr_mir_ses;
        meta.pkt_type = PKT_TYPE_MIRROR;
        eg_dprsr_md.mirror_type = MIRROR_TYPE_E2E;
    }
    // ====== Stage 11: Polka - Destination Endpoint? ======
    action rm_int_stack(){
        hdr.custom_int_stack[0].setInvalid();
        hdr.custom_int_stack[1].setInvalid();
        hdr.custom_int_stack[2].setInvalid();
        hdr.custom_int_stack[3].setInvalid();
        hdr.custom_int_stack[4].setInvalid();
        hdr.custom_int_stack[5].setInvalid();
    }
    action remove_all_hdrs(){
        hdr.ethernet.ether_type = ETHER_TYPE_INT;
        hdr.custom_int_shim.next_hdr = 0x0;
        // Invalidate protocol headers
        hdr.polka.setInvalid();
        hdr.outer_vlan.setInvalid();
        hdr.inner_vlan.setInvalid();
        hdr.ipv4.setInvalid();
        hdr.udp.setInvalid();
        hdr.tcp.setInvalid();
        rm_int_stack();
    }
    action rm_polka(){
        hdr.ethernet.ether_type = hdr.polka.proto;
        hdr.polka.setInvalid();
    }
    action rm_int(){
        hdr.ethernet.ether_type = hdr.custom_int_shim.next_hdr;
        hdr.custom_int_shim.setInvalid();
        rm_int_stack();
    }
    //--Main Actions--//
    action export_int(){ //==Stage11==
        remove_all_hdrs();
    }
    action rm_polka_int(){
        rm_polka();
        rm_int();
    }

    //=========INT METADATA=================//
        action increase_int_count(bit<8> int_count){
        hdr.custom_int_shim.int_count = int_count;
    }
    action push_int1(){
        hdr.custom_int_stack[1].setValid();
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x5678;
        increase_int_count(2);
    }
    action push_int2(){
        hdr.custom_int_stack[2].setValid();
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x9101;
        increase_int_count(3);
    }
    action push_int3(){
        hdr.custom_int_stack[3].setValid();
        hdr.custom_int_stack[3].data = hdr.custom_int_stack[2].data;
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x1121;
        increase_int_count(4);
    }
    action push_int4(){
        hdr.custom_int_stack[4].setValid();
        hdr.custom_int_stack[4].data = hdr.custom_int_stack[3].data;
        hdr.custom_int_stack[3].data = hdr.custom_int_stack[2].data;
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x2122;
        increase_int_count(5);
    }
    action push_int5(){
        hdr.custom_int_stack[5].setValid();
        hdr.custom_int_stack[5].data = hdr.custom_int_stack[4].data;
        hdr.custom_int_stack[4].data = hdr.custom_int_stack[3].data;
        hdr.custom_int_stack[3].data = hdr.custom_int_stack[2].data;
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x2223;
        increase_int_count(6);
    }
    action set_full_int_stack(){
        hdr.custom_int_shim.full_int_stack = 1;
    }    
    // ===== Stage 10: No Polka - Destination Endpoint? ======
    action add_polka(){
        hdr.polka.setValid();
        hdr.polka.version = 0x01;
        hdr.polka.ttl = 0x40;
        hdr.polka.proto = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_POLKA;


        hdr.polka.routeid[127:96] = meta.high_upper;
        hdr.polka.routeid[95:64]  = meta.high_lower;
        hdr.polka.routeid[63:32]  = meta.low_upper;
        hdr.polka.routeid[31:0]   = meta.low_lower;
    }    
    action push_int0(){
        hdr.custom_int_stack[0].setValid();
        hdr.custom_int_stack[0].data = 0x1234;
    }    
    action add_int_shim(){
        hdr.custom_int_shim.ig_tstamp = meta.ig_tstamp;
        hdr.custom_int_shim.full_int_stack = 0;
        hdr.custom_int_shim.full_mtu = 0;
        hdr.custom_int_shim._padding = 0;
        hdr.custom_int_shim.int_count = 1;
        hdr.custom_int_shim.reserved = 0;
        push_int0();
    }
    action add_int_polka(){
        hdr.custom_int_shim.setValid();
        hdr.custom_int_shim.next_hdr = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_INT;
        add_int_shim();
        add_polka();        
    }
    // ==== Stg 4: Partner-provided link? ====
    action rm_s_vlan_add_int(){
        hdr.ig_metadata.setInvalid();
        hdr.custom_int_shim.setValid();
        hdr.custom_int_shim.next_hdr = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_INT;
        add_int_shim();
    }    

//============================== T A B L E S ================================
    // ====== Stage 11: Polka - Destination Endpoint? ======
    table eg_polka_dst_ep_tbl{
        key = {
            //Do it based on the output port 
            eg_intr_md.egress_port:exact;
        }
        actions = {
            export_int;
            rm_polka_int;
            rm_md;
        }
        default_action = rm_md;
        size = 5;
    }
    // ====== Stage 11: Polka - Destination Endpoint? ====== Add the INT metadata
    table eg_int_table{
        key = {
            hdr.custom_int_shim.int_count: exact;
        }
        actions = {
            push_int1;
            push_int2;
            push_int3;
            push_int4;
            push_int5;
            increase_int_count;
            set_full_int_stack;
        }
        const entries = {
            1: push_int1();
            2: push_int2();
            3: push_int3();
            4: push_int4();
            5: push_int5();
        }
        default_action = set_full_int_stack;
        size = 5;
    }

    // ===== Stage 10: No Polka - Destination Endpoint? ======
    table eg_no_polka_dst_ep_tbl{
        key = {
            meta.endpoint: exact;
        }
        actions = {
            add_int_polka;
            rm_md;
        }
        default_action = rm_md;
        size = 100;        
    }

    apply{
        meta.edge_node_md = is_edge_node.execute(0);
        //===Mirroring===//
        if (hdr.bridged_md.do_egr_mirroring == 1) {
            set_mirror();
        }
        // ==== Stage 4: Partner-provided link? ====
        if (hdr.ig_metadata.rm_s_vlan_add_int == 1) {
            rm_s_vlan_add_int();
        }
        //=====Stage 11: Polka - Destination Endpoint? ======
        // Edge node - Egress
        if (meta.edge_node_md ==1){
            if(hdr.ethernet.ether_type == ETHER_TYPE_POLKA) {
                eg_polka_dst_ep_tbl.apply(); 
            }
            else{
                if (meta.endpoint == 0) {
                    meta.high_upper = read_high_upper.execute(0);
                    meta.high_lower = read_high_lower.execute(0);
                    meta.low_upper  = read_low_upper.execute(0);
                    meta.low_lower  = read_low_lower.execute(0);
                }
                eg_no_polka_dst_ep_tbl.apply(); //==Stage10==                
            }
        }
        // Core node- No Endpoint 
        else if (meta.edge_node_md ==0){
            if(hdr.ethernet.ether_type == ETHER_TYPE_POLKA) {
                eg_int_table.apply(); 
            }
        }
        rm_md();
    }
}
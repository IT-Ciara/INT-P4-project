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
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_high_upper;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_high_lower;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_low_upper;
    Register<bit<32>, bit<1>>(size=2, initial_value=0) routeId_low_lower;
//===================== R E G I S T E R   A C T I O N S =====================
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_high_upper) read_high_upper = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_high_lower) read_high_lower = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_low_upper) read_low_upper = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
    RegisterAction<bit<32>, bit<1>, bit<32>>(routeId_low_lower) read_low_lower = {
        void apply(inout bit<32> value, out bit<32> rv) {rv = value;}};
//========================== C O U N T E R S ================================
// ====== Egress INT Table Counter =====
DirectCounter<bit<64>>(CounterType_t.PACKETS) eg_int_table_counter;
// ====== Egress Port Info Table Counter =====
DirectCounter<bit<64>>(CounterType_t.PACKETS) eg_port_info_tbl_counter;
// ====== Egress User Port Table Counter =====
DirectCounter<bit<64>>(CounterType_t.PACKETS) eg_user_port_tbl_counter;
// ====== Egress P4 SW Port Table Counter =====
DirectCounter<bit<64>>(CounterType_t.PACKETS) eg_p4_sw_port_tbl_counter;
// ====== Egress Transit Port Table Counter =====
DirectCounter<bit<64>>(CounterType_t.PACKETS) eg_transit_port_tbl_counter;

//========================== I N D I R E C T    C O U N T E R S ================================
Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) eg_port_info_miss_counter;
//============== Output: User Port ================
Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) eg_user_port_miss_counter;
//============== Output: P4 SW Port ================
Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) eg_p4_sw_port_miss_counter;
//============== Output: Transit Port ================
Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) eg_transit_port_miss_counter;
//================ Mirror: Export INT ================
Counter<bit<64>,index2_t>(1,CounterType_t.PACKETS_AND_BYTES) eg_export_int_miss_counter;

//============================ A C T I O N S ================================
    // ====== General Actions ======
    action rm_md(){
        hdr.bridged_md.setInvalid();
        hdr.mirror_md.setInvalid();
        hdr.ig_metadata.setInvalid();  
    }  
    action rm_int_stack(){
        hdr.custom_int_stack[0].setInvalid();
        hdr.custom_int_stack[1].setInvalid();
        hdr.custom_int_stack[2].setInvalid();
        hdr.custom_int_stack[3].setInvalid();
        hdr.custom_int_stack[4].setInvalid();
        hdr.custom_int_stack[5].setInvalid();
    }   
    // ====== Stage 11: Polka - Destination Endpoint? ======
    action remove_all_hdrs(){
        hdr.ethernet.ether_type = ETHER_TYPE_INT;
        hdr.custom_int_shim.next_hdr = 0x0;
        // Invalidate protocol headers
        hdr.polka.setInvalid();
        hdr.s_vlan.setInvalid();
        hdr.u_vlan.setInvalid();
        hdr.ipv4.setInvalid();
        hdr.udp.setInvalid();
        hdr.tcp.setInvalid();
        rm_int_stack();
    }    
    //--Main Actions--//
    action export_int(){ //==Stage11==
        remove_all_hdrs();
    }    
    //===========MIRRORING=================//
    action set_mirror(){
        meta.egr_mir_ses = hdr.bridged_md.egr_mir_ses;
        meta.pkt_type = PKT_TYPE_MIRROR;
        eg_dprsr_md.mirror_type = MIRROR_TYPE_E2E;
    }


    //========================================================================
    // ====== INT Table ======
    //=========INT METADATA=================//
    action increase_int_count(bit<8> int_count){
        hdr.custom_int_shim.int_count = int_count;
    }
    action push_int1(){
        hdr.custom_int_stack[1].setValid();
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x5678;
        increase_int_count(2);
        eg_int_table_counter.count();
    }
    action push_int2(){
        hdr.custom_int_stack[2].setValid();
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x9101;
        increase_int_count(3);
        eg_int_table_counter.count();

    }
    action push_int3(){
        hdr.custom_int_stack[3].setValid();
        hdr.custom_int_stack[3].data = hdr.custom_int_stack[2].data;
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x1121;
        increase_int_count(4);
        eg_int_table_counter.count();
    }
    action push_int4(){
        hdr.custom_int_stack[4].setValid();
        hdr.custom_int_stack[4].data = hdr.custom_int_stack[3].data;
        hdr.custom_int_stack[3].data = hdr.custom_int_stack[2].data;
        hdr.custom_int_stack[2].data = hdr.custom_int_stack[1].data;
        hdr.custom_int_stack[1].data = hdr.custom_int_stack[0].data;
        hdr.custom_int_stack[0].data = 0x2122;
        increase_int_count(5);
        eg_int_table_counter.count();
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
        eg_int_table_counter.count();
    }
    action set_full_int_stack(){
        hdr.custom_int_shim.full_int_stack = 1;
        eg_int_table_counter.count();
    } 
    //========================================================================





    //========================================================================
    // =====Egress Port Info Table =====
    action set_port_md(bit<1> user_port, bit<1> p4_sw_port, 
                       bit<1> transit_port) {
        meta.user_port = user_port;
        meta.p4_sw_port = p4_sw_port;
        meta.transit_port = transit_port;
        eg_port_info_tbl_counter.count();
    }
    //========================================================================










    //========================================================================
    // ====== User Port Table ======    
    //========= CALLED ACTIONS ==========//
    action rm_polka(){
        hdr.ethernet.ether_type = hdr.polka.proto;
        hdr.polka.setInvalid();      
    }     
    action rm_int(){
        hdr.ethernet.ether_type = hdr.custom_int_shim.next_hdr;
        hdr.custom_int_shim.setInvalid();
        rm_int_stack();     
    }


    //========= H I T   A C T I O N S ==========//
    action rm_u_vlan(){
        hdr.ethernet.ether_type = hdr.u_vlan.ether_type;
        hdr.u_vlan.setInvalid();
        eg_user_port_tbl_counter.count();  
    }    
    action add_u_vlan(bit<12> new_vid){
        hdr.u_vlan.setValid();
        hdr.u_vlan.vid = new_vid;
        hdr.u_vlan.dei = 0;
        hdr.u_vlan.pri = 0;
        hdr.u_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_VLAN;
        eg_user_port_tbl_counter.count();        
    }    
    action modify_u_vlan(bit<12> new_vid){
        hdr.u_vlan.vid = new_vid;
        eg_user_port_tbl_counter.count();        
    }    
    action rm_polka_int(){
        rm_polka();
        rm_int();
        eg_user_port_tbl_counter.count();           
    }
    action rm_polka_int_add_u_vlan(bit<12> new_vid){
        rm_polka();
        rm_int();
        add_u_vlan(new_vid);     
    }
    action rm_polka_int_u_vlan(){
        rm_polka();
        rm_int();
        rm_u_vlan();  
        // eg_user_port_tbl_counter.count();
    }
    action rm_polka_int_modify_u_vlan(bit<12> new_vid){
        rm_polka();
        rm_int();  
        modify_u_vlan(new_vid);
    }
    action rm_s_vlan_add_u_vlan(bit<12> new_vid){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        add_u_vlan(new_vid);      
    }
    action rm_s_vlan(){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();  
        eg_user_port_tbl_counter.count();           
    }
    action rm_s_vlan_u_vlan(){
        hdr.ethernet.ether_type = hdr.u_vlan.ether_type;
        hdr.u_vlan.setInvalid();
        hdr.s_vlan.setInvalid();   
        eg_user_port_tbl_counter.count();        
    }
    action rm_s_vlan_modify_u_vlan(bit<12> new_vid){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        hdr.u_vlan.vid = new_vid;  
        eg_user_port_tbl_counter.count();           
    }   
















    //========================================================================
    // ====== Table - P4 SW Port ====
    //========= CALLED ACTIONS ==========//
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

    //========= H I T   A C T I O N S ==========//
    action add_int_polka(){
        hdr.custom_int_shim.setValid();
        hdr.custom_int_shim.next_hdr = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_INT;
        add_int_shim();
        add_polka();     
        eg_p4_sw_port_tbl_counter.count();   
    } 
    action rm_s_vlan_add_int_polka(){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        add_int_polka();
    }
    //========================================================================

















    //========================================================================
    // ====== Table - Transit Port ====
    //========= CALLED ACTIONS ==========//
    action rm_polka_int_transit(){
        // Remove Polka
        hdr.ethernet.ether_type = hdr.polka.proto;
        hdr.polka.setInvalid();
        // Remove INT 
        hdr.ethernet.ether_type = hdr.custom_int_shim.next_hdr;
        hdr.custom_int_shim.setInvalid();
        // Remove INT Stack
        hdr.custom_int_stack[0].setInvalid();
        hdr.custom_int_stack[1].setInvalid();
        hdr.custom_int_stack[2].setInvalid();
        hdr.custom_int_stack[3].setInvalid();
        hdr.custom_int_stack[4].setInvalid();
        hdr.custom_int_stack[5].setInvalid();        
    }
    //========= H I T   A C T I O N S ==========//
    action add_s_vlan(bit<12> new_vid){
        hdr.s_vlan.setValid();
        hdr.s_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.s_vlan.vid = new_vid;
        hdr.ethernet.ether_type = ETHER_TYPE_QINQ;
        eg_transit_port_tbl_counter.count();
    }
    action add_s_vlan_rm_int_polka(bit<12> new_vid){
        rm_polka_int_transit();
        hdr.s_vlan.setValid();
        hdr.s_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_QINQ;
        hdr.s_vlan.vid = new_vid;
        hdr.s_vlan.dei = 0;
        hdr.s_vlan.pri = 0;
        eg_transit_port_tbl_counter.count();
    }
    //========================================================================








//============================== T A B L E S ================================
    //========================================================================
    // ====== INT Table ======
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
        counters = eg_int_table_counter;
    }

    //========================================================================    
    // =====Egress Port Info Table =====
   table eg_port_info_tbl {
        key = {
            eg_intr_md.egress_port:exact;
        }
        actions = {
            set_port_md;
        }
        // default_action = set_port_md(0, 0, 0);
        size = 16;
        counters = eg_port_info_tbl_counter;
    }    

    //========================================================================    
    // ====== User Port Table ======
    table eg_user_port_tbl {
        key = {
            hdr.ethernet.ether_type: exact;
            hdr.u_vlan.vid: ternary;
            hdr.s_vlan.vid: ternary;
        }
        actions = {
            add_u_vlan;
            modify_u_vlan;
            rm_u_vlan;
            rm_s_vlan;
            rm_s_vlan_modify_u_vlan;
            rm_s_vlan_u_vlan;
            rm_s_vlan_add_u_vlan;
            rm_polka_int;
            rm_polka_int_modify_u_vlan;
            rm_polka_int_u_vlan;
            rm_polka_int_add_u_vlan;
        }
        size = 100;   
        counters = eg_user_port_tbl_counter;  
    }    

    //========================================================================    
    // ====== Table - P4 SW Port ====
    table eg_p4_sw_port_tbl{
        key = {
            hdr.ethernet.ether_type: exact;
            hdr.ig_metadata.ig_port: exact;
        }
        actions = {
            add_int_polka;
            rm_s_vlan_add_int_polka;
        }
        size = 100;  
        counters = eg_p4_sw_port_tbl_counter;
    }

    //========================================================================    
    // ====== Table - Transit Port ====
    table eg_transit_port_tbl{
        key = {
            hdr.ethernet.ether_type: exact;
            hdr.ig_metadata.ig_port: exact;
        }
        actions = {
            add_s_vlan_rm_int_polka;
            add_s_vlan;
        }
        size = 100;        
        counters = eg_transit_port_tbl_counter;
    }

    //========================================================================    
    apply{
        //===Mirroring===//
        if (hdr.bridged_md.do_egr_mirroring == 1) {
            set_mirror();
        }
        
        if(eg_port_info_tbl.apply().miss){
            // Increase the counter since the output port is not a user port
            eg_port_info_miss_counter.count(0);
        }

        if(meta.user_port==1){
            eg_user_port_tbl.apply();            
        }
        else if(meta.p4_sw_port==1){
            //Increase the counter since the output port is not an user port 
            eg_user_port_miss_counter.count(0);
            
            meta.high_upper = read_high_upper.execute(0);
            meta.high_lower = read_high_lower.execute(0);
            meta.low_upper  = read_low_upper.execute(0);
            meta.low_lower  = read_low_lower.execute(0);            
            if(hdr.ethernet.ether_type!=ETHER_TYPE_POLKA){
                eg_p4_sw_port_tbl.apply();
            }  
            else if (hdr.ethernet.ether_type==ETHER_TYPE_POLKA){
                eg_int_table.apply();
            }
        }
        else if(meta.transit_port==1){
            //Increase the counter since the output port is not a p4 sw port
            eg_user_port_miss_counter.count(0);
            eg_p4_sw_port_miss_counter.count(0);
            eg_transit_port_tbl.apply();
        }
        else{
            if(hdr.mirror_md.isValid() ){
                if (eg_intr_md.egress_port==EXPORT_INT1){
                    // Increase the counter since the output port is not a transit port    
                    export_int();
                    eg_export_int_miss_counter.count(0);
                }
            }   
            else{
                eg_transit_port_miss_counter.count(0);
            }         
        }
        
        rm_md();
    }
}
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

//============================ A C T I O N S ================================
    action rm_md(){
        hdr.bridged_md.setInvalid();
        hdr.mirror_md.setInvalid();
        hdr.ig_metadata.setInvalid();  
    }  
    // =====Egress General Actions=====
    action set_port_md(bit<1> user_port, bit<1> p4_sw_port, 
                       bit<1> transit_port) {
        meta.user_port = user_port;
        meta.p4_sw_port = p4_sw_port;
        meta.transit_port = transit_port;
    }
    //===== Egress VLAN Actions ======//
    action add_u_vlan(bit<12> new_vid){
        hdr.u_vlan.setValid();
        hdr.u_vlan.vid = new_vid;
        hdr.u_vlan.dei = 0;
        hdr.u_vlan.pri = 0;
        hdr.u_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_VLAN;
    }    
    action modify_u_vlan(bit<12> new_vid){
        hdr.u_vlan.vid = new_vid;
    }  
    action remove_u_vlan(){
        hdr.ethernet.ether_type = hdr.u_vlan.ether_type;
        hdr.u_vlan.setInvalid();
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
        hdr.s_vlan.setInvalid();
        hdr.u_vlan.setInvalid();
        // hdr.inner_vlan.setInvalid();
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
    action add_s_vlan(bit<12> new_vid){
        hdr.s_vlan.setValid();
        hdr.s_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.s_vlan.vid = new_vid;
        hdr.ethernet.ether_type = ETHER_TYPE_QINQ;
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
    action rm_s_vlan_add_int_polka(){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        add_int_polka();
    }
    action add_s_vlan_rm_int_polka(bit<12> new_vid){
        rm_polka_int();
        hdr.s_vlan.setValid();
        hdr.s_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = ETHER_TYPE_QINQ;
        hdr.s_vlan.vid = new_vid;
        hdr.s_vlan.dei = 0;
        hdr.s_vlan.pri = 0;
    }
    action rm_s_vlan(){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
    }
    action rm_s_vlan_modify_u_vlan(bit<12> new_vid){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        modify_u_vlan(new_vid);
    }   
    action rm_s_vlan_u_vlan(){
        hdr.ethernet.ether_type = hdr.u_vlan.ether_type;
        hdr.u_vlan.setInvalid();
        hdr.s_vlan.setInvalid();
    }
    action rm_s_vlan_add_u_vlan(bit<12> new_vid){
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        add_u_vlan(new_vid);
    }
    action rm_polka_int_modify_u_vlan(bit<12> new_vid){
        rm_polka();
        rm_int();
        modify_u_vlan(new_vid);
    }
    action rm_u_vlan(){
        hdr.ethernet.ether_type = hdr.u_vlan.ether_type;
        hdr.u_vlan.setInvalid();
    }
    action rm_polka_int_u_vlan(){
        rm_polka_int();
        rm_u_vlan();
        
    }
    action rm_polka_int_add_u_vlan(bit<12> new_vid){
        rm_polka_int();
        add_u_vlan(new_vid);
    }
//============================== T A B L E S ================================
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
   // =====Egress General Table=====
   table eg_port_info_tbl {
        key = {
            eg_intr_md.egress_port:exact;
        }
        actions = {
            set_port_md;
        }
        size = 16;
    }    
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
            remove_u_vlan;
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
    }    
    // ====== Table - P4 SW Port ====
    table eg_p4_sw_port_tbl{
        key = {
            meta.p4_sw_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.ig_metadata.ig_port: exact;
        }
        actions = {
            add_int_polka;
            rm_s_vlan_add_int_polka;
            rm_md;
        }
        default_action = rm_md;
        size = 100;        
    }
    // ====== Table - Transit Port ====
    table eg_transit_port_tbl{
        key = {
            meta.transit_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.ig_metadata.ig_port: exact;
        }
        actions = {
            add_s_vlan_rm_int_polka;
            add_s_vlan;
            rm_md;
        }
        default_action = rm_md;
        size = 100;        
    }
    apply{
        eg_port_info_tbl.apply();
        if(meta.user_port==1){
            eg_user_port_tbl.apply();
        }
        //===Mirroring===//
        if (hdr.bridged_md.do_egr_mirroring == 1) {
            set_mirror();
        }
        if(meta.p4_sw_port==1){
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
            eg_transit_port_tbl.apply();
        }
        else if(hdr.mirror_md.isValid() && (eg_intr_md.egress_port==EXPORT_INT1||eg_intr_md.egress_port==EXPORT_INT2)){
            export_int();
        }
        rm_md();
    }
}
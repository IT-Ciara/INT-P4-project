
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
    //========================== P O L K A ==================================
    CRCPolynomial<bit<16>>(coeff    = (65539 & 0xffff),
                            reversed = false,
                            msb      = false,
                            extended = false,
                            init     = 16w0x0000,
                            xor      = 16w0x0000) poly;
    Hash<bit<16>>(HashAlgorithm_t.CUSTOM, poly) hash;     
    //========================== R E G I S T E R S ==============================

    //========================== D I R E C T    C O U N T E R S ================================
    // ===== Stage 1: User Port? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_port_info_tbl_counter;
    // ===== Stage 3: Topology Discovery? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_topology_discovery_tbl_counter;
    // ===== Stage 3: Link continuity test? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_link_continuity_test_tbl_counter;
    // ===== Stage 4: Partner provided link? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_partner_provided_link_tbl_counter;
    // ====== Stage 5: SDN trace? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_sdn_trace_tbl_counter;
    // ===== Stage 6: Contention flow? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_contention_flow_tbl_drop_counter;
    // ===== Stage 7: Port loop? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_port_loop_tbl_counter;
    // ===== Stage 7: VLAN loop? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_vlan_loop_tbl_counter;
    // ===== Stage 8: Flow mirror? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_flow_mirror_tbl_counter; 
    //===== Stage 9: Port Mirror? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_port_mirror_tbl_counter;
    //==== Stage 11: Polka - Destination Endpoint? ====== No
    DirectCounter<bit<64>>(CounterType_t.PACKETS) ig_output_polka_port_tbl_counter;


    //========================== I N D I R E C T    C O U N T E R S ================================
    // index_t index = 0 ;    

    // index2_t index2 = 0;

    // Counter<bit<64>,index_t>(15,CounterType_t.PACKETS_AND_BYTES) miss_counter;
    // ===== Stage 1: User Port? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_port_info_tbl_miss_counter;
    // ===== Stage 2: has Polka ID? =====
    Counter<bit<64>,index2_t>(4,CounterType_t.PACKETS_AND_BYTES) has_polka_id_tbl_counter;
    // ===== Stage 3: Topology Discovery? ======    
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_topology_discovery_tbl_miss_counter;
    // ===== Stage 3: Link continuity test? ======    
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_link_continuity_test_tbl_miss_counter;
    // ===== Stage 4: Partner provided link? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_partner_provided_link_tbl_miss_counter;
    // ====== Stage 5: SDN trace? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_sdn_trace_tbl_miss_counter;
    // ===== Stage 6: Contention flow? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_contention_flow_tbl_miss_counter;
    // ===== Stage 7: Port loop? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_port_loop_tbl_miss_counter;
    // ===== Stage 7: VLAN loop? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_vlan_loop_tbl_miss_counter;
    // ===== Stage 8: Flow mirror? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_flow_mirror_tbl_miss_counter;
    //===== Stage 9: Port Mirror? ======
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_port_mirror_tbl_miss_counter;
    //==== Stage 11: Polka - Destination Endpoint? ====== No
    Counter<bit<64>,index_t>(1,CounterType_t.PACKETS_AND_BYTES) ig_output_polka_port_tbl_miss_counter;

    //============================ A C T I O N S ================================
    // =====Ingress General Actions=====
    action set_output_port(PortId_t port) {
        ig_tm_md.ucast_egress_port = port;
    }    
    // ====== Stage 1: User Port? ======    
    action set_port_md(bit<1> user_port, 
                       PortId_t egress_port) {
        meta.user_port = user_port;
        set_output_port(egress_port);
        ig_port_info_tbl_counter.count();
    }
    action set_normal_pkt() {
        hdr.bridged_md.setValid();
        hdr.bridged_md.pkt_type = PKT_TYPE_NORMAL;
    }        
    //===========MIRRORING=================//
    action set_mirror_type() {
        ig_dprsr_md.mirror_type = MIRROR_TYPE_I2E;
        meta.pkt_type = PKT_TYPE_MIRROR;
    }
    action set_md(PortId_t egress_port, bit<1> ing_mir, 
    MirrorId_t ing_ses, bit<1> egr_mir, 
    MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
        ig_output_polka_port_tbl_counter.count();
        
    }
    action mod_output_port(bit<128> routeid) {
        bit<16> nbase=0;
        bit<64> ncount=4294967296*2;
        bit<16> nresult;
        bit<16> nport;
        routeid_t ndata = routeid >> 16;
        bit<16> dif = (bit<16>) (routeid ^ (ndata << 16));
        nresult = hash.get((routeid_t) ndata);
        nport = nresult ^ dif;
        bit<9> output_port = (bit<9>) nport; 
        set_output_port(output_port);
    } 
    // ====== Stage 3: Topology Discovery? ======
    action topology_discovery(){
        ig_topology_discovery_tbl_counter.count();
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE; //send to cpu
    } 
    // ===== Stage 3: Link continuity test? ======
    action link_continuity_test(){
        ig_link_continuity_test_tbl_counter.count();
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE; //send to cpu
    }  
    // ===== Stage 4: Partner provided link? ======
    action set_user_port(PortId_t egress_port){
        meta.user_port = 1;
        set_output_port(egress_port);
        ig_partner_provided_link_tbl_counter.count();
    }
    action rm_s_vlan(PortId_t egress_port){
        meta.user_port = 1;
        hdr.ethernet.ether_type = hdr.s_vlan.ether_type;
        hdr.s_vlan.setInvalid();
        set_output_port(egress_port);
        ig_partner_provided_link_tbl_counter.count();
    }  
    // ==== Stage 5: SDN trace? ======
    action send_to_cpu(){
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE;
        ig_sdn_trace_tbl_counter.count();
    } 
    // ===== Stage 6: Contention flow? ======
    action drop(){
        ig_dprsr_md.drop_ctl = 1;
        ig_contention_flow_tbl_drop_counter.count();
    }   
    // ===== Stage 7: Port loop? ======
    action send_back(){
        ig_tm_md.ucast_egress_port = ig_intr_md.ingress_port;
        ig_port_loop_tbl_counter.count();  
    }    
    // ===== Stage 7: VLAN loop? ======
    action send_back_vlan(){
        ig_tm_md.ucast_egress_port = ig_intr_md.ingress_port;
        ig_vlan_loop_tbl_counter.count();
    } 
    // ==== Stage 8: Flow mirror? ======
    action set_md_flow_mirror(PortId_t egress_port, bit<1> ing_mir, MirrorId_t ing_ses, 
        bit<1> egr_mir, MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
        ig_flow_mirror_tbl_counter.count();
    } 
    //===== Stage 9: Port Mirror? ======
    action set_md_port_mirror(PortId_t egress_port, bit<1> ing_mir, MirrorId_t ing_ses, 
    bit<1> egr_mir, MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
        ig_port_mirror_tbl_counter.count();
    } 

    //============================== T A B L E S ================================
    // =====Ingress General Table=====
    // ====== Stage 1: User Port? ======    
    table ig_port_info_tbl {
        key = {
            ig_intr_md.ingress_port : exact;
        }
        actions = {
            set_port_md;
        }
        size = 16;
        counters = ig_port_info_tbl_counter;
    }
    // ====== Stage 3: Topology Discovery? ======
    table ig_topology_discovery_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
        }
        actions = {
            topology_discovery;
        }
        size = 10;
        counters = ig_topology_discovery_tbl_counter;
    }
    // ===== Stage 3: Link continuity test? ======
    table ig_link_continuity_test_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
        }
        actions = {
            link_continuity_test;
        }
        size = 10;
        counters = ig_link_continuity_test_tbl_counter;
    } 
    // ===== Stage 4: Partner provided link? ======
    table ig_partner_provided_link_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.s_vlan.vid: exact;
            hdr.u_vlan.vid: exact;
        }
        actions = {
            set_user_port;
            rm_s_vlan;
        }
        default_action = set_user_port(64);
        size = 100;
        counters = ig_partner_provided_link_tbl_counter;
    } 
    // ====== Stage 5: SDN trace? ======
    table ig_sdn_trace_tbl {
        key = {
            hdr.ethernet.src_addr: exact;
        }
        actions = {
            send_to_cpu;
        }
        size = 100;
        counters = ig_sdn_trace_tbl_counter;
    } 
    // ===== Stage 6: Contention flow? ======
    table ig_contention_flow_tbl {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.ethernet.dst_addr : exact;
            hdr.ethernet.ether_type: exact;
            hdr.u_vlan.vid : exact;
            hdr.s_vlan.vid : exact;
            hdr.ipv4.src_addr : exact;
            hdr.ipv4.dst_addr : exact;
        }
        actions = {
            drop;
        }
        counters = ig_contention_flow_tbl_drop_counter;
        size = 512;
    }   
    // ===== Stage 7: Port loop? ======
    table ig_port_loop_tbl {
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            send_back;
        }
        size = 16;
        counters = ig_port_loop_tbl_counter;
    }
    // ===== Stage 7: VLAN loop? ======
    table  ig_vlan_loop_tbl {
        key = {
            hdr.u_vlan.vid: exact;
            hdr.s_vlan.vid: exact;
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            send_back_vlan;
        }
        size = 100;
        counters = ig_vlan_loop_tbl_counter;
    }     
    // ===== Stage 8: Flow mirror? ======
    table ig_flow_mirror_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            set_md_flow_mirror;
        }
        size = 16;
        counters = ig_flow_mirror_tbl_counter;
    }  
    //===== Stage 9: Port Mirror? ======
    table ig_port_mirror_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            set_md_port_mirror;
        }
        size = 16;
        counters = ig_port_mirror_tbl_counter;
    }
    //==== Stage 11: Polka - Destination Endpoint? ====== No
    table ig_output_polka_port_tbl{
        key = {
            ig_tm_md.ucast_egress_port: exact;
        }
        actions = {
            set_md;
        }
        size=16;
        counters = ig_output_polka_port_tbl_counter;
    }
    apply{
        //===== Stage 1: User Port? ======
        ig_port_info_tbl.apply();
        set_normal_pkt();
        if(meta.user_port==0){
            ig_port_info_tbl_miss_counter.count(0);
            //===== Stage 2: has Polka ID? No ======
            if(hdr.ethernet.ether_type!=ETHER_TYPE_POLKA){
                has_polka_id_tbl_counter.count(0);
                //===== Stage3: Topology Discovery? ======
                if(ig_topology_discovery_tbl.apply().miss){
                    ig_topology_discovery_tbl_miss_counter.count(0);
                    //===== Stage3: Link continuity test? ======
                    if(ig_link_continuity_test_tbl.apply().miss){
                        ig_link_continuity_test_tbl_miss_counter.count(0);
                        //===== Stage 4: Partner provided link? ======
                        if(ig_partner_provided_link_tbl.apply().miss){
                            ig_partner_provided_link_tbl_miss_counter.count(0);
                        }
                    }
                }
            }       
            //===== Stage 2: has Polka ID? Yes ======
            else{
                has_polka_id_tbl_counter.count(1);
            }
        }
        if(meta.user_port == 1){
            //===== Stage 5: SDN trace? ======
            if(ig_sdn_trace_tbl.apply().miss) {
                ig_sdn_trace_tbl_miss_counter.count(0);
                //===== Stage 6: Contention flow? ======
                if(ig_contention_flow_tbl.apply().miss) {
                    ig_contention_flow_tbl_miss_counter.count(0);
                    //===== Stage 7: Port loop? ======
                    if(ig_port_loop_tbl.apply().miss){
                        ig_port_loop_tbl_miss_counter.count(0);
                        //===== Stage 7: VLAN loop? ======
                        if(ig_vlan_loop_tbl.apply().miss){
                            ig_vlan_loop_tbl_miss_counter.count(0);
                            //===== Stage 8: Flow mirror? ======
                            if(ig_flow_mirror_tbl.apply().miss){
                                ig_flow_mirror_tbl_miss_counter.count(0);
                            }
                        }
                    }
                }
            }
        }
        //===== Stage 9: Port Mirror? ======
        if(ig_port_mirror_tbl.apply().miss){
            ig_port_mirror_tbl_miss_counter.count(0);
        }
        if(hdr.polka.isValid()){
            mod_output_port(meta.polka_routeid);           
            //==== Stage 11: Polka - Destination Endpoint? ====== No
            if(ig_output_polka_port_tbl.apply().miss){
                ig_output_polka_port_tbl_miss_counter.count(0);
            }
        }
        if(meta.do_ing_mirroring == 1){
            set_mirror_type();
        }    
    }
}

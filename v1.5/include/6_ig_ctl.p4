
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
    // ====== Stage 11: Polka - Destination Endpoint? ======
    Register<bit<1>,bit<1>>(size=1,initial_value=0) core_node; 
    //===================== R E G I S T E R   A C T I O N S =====================
    RegisterAction<bit<1>,bit<1>,bit<1>>(core_node) is_core_node = {void apply(inout bit<1> value, out bit<1> rv) {
            rv = value;}};    
    //========================== C O U N T E R S ================================
    // ====== Stage 1: User Port? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_user_port_tbl_counter;
    // ===== Stage 3: Topology Discovery? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_topolog_discovery_tbl_counter;
    // ===== Stage 3: Link continuity test? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_link_continuity_test_tbl_counter;
    // ===== Stage 4: Partner provided link? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_partner_provided_link_tbl_counter;
    // ====== Stage 5: SDN trace? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_sdn_trace_tbl_counter;
    // ===== Stage 6: Contention flow? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) drop_counter;
    // ===== Stage 7: Port loop? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_port_loop_tbl_counter;
    // ===== Stage 7: VLAN loop? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_vlan_loop_tbl_counter;
    // ===== Stage 8: Flow mirror? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_flow_mirror_tbl_counter; 
    //===== Stage 9: Port Mirror? ======
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_port_mirror_tbl_counter;
    //============================ A C T I O N S ================================
    action set_output_port(bit<9> egress_port) {
        ig_tm_md.ucast_egress_port = egress_port;
    }     
    //===========MIRRORING=================//
    action set_mirror_type() {
        ig_dprsr_md.mirror_type = MIRROR_TYPE_I2E;
        meta.pkt_type = PKT_TYPE_MIRROR;
    }
    action set_md(PortId_t egress_port, bit<1> ing_mir, MirrorId_t ing_ses, bit<1> egr_mir, MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
    }
    // ====== Stage 1: User Port? ======
    action user_port(bit <1> user_port){ 
        ig_user_port_tbl_counter.count();
        meta.user_port = user_port;
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
        ig_topolog_discovery_tbl_counter.count();
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE; //send to cpu
    } 
    // ===== Stage 3: Link continuity test? ======
    action link_continuity_test(){
        ig_link_continuity_test_tbl_counter.count();
        ig_tm_md.ucast_egress_port = CPU_PORT_VALUE; //send to cpu
    }  
    // ===== Stage 4: Partner provided link? ======
    action set_user_port(){
        meta.user_port = 1;
        set_output_port(10);
        ig_partner_provided_link_tbl_counter.count();
    }
    action rm_s_vlan_add_int(){
        hdr.ig_metadata.setValid();
        hdr.ig_metadata.rm_s_vlan_add_int = 1;
        set_output_port(11);
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
        drop_counter.count();
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
    action set_normal_pkt() {
        hdr.bridged_md.setValid();
        hdr.bridged_md.pkt_type = PKT_TYPE_NORMAL;
        set_output_port(12);
    }    
    //===== Stage 9: Port Mirror? ======
    action set_normal_pkt_flow_mirror() {
        hdr.bridged_md.setValid();
        hdr.bridged_md.pkt_type = PKT_TYPE_NORMAL;
        meta.eval_port_mirror = 1;
    }
    action set_md_port_mirror(PortId_t egress_port, bit<1> ing_mir, MirrorId_t ing_ses, bit<1> egr_mir, MirrorId_t egr_ses) {
        ig_tm_md.ucast_egress_port = egress_port;
        meta.do_ing_mirroring = ing_mir;
        meta.ing_mir_ses = ing_ses;
        hdr.bridged_md.do_egr_mirroring = egr_mir;
        hdr.bridged_md.egr_mir_ses = egr_ses;
        ig_port_mirror_tbl_counter.count();
    } 
    // ===== Stage 10: No Polka - Destination Endpoint? ======
    action forward(PortId_t egress_port,
                    bit<1> endpoint){
        ig_tm_md.ucast_egress_port = egress_port;
        hdr.ig_metadata.endpoint = endpoint;
    }
    action add_u_vlan(bit<12> new_vid, PortId_t egress_port,
                    bit<1> endpoint
    ){
        hdr.outer_vlan.setValid();
        hdr.outer_vlan.vid = new_vid;
        hdr.outer_vlan.dei = 0;
        hdr.outer_vlan.pri = 0;
        hdr.outer_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = 0x8100;
        ig_tm_md.ucast_egress_port = egress_port;
        hdr.ig_metadata.endpoint = endpoint;
    }
    action modify_u_vlan(bit<12> new_vid, PortId_t egress_port,
                        bit<1> endpoint
    ){
        hdr.outer_vlan.vid = new_vid;
        ig_tm_md.ucast_egress_port = egress_port;
        hdr.ig_metadata.endpoint = endpoint;
    }        


    //============================== T A B L E S ================================
    // ====== Stage 1: User Port? ======
    table ig_user_port_tbl{ 
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            user_port;
        }
        counters = ig_user_port_tbl_counter;
        size = 8;        
    }
    // ====== Stage 3: Topology Discovery? ======
    table ig_topolog_discovery_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
        }
        actions = {
            topology_discovery;
        }
        size = 10;
        counters = ig_topolog_discovery_tbl_counter;
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
            hdr.outer_vlan.vid: exact;
        }
        actions = {
            set_user_port;
            rm_s_vlan_add_int;
        }
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
            hdr.outer_vlan.vid : exact;
            hdr.ipv4.src_addr : exact;
            hdr.ipv4.dst_addr : exact;
        }
        actions = {
            drop;
        }
        counters = drop_counter;
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
            hdr.outer_vlan.vid: exact;
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
    // ===== Stage 10: No Polka - Destination Endpoint? ======
    table ig_no_polka_dst_ep_tbl{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.outer_vlan.vid: ternary;
        }
        actions = {
            forward;
            add_u_vlan;
            modify_u_vlan;
        }
        size = 100;     
    }

    apply{
        meta.core_node = is_core_node.execute(0);
        if (ig_user_port_tbl.apply().miss) {
            meta.user_port = 0;
            //===== Stage 2: has Polka ID? ======
            meta.has_polka = 1;
            if(hdr.ethernet.ether_type!=ETHER_TYPE_POLKA){
                meta.has_polka = 0;
                //===== Stage3: Topology Discovery? ======
                if(ig_topolog_discovery_tbl.apply().miss){
                    //===== Stage3: Link continuity test? ======
                    if(ig_link_continuity_test_tbl.apply().miss){
                        //===== Stage 4: Partner provided link? ======
                        ig_partner_provided_link_tbl.apply();
                    }
                }
            }
        } 
        if(meta.user_port == 1){
            //===== Stage 5: SDN trace? ======
            if(ig_sdn_trace_tbl.apply().miss) {
                //===== Stage 6: Contention flow? ======
                if(ig_contention_flow_tbl.apply().miss) {
                    //===== Stage 7: Port loop? ======
                    if(ig_port_loop_tbl.apply().miss){
                        //===== Stage 7: VLAN loop? ======
                        if(ig_vlan_loop_tbl.apply().miss){
                            //===== Stage 8: Flow mirror? ======
                            if(ig_intr_md.resubmit_flag == 0){
                                ig_flow_mirror_tbl.apply();
                            }
                            if(meta.do_ing_mirroring == 1){
                                set_mirror_type();
                            }
                            set_normal_pkt_flow_mirror();
                        }
                    }
                }
            }
        }
        //===== Stage 9: Port Mirror? ======
        if(meta.eval_port_mirror == 1){
            if(ig_intr_md.resubmit_flag == 0){
                ig_port_mirror_tbl.apply();
            }
            if(meta.do_ing_mirroring == 1){
                set_mirror_type();
            }
            set_normal_pkt();
        }
        //===== Stage 11: Polka - Destination Endpoint? ======
        if(meta.core_node == 1){
            mod_output_port(meta.polka_routeid);
        }
        //===== Stage 10: No Polka - Destination Endpoint? ======
        else{
            ig_no_polka_dst_ep_tbl.apply();
        }
    }
}

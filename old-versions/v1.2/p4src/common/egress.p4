/* -*- P4_16 -*- */

/**************** V1.2 ****************/

/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

    /***********************  H E A D E R S  ************************/

struct my_egress_headers_t {
    ethernet_h   ethernet;
    vlan_tag_h outer_vlan;
    custom_int_shim_h custom_int_shim;
    custom_int_h[6] custom_int_stack;
    vlan_tag_h inner_vlan;
}

    /********  G L O B A L   E G R E S S   M E T A D A T A  *********/

struct my_egress_metadata_t {
    bit<16> last_int_eth_type;
}

    /***********************  P A R S E R  **************************/

parser EgressParser(packet_in        pkt,
    /* User */
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    /* Intrinsic */
    out egress_intrinsic_metadata_t  eg_intr_md)
{
    /* This is a mandatory state, required by Tofino Architecture */
    state start {
        pkt.extract(eg_intr_md);
        transition parse_ethernet;
    }

    state parse_ethernet{
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type){
            ether_type_t.VLAN: parse_outer_vlan;
            ether_type_t.QINQ: parse_outer_vlan;
            // ether_type_t.INT: parse_int0;
            default: accept;
        }
    }

    state parse_outer_vlan{
        pkt.extract(hdr.outer_vlan);
        // transition accept;
        transition select(hdr.outer_vlan.ether_type){
            ether_type_t.INT: parse_int_shim;
            default: accept;
        }
    }
    state parse_int_shim{
        pkt.extract(hdr.custom_int_shim);
        transition select(hdr.custom_int_shim.int_count, hdr.custom_int_shim.next_hdr){
            (1, 0x8100): parse_0_int;
            (1,_): parse_0_int;
            (2, 0x8100): parse_1_int;
            (2,_): parse_1_int;
            (3, 0x8100): parse_2_int;
            (3,_): parse_2_int;
            (4, 0x8100): parse_3_int;
            (4,_): parse_3_int;
            (5, 0x8100): parse_4_int;
            (5,_): parse_4_int;
            (6, 0x8100): parse_5_int;
            (6,_): parse_5_int;
            (_,0x8100): parse_inner_vlan;
            default: accept;
        }
    }

    state parse_5_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        pkt.extract(hdr.custom_int_stack[4]);
        pkt.extract(hdr.custom_int_stack[5]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }

    state parse_4_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        pkt.extract(hdr.custom_int_stack[4]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }

    state parse_3_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }

    state parse_2_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }

    state parse_1_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }
    state parse_0_int{
        pkt.extract(hdr.custom_int_stack[0]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_inner_vlan;
            default: accept;
        }
    }

    state parse_inner_vlan{
        pkt.extract(hdr.inner_vlan);
        transition accept;
    }

}

    /***************** M A T C H - A C T I O N  *********************/

control Egress(
    /* User */
    inout my_egress_headers_t                          hdr,
    inout my_egress_metadata_t                         meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md)
{   
    //First INT, packet coming from user 
    action push_int0(){
        hdr.custom_int_stack[0].setValid();
        hdr.custom_int_stack[0].data = 0x1234;
    }
    action add_int_shim(){
        hdr.custom_int_shim.setValid();
        hdr.custom_int_shim.next_hdr = hdr.outer_vlan.ether_type;
        hdr.custom_int_shim.int_count = 1;
        hdr.outer_vlan.ether_type = 0x0601;
        push_int0();
    }
    action swap_outer_vlan(bit<12> new_vid){
        hdr.inner_vlan.setValid();
        hdr.inner_vlan.vid = hdr.outer_vlan.vid;
        hdr.inner_vlan.pri = hdr.outer_vlan.pri;
        hdr.inner_vlan.dei = hdr.outer_vlan.dei;
        hdr.inner_vlan.ether_type = hdr.outer_vlan.ether_type;
        hdr.outer_vlan.vid = new_vid;
        hdr.outer_vlan.pri = 0;
        hdr.outer_vlan.dei = 0;
        hdr.outer_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = 0x88a8;
        add_int_shim();
    }

    action modify_s_vlan(bit<12> new_vid){
        hdr.outer_vlan.vid = new_vid;
    }

    action remove_int(){
        hdr.custom_int_shim.setInvalid();
        hdr.custom_int_stack[0].setInvalid();
        hdr.custom_int_stack[1].setInvalid();
        hdr.custom_int_stack[2].setInvalid();
        hdr.custom_int_stack[3].setInvalid();
        hdr.custom_int_stack[4].setInvalid();
        hdr.custom_int_stack[5].setInvalid();
    }

    action swap_inner_to_outer_vlan(){
        hdr.outer_vlan.vid = hdr.inner_vlan.vid;
        hdr.outer_vlan.pri = hdr.inner_vlan.pri;
        hdr.outer_vlan.dei = hdr.inner_vlan.dei;
        hdr.outer_vlan.ether_type = hdr.inner_vlan.ether_type;
        hdr.inner_vlan.setInvalid();
    }

    action swap_vlans_rm_int(){
        hdr.ethernet.ether_type = hdr.custom_int_shim.next_hdr;
        remove_int();
        swap_inner_to_outer_vlan();
    }

    action rm_s_vlan(){
        hdr.outer_vlan.setInvalid();
    }

    action rm_s_vlan_rm_int(){
        hdr.ethernet.ether_type = hdr.custom_int_shim.next_hdr;
        rm_s_vlan();
        remove_int();
    }

    table egress_s_vlan_traffic_table{
        key = {
            eg_intr_md.egress_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.outer_vlan.vid: ternary;
        }
        actions = {
            swap_outer_vlan;
            add_int_shim;
            push_int0;
            modify_s_vlan;
            remove_int;
            swap_inner_to_outer_vlan;
            swap_vlans_rm_int;
            rm_s_vlan;
            rm_s_vlan_rm_int;
        }
        size = 1024;
    }

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
    table egress_int_table{
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
        }
        const entries = {
            1: push_int1();
            2: push_int2();
            3: push_int3();
            4: push_int4();
            5: push_int5();
        }
        size = 10;
    }

    action add_s_vlan(bit<12> new_vid){
        hdr.outer_vlan.setValid();
        hdr.outer_vlan.vid = new_vid;
        hdr.outer_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = 0x88a8;
        add_int_shim();
    }

    table egress_normal_traffic_table{
        key = {
            eg_intr_md.egress_port: exact;
        }
        actions = {
            remove_int;
            swap_inner_to_outer_vlan;
            swap_vlans_rm_int;
            add_s_vlan;
        }
        size = 1024;
    }


    apply {        
        
        if(hdr.custom_int_shim.isValid()){
            egress_int_table.apply();
        }
        if(egress_s_vlan_traffic_table.apply().miss){
            egress_normal_traffic_table.apply();
        }
    }
}

    /*********************  D E P A R S E R  ************************/

control EgressDeparser(packet_out pkt,
    /* User */
    inout my_egress_headers_t                       hdr,
    in    my_egress_metadata_t                      meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md)
{
    apply {

        pkt.emit(hdr);
    }
}


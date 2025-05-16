/* -*- P4_16 -*- */

/**************** V1.1 ****************/

/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

    /***********************  H E A D E R S  ************************/

struct my_egress_headers_t {
    ethernet_h   ethernet;
    vlan_tag_h outer_vlan_tag;
    custom_int_h[5] int_stack;
    vlan_tag_h[3] inner_vlan_tags;
    ipv4_h       ipv4;
    ipv6_h      ipv6;
    udp_h        udp;
    tcp_h        tcp;
    payload_h    payload;
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
            ether_type_t.INT: parse_int0;
            default: accept;
        }
    }

    state parse_outer_vlan{
        pkt.extract(hdr.outer_vlan_tag);
        transition select(hdr.outer_vlan_tag.ether_type){
            ether_type_t.INT: parse_int0;
            default: accept;
        }
    }

    state parse_int0{
        pkt.extract(hdr.int_stack[0]);
        transition select(hdr.int_stack[0].ether_type){
            ether_type_t.INT: parse_int1;
            ether_type_t.VLAN: parse_inner_vlan0;
            default: accept;
        }
    }
    state parse_int1{
        pkt.extract(hdr.int_stack[1]);
        transition select(hdr.int_stack[1].ether_type){
            ether_type_t.INT: parse_int2;
            ether_type_t.VLAN: parse_inner_vlan0;
            default: accept;
        }
    }
    state parse_int2{
        pkt.extract(hdr.int_stack[2]);
        transition select(hdr.int_stack[2].ether_type){
            ether_type_t.INT: parse_int3;
            ether_type_t.VLAN: parse_inner_vlan0;
            default: accept;
        }
    }
    state parse_int3{
        pkt.extract(hdr.int_stack[3]);
        transition select(hdr.int_stack[3].ether_type){
            ether_type_t.INT: parse_int4;
            ether_type_t.VLAN: parse_inner_vlan0;
            default: accept;
        }
    }
    state parse_int4{
        pkt.extract(hdr.int_stack[4]);
        transition select(hdr.int_stack[4].ether_type){
            ether_type_t.VLAN: parse_inner_vlan0;
            default: accept;
        }
    }

    state parse_inner_vlan0{
        pkt.extract(hdr.inner_vlan_tags[0]);
        transition select(hdr.inner_vlan_tags[0].ether_type){
            ether_type_t.VLAN: parse_inner_vlan1;
            default: accept;
        }
    }

    state parse_inner_vlan1{
        pkt.extract(hdr.inner_vlan_tags[1]);
        transition select(hdr.inner_vlan_tags[1].ether_type){
            ether_type_t.VLAN: parse_inner_vlan2;
            default: accept;
        }
    }

    state parse_inner_vlan2{
        pkt.extract(hdr.inner_vlan_tags[2]);
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

    action shift_int(){
        hdr.int_stack[4] = hdr.int_stack[3];
        hdr.int_stack[3] = hdr.int_stack[2];
        hdr.int_stack[2] = hdr.int_stack[1];
        hdr.int_stack[1] = hdr.int_stack[0];
        hdr.int_stack[0].ether_type = hdr.outer_vlan_tag.ether_type;
        hdr.int_stack[0].data = 0x5678;
        hdr.outer_vlan_tag.ether_type = ether_type_t.INT;
    }

    action push_int(){
        hdr.int_stack[0].setValid();
        hdr.int_stack[0].ether_type = hdr.outer_vlan_tag.ether_type;
        hdr.int_stack[0].data = 0x1234;
        hdr.outer_vlan_tag.ether_type = INT;
    }

    action pop_int() {
        hdr.int_stack[4].setInvalid();
        hdr.int_stack[3].setInvalid();
        hdr.int_stack[2].setInvalid();
        hdr.int_stack[1].setInvalid();
        hdr.int_stack[0].setInvalid();
        hdr.ethernet.ether_type = meta.last_int_eth_type;
    }

    action pop_int_and_add_vlan(bit<12> new_vid, ether_type_t new_ether_type){
        pop_int();
        hdr.outer_vlan_tag.setValid();
        hdr.outer_vlan_tag.vid = new_vid;
        hdr.outer_vlan_tag.ether_type = meta.last_int_eth_type;
        hdr.ethernet.ether_type = new_ether_type;   
    }

    action pop_and_vlan(bit<12> new_vid){
        hdr.outer_vlan_tag.vid = new_vid;
        hdr.outer_vlan_tag.ether_type = hdr.inner_vlan_tags[0].ether_type;
        hdr.outer_vlan_tag.pri = hdr.inner_vlan_tags[0].pri;
        hdr.outer_vlan_tag.dei = hdr.inner_vlan_tags[0].dei;
        hdr.inner_vlan_tags[0].setInvalid();
        hdr.inner_vlan_tags[1].setInvalid();
        hdr.inner_vlan_tags[2].setInvalid();
        pop_int();
    }


    table egress_vlan_traffic_table{
        key = {
            eg_intr_md.egress_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.outer_vlan_tag.vid: ternary;
        }
        actions = {
            shift_int;
            push_int;
            pop_int;
            pop_int_and_add_vlan;
            pop_and_vlan;
        }
        size = 1024;
    }

    table egress_traffic_table{
        key = {
            eg_intr_md.egress_port: exact;
            hdr.ethernet.ether_type: exact;
            //ingress port
            
        }
        actions = {
            pop_int;
            pop_int_and_add_vlan;
        }
        size = 1024;
    }

    apply {        
            if(hdr.int_stack[4].isValid()){
                meta.last_int_eth_type = hdr.int_stack[4].ether_type;
            }
            else if(hdr.int_stack[3].isValid()){
                meta.last_int_eth_type = hdr.int_stack[3].ether_type;
            }
            else if(hdr.int_stack[2].isValid()){
                meta.last_int_eth_type = hdr.int_stack[2].ether_type;
            }
            else if(hdr.int_stack[1].isValid()){
                meta.last_int_eth_type = hdr.int_stack[1].ether_type;
            }
            else if(hdr.int_stack[0].isValid()){
                meta.last_int_eth_type = hdr.int_stack[0].ether_type;
            }
        if(egress_vlan_traffic_table.apply().miss){
            egress_traffic_table.apply();
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


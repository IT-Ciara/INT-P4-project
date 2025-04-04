/* -*- P4_16 -*- */

/**************** V1.1 ****************/

/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

    /***********************  H E A D E R S  ************************/

struct my_ingress_headers_t {
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

    /******  G L O B A L   I N G R E S S   M E T A D A T A  *********/

struct my_ingress_metadata_t {
}

    /***********************  P A R S E R  **************************/
parser IngressParser(packet_in        pkt,
    /* User */
    out my_ingress_headers_t          hdr,
    out my_ingress_metadata_t         meta,
    /* Intrinsic */
    out ingress_intrinsic_metadata_t  ig_intr_md)
{
    /* This is a mandatory state, required by Tofino Architecture */
    state start {
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);
        transition parse_ethernet;
    }
    state parse_ethernet{
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type){
            ether_type_t.VLAN: parse_outer_vlan;
            ether_type_t.QINQ: parse_outer_vlan;
            default: accept;
        }
    }
    state parse_outer_vlan{
        pkt.extract(hdr.outer_vlan_tag);
        transition accept;
    }
}

    /***************** M A T C H - A C T I O N  *********************/

control Ingress(
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{   
    action forward(PortId_t egress_port){
        ig_tm_md.ucast_egress_port = egress_port;
    }
    action swap_vlan_id(bit<12> new_vid, PortId_t egress_port){
        hdr.outer_vlan_tag.vid = new_vid;
        ig_tm_md.ucast_egress_port = egress_port;
    }
    action push_outer_vlan(bit<12> new_vid, ether_type_t new_ether_type, PortId_t egress_port){
        hdr.outer_vlan_tag.setValid();
        hdr.outer_vlan_tag.vid = new_vid;
        hdr.outer_vlan_tag.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = new_ether_type;
        ig_tm_md.ucast_egress_port = egress_port;
    }
    action swap_vlan(bit<12> new_vid, ether_type_t new_ether_type, PortId_t egress_port){
        hdr.inner_vlan_tags[0].setValid();  
        hdr.inner_vlan_tags[0].vid = hdr.outer_vlan_tag.vid;
        hdr.inner_vlan_tags[0].ether_type = hdr.outer_vlan_tag.ether_type;
        hdr.inner_vlan_tags[0].pri = hdr.outer_vlan_tag.pri;
        hdr.inner_vlan_tags[0].dei = hdr.outer_vlan_tag.dei;
        push_outer_vlan(new_vid, new_ether_type, egress_port);
    }
    action pop_outer_vlan(PortId_t egress_port){
        hdr.ethernet.ether_type = hdr.outer_vlan_tag.ether_type;
        hdr.outer_vlan_tag.setInvalid();
        ig_tm_md.ucast_egress_port = egress_port;
    }
    
    table ingress_vlan_traffic_table{
        key = {
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
            hdr.outer_vlan_tag.vid: ternary;
        }
        actions = {
            forward;
            push_outer_vlan;
            swap_vlan_id;
            swap_vlan;
            pop_outer_vlan;
        }
        size = 100;
    }

    table ingress_normal_traffic_table{
        key = {
            ig_intr_md.ingress_port: exact;
            // ig_tm_md.ucast_egress_port: exact;
        }
        actions = {
            push_outer_vlan;
            forward;
        }
        size = 100;
    }
    apply {
        if(ingress_vlan_traffic_table.apply().miss){
            ingress_normal_traffic_table.apply();
        }

    }
}

    /*********************  D E P A R S E R  ************************/

control IngressDeparser(packet_out pkt,
    /* User */
    inout my_ingress_headers_t                       hdr,
    in    my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md)
{
    apply {
        pkt.emit(hdr);
    }
}

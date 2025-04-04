/* -*- P4_16 -*- */

/**************** V1.2 ****************/

/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

    /***********************  H E A D E R S  ************************/

struct my_ingress_headers_t {
    ethernet_h   ethernet;
    vlan_tag_h outer_vlan;
    custom_int_shim_h custom_int_shim;
    custom_int_h[6] custom_int_stack;
    vlan_tag_h inner_vlan;
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
        pkt.extract(hdr.outer_vlan);
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

    action add_u_vlan(bit<12> new_vid, PortId_t egress_port){
        hdr.outer_vlan.setValid();
        hdr.outer_vlan.vid = new_vid;
        hdr.outer_vlan.dei = 0;
        hdr.outer_vlan.pri = 0;
        hdr.outer_vlan.ether_type = hdr.ethernet.ether_type;
        hdr.ethernet.ether_type = 0x8100;
        ig_tm_md.ucast_egress_port = egress_port;
    }

    table no_vlan_traffic_table{
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            add_u_vlan;
            forward;
        }
        size = 100;
    }

    action modify_u_vlan(bit<12> new_vid, PortId_t egress_port){
        hdr.outer_vlan.vid = new_vid;
        ig_tm_md.ucast_egress_port = egress_port;
    }

    table vlan_traffic_table{
        key = {
            hdr.outer_vlan.vid: ternary;
            ig_intr_md.ingress_port: exact;
            hdr.ethernet.ether_type: exact;
        }
        actions = {
            modify_u_vlan;
            forward;
        }
        size = 100;
    }

    apply {
        if(vlan_traffic_table.apply().miss){
            no_vlan_traffic_table.apply();
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

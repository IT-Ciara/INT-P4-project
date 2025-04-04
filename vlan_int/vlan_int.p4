/* -*- P4_16 -*- */

#include <core.p4>
#include <tna.p4>

/*************************************************************************
 ************* C O N S T A N T S    A N D   T Y P E S  *******************
**************************************************************************/

const PortId_t CPU_ETH_PORT=64;
const PortId_t CPU_PCIE_PORT_4pipes=320;
const PortId_t CPU_PCIE_PORT_2pipes=192;

/* indicate INT by DSCP value */
const bit<6> DSCP_INT = 0x17;
const bit<6> DSCP_MASK = 0x3F;

typedef bit<48> timestamp_t;
typedef bit<32> switch_id_t;

const bit<8> INT_HEADER_LEN_WORD = 3;
const bit<16> INT_HEADER_SIZE = 8;
const bit<16> INT_SHIM_HEADER_SIZE = 4;
const bit<3> NPROTO_ETHERNET = 0;
const bit<6> HW_ID = 1;
const bit<8> REPORT_HDR_TTL = 64;

#define ETH_TYPE_IPV4 0x0800
#define ETH_TYPE_VLAN  0x8100
#define ETH_TYPE_SVLAN 0x9100  // 0x9100 0x88A8
#define ETH_TYPE_IPV6  0x86DD

#define IP_PROTO_HOPOPT         8w0
#define IP_PROTO_ICMP           8w1
#define IP_PROTO_IGMP           8w2
#define IP_PROTO_TCP            8w6
#define IP_PROTO_UDP            8w17
#define IP_PROTO_IPV6_ROUTE     8w43
#define IP_PROTO_IPV6_FRAGMENT  8w44
#define IP_PROTO_IPSEC_ESP      8w50
#define IP_PROTO_IPSEC_AH       8w51
#define IP_PROTO_IPV6_OPTS      8w60
#define IP_PROTO_MOBILITY       8w135
#define IP_PROTO_SHIM6          8w140
#define IP_PROTO_RESERVED_FD    8w253
#define IP_PROTO_RESERVED_FE    8w254

#define IP_VERSION_4            4w4
#define IP_VERSION_6            4w6
#define IPV4_IHL_MIN            4w5

const bit<16> IPV4_MIN_HEAD_LEN = 20;
const bit<16> UDP_HEADER_LEN = 8;
const bit<16> VLAN_HEADER_LEN = 4;
const bit<16> ETH_HEADER_LEN = 14;

typedef bit<16>  ether_type_t;
typedef bit<48>  mac_addr_t;
typedef bit<32>  ipv4_addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<16>  l4_port_t;
typedef bit<16> mirror_id_t;

header packet_in_h {
    bit<9> ingress_port;
    bit<7> _padding;
}

header packet_out_h {
    bit<9> egress_port;
    bit<7> _padding;
}

typedef bit<4> header_type_t;
typedef bit<4> header_info_t;

const header_type_t HEADER_TYPE_BRIDGE         = 0xB;
const header_type_t HEADER_TYPE_MIRROR_INGRESS = 0xC;
const header_type_t HEADER_TYPE_MIRROR_EGRESS  = 0xD;

// #define INTERNAL_HEADER         \
//     header_type_t header_type;  \
//     header_info_t header_info


header inthdr_h {
    header_type_t header_type;
    header_info_t header_info;
}

/* Bridged metadata */
header bridge_h {
    header_type_t header_type;
    header_info_t header_info;
    @flexible     PortId_t      ingress_port;
    bit<1>        is_sink;
    bit<1>        is_source;
    bit<1>        is_transit;
    bit<1>        is_report;
    bit<4>        pad1;
    bit<32>       ingress_mac_tstamp;
}

/* Ingress mirroring information */
const MirrorType_t ING_PORT_MIRROR = 3;
const MirrorType_t EGR_PORT_MIRROR = 5;

header egr_port_mirror_h {
    header_type_t header_type;
    header_info_t header_info;                                  /* 1B */
    bit<8>                 flags;                       /* 1B */
    @padding      bit<16>  pad2;                        /* 2B */
    bit<16>                ingress_port;                /* 2B */
    bit<16>                egress_port;                 /* 2B */
    bit<32>                ingress_mac_tstamp;          /* 4B */
    bit<32>                egress_global_tstamp;        /* 4B */
    bit<24>                enq_qdepth;                  /* 3B */
    bit<8>                 egress_qid;                  /* 1B */
    //bit<2>                 enq_congest_stat;            /* 1B */
    //bit<6>                 pad2;
}


/*************************************************************************
 ***********************  H E A D E R S  *********************************
 *************************************************************************/

// INT version 1.0

// INT header
header int_header_t {
    bit<4>  ver;
    bit<2>  rep;
    bit<1>  c;
    bit<1>  e;
    bit<1>  m;
    bit<7>  rsvd1;
    bit<3>  rsvd2;
    bit<5>  hop_metadata_len;
    bit<8>  remaining_hop_cnt;
    bit<4>  instruction_mask_0003; /* split the bits for lookup */
    bit<4>  instruction_mask_0407;
    bit<4>  instruction_mask_0811;
    bit<4>  instruction_mask_1215;
    bit<16> rsvd3;
}

// INT meta-value headers - different header for each value type
header int_switch_id_t {
    bit<32> switch_id;
}
header int_level1_port_ids_t {
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
}
header int_hop_latency_t {
    bit<32> hop_latency;
}
header int_q_occupancy_t {
    bit<8> q_id;
    bit<24> q_occupancy;
}
header int_ingress_tstamp_t {
    bit<32> ingress_tstamp;
}
header int_egress_tstamp_t {
    bit<32> egress_tstamp;
}
header int_level2_port_ids_t {
    bit<32> ingress_port_id;
    bit<32> egress_port_id;
}
header int_egress_port_tx_util_t {
    bit<32> egress_port_tx_util;
}

header int_data_t {
    // Maximum int metadata stack size in bits:
    // (0x3F - 3) * 4 * 8 (excluding INT shim header and INT header)
    varbit<1920> data;
}

// INT shim header for TCP/UDP
header intl4_shim_t {
    bit<8> int_type;
    bit<8> rsvd1;
    bit<8> len;
    bit<6> dscp;
    bit<2> rsvd2;
}

struct int_metadata_t {
    switch_id_t switch_id;
    bit<16> new_bytes;
    bit<8>  new_words;
    bit<8>  intl4_shim_len;
}

// Report Telemetry Headers
header report_fixed_header_t {
    bit<4>  ver;
    bit<4>  len;
    bit<3>  nproto;
    bit<6>  rep_md_bits;
    bit<1>  d;
    bit<1>  q;
    bit<1>  f;
    bit<6>  rsvd;
    bit<6>  hw_id;
    bit<32> sw_id;
    bit<32> seq_no;
    bit<32> ingress_tstamp;
}
const bit<16> REPORT_FIXED_HEADER_LEN = 16;


header ethernet_h {
    mac_addr_t    dst_addr;
    mac_addr_t    src_addr;
}

header vlan_h {
    ether_type_t  ether_type;
    bit<3>        pcp;
    bit<1>        dei;
    bit<12>       vid;
}

header etherII_h {
    ether_type_t ether_type;
}

header ipv4_h {
    bit<4>       version;
    bit<4>       ihl;
    bit<6>       dscp;
    bit<2>       ecn;
    bit<16>      len;
    bit<16>      identification;
    bit<3>       flags;
    bit<13>      frag_offset;
    bit<8>       ttl;
    bit<8>       protocol;
    bit<16>      hdr_checksum;
    ipv4_addr_t  src_addr;
    ipv4_addr_t  dst_addr;
}

header tcp_h {
    bit<16>  src_port;
    bit<16>  dst_port;
    bit<32>  seq_no;
    bit<32>  ack_no;
    bit<4>   data_offset;
    bit<4>   res;
    bit<8>   flags;
    bit<16>  window;
    bit<16>  checksum;
    bit<16>  urgent_ptr;
}

header udp_h {
    bit<16>  src_port;
    bit<16>  dst_port;
    bit<16>  len;
    bit<16>  checksum;
}

struct packet_headers_t {
    packet_out_h packet_out;
    packet_in_h packet_in;
    bridge_h                   bridge;
    /* INT */
    ethernet_h             report_ethernet;
    etherII_h              report_etherII;
    ipv4_h                 report_ipv4;
    udp_h                  report_udp;
    // INT Report Headers
    report_fixed_header_t  report_fixed_header;
    /* end INT */
    ethernet_h                 ethernet;
    vlan_h[3]                  vlan_list;
    etherII_h                  etherII;
    ipv4_h                     ipv4;
    tcp_h                      tcp;
    udp_h                      udp;
    /* INT */
    intl4_shim_t               intl4_shim;
    int_header_t               int_header;
    int_switch_id_t            int_switch_id;
    int_level1_port_ids_t      int_level1_port_ids;
    int_hop_latency_t          int_hop_latency;
    int_q_occupancy_t          int_q_occupancy;
    int_ingress_tstamp_t       int_ingress_tstamp;
    int_egress_tstamp_t        int_egress_tstamp;
    int_level2_port_ids_t      int_level2_port_ids;
    int_egress_port_tx_util_t  int_egress_tx_util;
    int_data_t                 int_data;
}

struct ingress_metadata_t {
    bool             compute_checksum_ipv4;
}

struct egress_metadata_t {
    inthdr_h           inthdr;
    bridge_h           bridge;
    bool               egr_mirrored;
    egr_port_mirror_h  egr_port_mirror;
    int_metadata_t     int_meta;
    header_type_t      mirror_header_type;
    header_info_t      mirror_header_info;
    MirrorId_t         egr_mirror_session;
    bit<16>            ingress_port;
    bit<16>            egress_port;
    bit<32>            egress_global_tstamp;
    bit<24>            enq_qdepth;
    bit<8>             egress_qid;
    bool               compute_checksum_ipv4;
}

/*************************************************************************
 ******************  P A C K E T   I O   C O N T R O L *******************
 *************************************************************************/
control packetio_ingress(
    inout packet_headers_t                           hdr,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{

    action output(PortId_t port) {
        ig_tm_md.ucast_egress_port = port;
    }
    apply {
        if (hdr.packet_out.isValid()) {
            ig_tm_md.ucast_egress_port = hdr.packet_out.egress_port;
            hdr.packet_out.setInvalid();
        }
     }
}

/*************************************************************************
 *********************  V L A N   C O N T R O L **************************
 *************************************************************************/

control vlan_control(
    inout packet_headers_t                           hdr,
    inout ingress_metadata_t                         meta,
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{

    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) vlan_counter;

    action push_vlan(bit<12> vlan, PortId_t port) {
        hdr.vlan_list.push_front(1);
        hdr.vlan_list[0].setValid();
        hdr.vlan_list[0].vid = vlan;
        hdr.vlan_list[0].ether_type = ETH_TYPE_SVLAN;
        hdr.vlan_list[0].pcp = 0;
        hdr.vlan_list[0].dei = 0;
        ig_tm_md.ucast_egress_port = port;
        vlan_counter.count();
    }

    action pop_vlan(PortId_t port) {
        hdr.vlan_list.pop_front(1);
        ig_tm_md.ucast_egress_port = port;
        vlan_counter.count();
    }

    action set_vlan(bit<12> vlan, PortId_t port) {
        hdr.vlan_list[0].vid = vlan;
        ig_tm_md.ucast_egress_port = port;
        vlan_counter.count();
    }

    action output(PortId_t port) {
        ig_tm_md.ucast_egress_port = port;
        vlan_counter.count();
    }

    action send_to_cpu() {
        ig_tm_md.ucast_egress_port = CPU_ETH_PORT;
        vlan_counter.count();
    }

    action drop() {
        ig_dprsr_md.drop_ctl = 1;
        vlan_counter.count();
    }

    table vlan {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.vlan_list[0].vid    : ternary @name("vlan_vid");
        }
        actions = {
            push_vlan;
            pop_vlan;
            set_vlan;
            output;
            send_to_cpu;
            drop;
            @defaultonly NoAction;
        }
        const default_action = NoAction();
        counters = vlan_counter;
        size = 1024;
    }

    apply {
        //if (hdr.vlan_list[0].isValid()) {
            vlan.apply();
        //}
     }
}


/*************************************************************************
 ***********************  I N T  C O N T R O L  **************************
 *************************************************************************/

control process_int_source_transit_sink (
    inout packet_headers_t             hdr,
    inout ingress_metadata_t           meta,
    in ingress_intrinsic_metadata_t    ig_intr_md) {

    action int_set_source () {
        hdr.bridge.is_source = 1;
    }

    action int_set_transit () {
        hdr.bridge.is_transit = 1;
    }

    action int_set_sink () {
        hdr.bridge.is_sink = 1;
    }

    action int_set_report () {
        hdr.bridge.is_report = 1;
    }

    table tb_set_source {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.vlan_list[0].vid    : exact @name("vlan_vid");
        }
        actions = {
            int_set_source;
            @defaultonly NoAction();
        }
        const default_action = NoAction();
        size = 1024;
    }
    table tb_set_transit {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.vlan_list[0].vid    : exact @name("vlan_vid");
        }
        actions = {
            int_set_transit;
            @defaultonly NoAction();
        }
        const default_action = NoAction();
        size = 1024;
    }
    table tb_set_sink {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.vlan_list[0].vid    : exact @name("vlan_vid");
        }
        actions = {
            int_set_sink;
            @defaultonly NoAction();
        }
        const default_action = NoAction();
        size = 1024;
    }
    table tb_set_report {
        key = {
            ig_intr_md.ingress_port : exact;
            hdr.vlan_list[0].vid    : exact @name("vlan_vid");
        }
        actions = {
            int_set_report;
            @defaultonly NoAction();
        }
        const default_action = NoAction();
        size = 1024;
    }

    apply {
        if (hdr.vlan_list[0].isValid()) {
            tb_set_source.apply();
            tb_set_transit.apply();
            tb_set_sink.apply();
            tb_set_report.apply();
        }
    }
}

control process_int_source (
    inout packet_headers_t             hdr,
    inout egress_metadata_t            meta,
    in egress_intrinsic_metadata_t    eg_intr_md) {

    action int_source(bit<5> hop_metadata_len, bit<8> remaining_hop_cnt, bit<4> ins_mask0003, bit<4> ins_mask0407) {
        // insert INT shim header
        hdr.intl4_shim.setValid();
        // int_type: Hop-by-hop type (1) , destination type (2)
        hdr.intl4_shim.int_type = 1;
        hdr.intl4_shim.rsvd1 = 0;
        hdr.intl4_shim.len = INT_HEADER_LEN_WORD;
        hdr.intl4_shim.dscp = hdr.ipv4.dscp;
        hdr.intl4_shim.rsvd2 = 0;

        // insert INT header
        hdr.int_header.setValid();
        hdr.int_header.ver = 0;
        hdr.int_header.rep = 0;
        hdr.int_header.c = 0;
        hdr.int_header.e = 0;
        hdr.int_header.m = 0;
        hdr.int_header.rsvd1 = 0;
        hdr.int_header.rsvd2 = 0;
        hdr.int_header.hop_metadata_len = hop_metadata_len;
        hdr.int_header.remaining_hop_cnt = remaining_hop_cnt;
        hdr.int_header.instruction_mask_0003 = ins_mask0003;
        hdr.int_header.instruction_mask_0407 = ins_mask0407;
        hdr.int_header.instruction_mask_0811 = 0; // not supported
        hdr.int_header.instruction_mask_1215 = 0; // not supported

        // add the header len (3 words) to total len
        hdr.ipv4.len = hdr.ipv4.len + INT_HEADER_SIZE + INT_SHIM_HEADER_SIZE;
        //hdr.udp.len = hdr.udp.len + INT_HEADER_SIZE + INT_SHIM_HEADER_SIZE;
    }

    action int_source_dscp(bit<5> hop_metadata_len, bit<8> remaining_hop_cnt, bit<4> ins_mask0003, bit<4> ins_mask0407) {
        int_source(hop_metadata_len, remaining_hop_cnt, ins_mask0003, ins_mask0407);
        hdr.ipv4.dscp = DSCP_INT;
        meta.compute_checksum_ipv4 = true;
    }

    table tb_int_source {
        key = {
            meta.bridge.is_source   : exact @name("is_source");
        }
        actions = {
            int_source_dscp;
            @defaultonly NoAction();
        }
        const default_action = NoAction();
        size = 1;
    }

    apply {
        if (meta.bridge.is_source == 1 && (hdr.tcp.isValid() || hdr.udp.isValid())) {
            tb_int_source.apply();
        }
    }
}

control process_int_report (
    inout packet_headers_t                      hdr,
    inout egress_metadata_t                     meta,
    in egress_intrinsic_metadata_t              eg_intr_md
) {

    bit<16> temp_report_pkt_len;

    action add_report_fixed_header() {
        hdr.report_fixed_header.setValid();
        hdr.report_fixed_header.ver = 1;
        hdr.report_fixed_header.len = 4;
        /* only support for flow_watchlist */
        hdr.report_fixed_header.nproto = NPROTO_ETHERNET;
        hdr.report_fixed_header.rep_md_bits = 0;
        hdr.report_fixed_header.d = 0;
        hdr.report_fixed_header.q = 0;
        hdr.report_fixed_header.f = 1;
        hdr.report_fixed_header.rsvd = 0;
        //TODO how to get information specific to the switch
        hdr.report_fixed_header.hw_id = HW_ID;
        //hdr.report_fixed_header.sw_id = meta.int_meta.switch_id;
        hdr.report_fixed_header.sw_id = 0x00000001;
        // TODO how save a variable and increment
        hdr.report_fixed_header.seq_no = 0;
        //TODO how to get timestamp from ingress ns
        hdr.report_fixed_header.ingress_tstamp =  0;
    }

    action compute_report_pkt_length() {
        temp_report_pkt_len = UDP_HEADER_LEN + REPORT_FIXED_HEADER_LEN + eg_intr_md.pkt_length; 
    }

    action add_report_udp_header(l4_port_t mon_port) {
        //Report UDP Header
        hdr.report_udp.setValid();
        hdr.report_udp.src_port = 5900;
        hdr.report_udp.dst_port = mon_port;
        hdr.report_udp.len = temp_report_pkt_len;
        hdr.report_udp.checksum = 0;
    }

    action do_report_encapsulation(mac_addr_t src_mac, mac_addr_t mon_mac, ipv4_addr_t src_ip,
                        ipv4_addr_t mon_ip, l4_port_t mon_port) {
        //Report Ethernet Header
        hdr.report_ethernet.setValid();
        hdr.report_ethernet.dst_addr = mon_mac;
        hdr.report_ethernet.src_addr = src_mac;
        hdr.report_etherII.setValid();
        hdr.report_etherII.ether_type = ETH_TYPE_IPV4;

        //Report IPV4 Header
        hdr.report_ipv4.setValid();
        hdr.report_ipv4.version = IP_VERSION_4;
        hdr.report_ipv4.ihl = IPV4_IHL_MIN;
        hdr.report_ipv4.dscp = 6w0;
        hdr.report_ipv4.ecn = 2w0;
        hdr.report_ipv4.len = IPV4_MIN_HEAD_LEN + temp_report_pkt_len;
        /* Dont Fragment bit should be set */
        hdr.report_ipv4.identification = 0;
        hdr.report_ipv4.flags = 0;
        hdr.report_ipv4.frag_offset = 0;
        hdr.report_ipv4.ttl = REPORT_HDR_TTL;
        hdr.report_ipv4.protocol = IP_PROTO_UDP;
        hdr.report_ipv4.src_addr = src_ip;
        hdr.report_ipv4.dst_addr = mon_ip;
        meta.compute_checksum_ipv4 = true;

        add_report_udp_header(mon_port);

        add_report_fixed_header();
    }

    // Cloned packet is forwarded according to the mirroring_add command
    table tb_generate_report {
        // We don't really need a key here, however we add a dummy one as a
        // workaround to ONOS inability to properly support default actions.
        key = {
            hdr.int_header.isValid(): exact @name("int_is_valid");
        }
        actions = {
            do_report_encapsulation;
            @defaultonly NoAction();
        }
        default_action = NoAction;
        size = 1;
    }

    apply {
        compute_report_pkt_length();
        tb_generate_report.apply();
    }
}

control process_int_transit (
    inout packet_headers_t                      hdr,
    inout egress_metadata_t                     meta,
    in egress_intrinsic_metadata_t              eg_intr_md,
    in egress_intrinsic_metadata_from_parser_t  eg_prsr_md) {

    action init_metadata(switch_id_t switch_id) {
        meta.int_meta.switch_id = switch_id;
    }

    @hidden
    action int_set_header_0() { //switch_id
        hdr.int_switch_id.setValid();
        hdr.int_switch_id.switch_id = meta.int_meta.switch_id;
    }
    @hidden
    action int_set_header_1() { //level1_port_id
        hdr.int_level1_port_ids.setValid();
        hdr.int_level1_port_ids.ingress_port_id = (bit<16>) meta.bridge.ingress_port;
        hdr.int_level1_port_ids.egress_port_id = (bit<16>) eg_intr_md.egress_port;
    }
    @hidden
    action int_set_header_2() { //hop_latency
        hdr.int_hop_latency.setValid();
        hdr.int_hop_latency.hop_latency = (bit<32>) eg_prsr_md.global_tstamp - meta.bridge.ingress_mac_tstamp;
    }
    @hidden
    action int_set_header_3() { //q_occupancy
        hdr.int_q_occupancy.setValid();
        hdr.int_q_occupancy.q_id = (bit<8>)eg_intr_md.egress_qid;
        hdr.int_q_occupancy.q_occupancy = (bit<24>)eg_intr_md.enq_qdepth;
    }
    @hidden
    action int_set_header_4() { //ingress_tstamp
        hdr.int_ingress_tstamp.setValid();
        hdr.int_ingress_tstamp.ingress_tstamp = meta.bridge.ingress_mac_tstamp;
    }
    @hidden
    action int_set_header_5() { //egress_timestamp
        hdr.int_egress_tstamp.setValid();
        hdr.int_egress_tstamp.egress_tstamp = (bit<32>) eg_prsr_md.global_tstamp;
    }
    @hidden
    action int_set_header_6() { //level2_port_id
        hdr.int_level2_port_ids.setValid();
        // level2_port_id indicates Logical port ID
        hdr.int_level2_port_ids.ingress_port_id = (bit<32>) meta.bridge.ingress_port;
        hdr.int_level2_port_ids.egress_port_id = (bit<32>) eg_intr_md.egress_port;
     }
    @hidden
    action int_set_header_7() { //egress_port_tx_utilization
        // TODO: implement tx utilization ??
        hdr.int_egress_tx_util.setValid();
        hdr.int_egress_tx_util.egress_port_tx_util = 0;
    }

    // Actions to keep track of the new metadata added.
    @hidden
    action add_1() {
        meta.int_meta.new_words = meta.int_meta.new_words + 1;
        meta.int_meta.new_bytes = meta.int_meta.new_bytes + 4;
    }

    @hidden
    action add_2() {
        meta.int_meta.new_words = meta.int_meta.new_words + 2;
        meta.int_meta.new_bytes = meta.int_meta.new_bytes + 8;
    }

    @hidden
    action add_3() {
        meta.int_meta.new_words = meta.int_meta.new_words + 3;
        meta.int_meta.new_bytes = meta.int_meta.new_bytes + 12;
    }

    @hidden
    action add_4() {
        meta.int_meta.new_words = meta.int_meta.new_words + 4;
        meta.int_meta.new_bytes = meta.int_meta.new_bytes + 16;
    }

    @hidden
    action add_5() {
        meta.int_meta.new_words = meta.int_meta.new_words + 5;
        meta.int_meta.new_bytes = meta.int_meta.new_bytes + 20;
    }

     /* action function for bits 0-3 combinations, 0 is msb, 3 is lsb */
     /* Each bit set indicates that corresponding INT header should be added */
    @hidden
     action int_set_header_0003_i0() {
     }
    @hidden
     action int_set_header_0003_i1() {
        int_set_header_3();
        add_1();
    }
    @hidden
    action int_set_header_0003_i2() {
        int_set_header_2();
        add_1();
    }
    @hidden
    action int_set_header_0003_i3() {
        int_set_header_3();
        int_set_header_2();
        add_2();
    }
    @hidden
    action int_set_header_0003_i4() {
        int_set_header_1();
        add_1();
    }
    @hidden
    action int_set_header_0003_i5() {
        int_set_header_3();
        int_set_header_1();
        add_2();
    }
    @hidden
    action int_set_header_0003_i6() {
        int_set_header_2();
        int_set_header_1();
        add_2();
    }
    @hidden
    action int_set_header_0003_i7() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_1();
        add_3();
    }
    @hidden
    action int_set_header_0003_i8() {
        int_set_header_0();
        add_1();
    }
    @hidden
    action int_set_header_0003_i9() {
        int_set_header_3();
        int_set_header_0();
        add_2();
    }
    @hidden
    action int_set_header_0003_i10() {
        int_set_header_2();
        int_set_header_0();
        add_2();
    }
    @hidden
    action int_set_header_0003_i11() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_0();
        add_3();
    }
    @hidden
    action int_set_header_0003_i12() {
        int_set_header_1();
        int_set_header_0();
        add_2();
    }
    @hidden
    action int_set_header_0003_i13() {
        int_set_header_3();
        int_set_header_1();
        int_set_header_0();
        add_3();
    }
    @hidden
    action int_set_header_0003_i14() {
        int_set_header_2();
        int_set_header_1();
        int_set_header_0();
        add_3();
    }
    @hidden
    action int_set_header_0003_i15() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_1();
        int_set_header_0();
        add_4();
    }

     /* action function for bits 4-7 combinations, 4 is msb, 7 is lsb */
    @hidden
    action int_set_header_0407_i0() {
    }
    @hidden
    action int_set_header_0407_i1() {
        int_set_header_7();
        add_1();
    }
    @hidden
    action int_set_header_0407_i2() {
        int_set_header_6();
        add_2();
    }
    @hidden
    action int_set_header_0407_i3() {
        int_set_header_7();
        int_set_header_6();
        add_3();
    }
    @hidden
    action int_set_header_0407_i4() {
        int_set_header_5();
        add_1();
    }
    @hidden
    action int_set_header_0407_i5() {
        int_set_header_7();
        int_set_header_5();
        add_2();
    }
    @hidden
    action int_set_header_0407_i6() {
        int_set_header_6();
        int_set_header_5();
        add_3();
    }
    @hidden
    action int_set_header_0407_i7() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_5();
        add_4();
    }
    @hidden
    action int_set_header_0407_i8() {
        int_set_header_4();
        add_1();
    }
    @hidden
    action int_set_header_0407_i9() {
        int_set_header_7();
        int_set_header_4();
        add_2();
    }
    @hidden
    action int_set_header_0407_i10() {
        int_set_header_6();
        int_set_header_4();
        add_3();
    }
    @hidden
    action int_set_header_0407_i11() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_4();
        add_4();
    }
    @hidden
    action int_set_header_0407_i12() {
        int_set_header_5();
        int_set_header_4();
        add_2();
    }
    @hidden
    action int_set_header_0407_i13() {
        int_set_header_7();
        int_set_header_5();
        int_set_header_4();
        add_3();
    }
    @hidden
    action int_set_header_0407_i14() {
        int_set_header_6();
        int_set_header_5();
        int_set_header_4();
        add_4();
    }
    @hidden
    action int_set_header_0407_i15() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_5();
        int_set_header_4();
        add_5();
    }

    // Default action used to set switch ID.
    table tb_int_insert {
        // TODO: We don't really need a key here, however we add a dummy one as a
        // workaround to ONOS inability to properly support default actions.
        key = {
            hdr.int_header.isValid(): exact @name("int_is_valid");
        }
        actions = {
            init_metadata;
            @defaultonly NoAction;
        }
        const default_action = NoAction();
        size = 1;
    }

    /* Table to process instruction bits 0-3 */
    @hidden
    table tb_int_inst_0003 {
        key = {
            hdr.int_header.instruction_mask_0003 : exact;
        }
        actions = {
            int_set_header_0003_i0;
            int_set_header_0003_i1;
            int_set_header_0003_i2;
            int_set_header_0003_i3;
            int_set_header_0003_i4;
            int_set_header_0003_i5;
            int_set_header_0003_i6;
            int_set_header_0003_i7;
            int_set_header_0003_i8;
            int_set_header_0003_i9;
            int_set_header_0003_i10;
            int_set_header_0003_i11;
            int_set_header_0003_i12;
            int_set_header_0003_i13;
            int_set_header_0003_i14;
            int_set_header_0003_i15;
        }
        const entries = {
            (0x0) : int_set_header_0003_i0();
            (0x1) : int_set_header_0003_i1();
            (0x2) : int_set_header_0003_i2();
            (0x3) : int_set_header_0003_i3();
            (0x4) : int_set_header_0003_i4();
            (0x5) : int_set_header_0003_i5();
            (0x6) : int_set_header_0003_i6();
            (0x7) : int_set_header_0003_i7();
            (0x8) : int_set_header_0003_i8();
            (0x9) : int_set_header_0003_i9();
            (0xA) : int_set_header_0003_i10();
            (0xB) : int_set_header_0003_i11();
            (0xC) : int_set_header_0003_i12();
            (0xD) : int_set_header_0003_i13();
            (0xE) : int_set_header_0003_i14();
            (0xF) : int_set_header_0003_i15();
        }
    }

    /* Table to process instruction bits 4-7 */
    @hidden
    table tb_int_inst_0407 {
        key = {
            hdr.int_header.instruction_mask_0407 : exact;
        }
        actions = {
            int_set_header_0407_i0;
            int_set_header_0407_i1;
            int_set_header_0407_i2;
            int_set_header_0407_i3;
            int_set_header_0407_i4;
            int_set_header_0407_i5;
            int_set_header_0407_i6;
            int_set_header_0407_i7;
            int_set_header_0407_i8;
            int_set_header_0407_i9;
            int_set_header_0407_i10;
            int_set_header_0407_i11;
            int_set_header_0407_i12;
            int_set_header_0407_i13;
            int_set_header_0407_i14;
            int_set_header_0407_i15;
        }
        const entries = {
            (0x0) : int_set_header_0407_i0();
            (0x1) : int_set_header_0407_i1();
            (0x2) : int_set_header_0407_i2();
            (0x3) : int_set_header_0407_i3();
            (0x4) : int_set_header_0407_i4();
            (0x5) : int_set_header_0407_i5();
            (0x6) : int_set_header_0407_i6();
            (0x7) : int_set_header_0407_i7();
            (0x8) : int_set_header_0407_i8();
            (0x9) : int_set_header_0407_i9();
            (0xA) : int_set_header_0407_i10();
            (0xB) : int_set_header_0407_i11();
            (0xC) : int_set_header_0407_i12();
            (0xD) : int_set_header_0407_i13();
            (0xE) : int_set_header_0407_i14();
            (0xF) : int_set_header_0407_i15();
        }
    }

    apply {
        if (meta.bridge.is_transit == 1 && hdr.int_header.isValid()) {
            tb_int_insert.apply();
            tb_int_inst_0003.apply();
            tb_int_inst_0407.apply();

            // Decrement remaining hop cnt
            hdr.int_header.remaining_hop_cnt = hdr.int_header.remaining_hop_cnt - 1;

            // Update headers lengths.
            if (hdr.ipv4.isValid()) {
                hdr.ipv4.len = hdr.ipv4.len + meta.int_meta.new_bytes;
            }
            if (hdr.udp.isValid()) {
                hdr.udp.len = hdr.udp.len + meta.int_meta.new_bytes;
            }
            if (hdr.intl4_shim.isValid()) {
                hdr.intl4_shim.len = hdr.intl4_shim.len + meta.int_meta.new_words;
            }
        }
    }
}

control process_int_sink (
    inout packet_headers_t             hdr,
    inout ingress_metadata_t           meta,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md
) {
    bit<16> temp_int_len;
    @hidden
    action compute_ipv4_len() {
         hdr.ipv4.len = hdr.ipv4.len - temp_int_len;
    }
    @hidden
    action compute_udp_len() {
         hdr.udp.len = hdr.udp.len - temp_int_len;
    }
    @hidden
    action invalidate_int_headers() {
        // remove all the INT information from the packet
        hdr.int_header.setInvalid();
        hdr.int_data.setInvalid();
        hdr.intl4_shim.setInvalid();
        hdr.int_switch_id.setInvalid();
        hdr.int_level1_port_ids.setInvalid();
        hdr.int_hop_latency.setInvalid();
        hdr.int_q_occupancy.setInvalid();
        hdr.int_ingress_tstamp.setInvalid();
        hdr.int_egress_tstamp.setInvalid();
        hdr.int_level2_port_ids.setInvalid();
        hdr.int_egress_tx_util.setInvalid();
    }
    apply {
        if (hdr.bridge.isValid() && hdr.bridge.is_sink == 1) {
            //temp_int_len = ((bit<16>)hdr.intl4_shim.len)*4;
            temp_int_len = (bit<16>)hdr.intl4_shim.len;
            temp_int_len = temp_int_len*4;
            hdr.ipv4.dscp = hdr.intl4_shim.dscp;
            // restore length fields of IPv4 header and UDP header
            compute_ipv4_len();
            if (hdr.udp.isValid()) {
                compute_udp_len();
            }
            invalidate_int_headers();
            meta.compute_checksum_ipv4 = true;
        }
    }
}

/*************************************************************************
 ***********************  I N G R E S S   **************************
 *************************************************************************/
parser IngressParser(packet_in        pkt,
    out packet_headers_t              hdr,
    out ingress_metadata_t            meta,
    out ingress_intrinsic_metadata_t  ig_intr_md)
{
    state start {
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);
        transition init_bridge_and_meta;
    }

    state init_bridge_and_meta {
        hdr.bridge.setValid();
        hdr.bridge.header_type  = HEADER_TYPE_BRIDGE;
        hdr.bridge.header_info  = 0;

        hdr.bridge.is_source = 0;
        hdr.bridge.is_transit = 0;
        hdr.bridge.is_sink = 0;
        hdr.bridge.is_report = 0;
        hdr.bridge.pad1 = 0;
        hdr.bridge.ingress_port = ig_intr_md.ingress_port;
        //hdr.bridge.ingress_port = (bit<16>)ig_intr_md.ingress_port;
        hdr.bridge.ingress_mac_tstamp = (bit<32>)ig_intr_md.ingress_mac_tstamp;

        //transition parse_ethernet;
        transition select(ig_intr_md.ingress_port) {
            CPU_PCIE_PORT_4pipes: parse_packet_out;
            CPU_PCIE_PORT_2pipes: parse_packet_out;
            default: parse_ethernet;
        }
    }

    state parse_packet_out {
        pkt.extract(hdr.packet_out);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan {
        transition parse_vlan_0;
    }

    state parse_vlan_0 {
        pkt.extract(hdr.vlan_list[0]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan_1;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan_1 {
        pkt.extract(hdr.vlan_list[1]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan_2;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan_2 {
        pkt.extract(hdr.vlan_list[2]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : too_many_vlan_tags;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state too_many_vlan_tags {
        transition accept;
    }

    state parse_etherII {
        pkt.extract(hdr.etherII);
        transition select(hdr.etherII.ether_type) {
            ETH_TYPE_IPV4            : parse_ipv4;
            ETH_TYPE_IPV6            : parse_ipv6;
            default                  : accept;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            IP_PROTO_TCP : parse_tcp;
            IP_PROTO_UDP : parse_udp;
            default: accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition select(hdr.ipv4.dscp) {
            DSCP_INT &&& DSCP_MASK: parse_intl4_shim;
            default: accept;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.ipv4.dscp) {
            DSCP_INT &&& DSCP_MASK: parse_intl4_shim;
            default: accept;
        }
    }

    state parse_ipv6 {
        transition accept;
    }

    state parse_intl4_shim {
        pkt.extract(hdr.intl4_shim);
        transition parse_int_header;
    }

    state parse_int_header {
        pkt.extract(hdr.int_header);
        //transition parse_int_data;
        //transition accept;
        transition select(hdr.intl4_shim.len) {
             9: parse_int_data_6;    // 6 + INT_HEADER_LEN_WORD
            15: parse_int_data_12;
            21: parse_int_data_18;
            27: parse_int_data_24;
            33: parse_int_data_30;
            39: parse_int_data_36;
            45: parse_int_data_42;
            51: parse_int_data_48;
            57: parse_int_data_54;
            63: parse_int_data_60;
            default: reject;
        }
    }

    state parse_int_data_6 {
        // Parse INT metadata stack
        //pkt.advance(((bit<32>) (hdr.intl4_shim.len & 0x3F - INT_HEADER_LEN_WORD)) << 5);
        //pkt.advance(192);  // 6*32 (word lenght == 4 bytes == 32bits)
        pkt.extract(hdr.int_data, 192);  // 6*32 (word lenght == 4 bytes == 32bits)
        transition accept;
    }

    state parse_int_data_12 {
        pkt.extract(hdr.int_data, 384);
        transition accept;
    }
    state parse_int_data_18 {
        pkt.extract(hdr.int_data, 576);
        transition accept;
    }
    state parse_int_data_24 {
        pkt.extract(hdr.int_data, 768);
        transition accept;
    }
    state parse_int_data_30 {
        pkt.extract(hdr.int_data, 960);
        transition accept;
    }
    state parse_int_data_36 {
        pkt.extract(hdr.int_data, 1152);
        transition accept;
    }
    state parse_int_data_42 {
        pkt.extract(hdr.int_data, 1344);
        transition accept;
    }
    state parse_int_data_48 {
        pkt.extract(hdr.int_data, 1536);
        transition accept;
    }
    state parse_int_data_54 {
        pkt.extract(hdr.int_data, 1728);
        transition accept;
    }
    state parse_int_data_60 {
        pkt.extract(hdr.int_data, 1920);
        transition accept;
    }

}

    /***************** M A T C H - A C T I O N  *********************/

control Ingress(
    inout packet_headers_t                           hdr,
    inout ingress_metadata_t                         meta,
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md)
{
    apply {
        packetio_ingress.apply(hdr, ig_tm_md);
        process_int_source_transit_sink.apply(hdr, meta, ig_intr_md);
        vlan_control.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md, ig_tm_md);

        process_int_sink.apply(hdr, meta, ig_dprsr_md);
    }
}

    /*********************  D E P A R S E R  ************************/

control IngressDeparser(packet_out pkt,
    inout packet_headers_t                           hdr,
    in    ingress_metadata_t                         meta,
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md)
{
    Checksum() ipv4_checksum;

    apply {
        if (meta.compute_checksum_ipv4) {
            hdr.ipv4.hdr_checksum = ipv4_checksum.update(
                {hdr.ipv4.version,
                 hdr.ipv4.ihl,
                 hdr.ipv4.dscp,
                 hdr.ipv4.ecn,
                 hdr.ipv4.len,
                 hdr.ipv4.identification,
                 hdr.ipv4.flags,
                 hdr.ipv4.frag_offset,
                 hdr.ipv4.ttl,
                 hdr.ipv4.protocol,
                 hdr.ipv4.src_addr,
                 hdr.ipv4.dst_addr});
        }

        pkt.emit(hdr);
    }
}


/*************************************************************************
 *******************************  E G R E S S   **************************
 *************************************************************************/

parser EgressParser(packet_in        pkt,
    out packet_headers_t             hdr,
    out egress_metadata_t            meta,
    out egress_intrinsic_metadata_t  eg_intr_md)
{
    state start {
        meta.egr_mirrored          = false;
        meta.mirror_header_type    = 0;
        meta.mirror_header_info    = 0;
        meta.egr_mirror_session    = 0;
        meta.egress_global_tstamp  = 0;
        meta.ingress_port          = 0;
        meta.egress_port           = 0;
        meta.egress_qid            = 0;
        meta.enq_qdepth            = 0;
        meta.int_meta              = {0, 0, 0, 0};
        meta.compute_checksum_ipv4     = false;

        pkt.extract(eg_intr_md);

        meta.inthdr = pkt.lookahead<inthdr_h>();

        transition select(meta.inthdr.header_type, meta.inthdr.header_info) {
            ( HEADER_TYPE_BRIDGE,         _ ) :
                           parse_bridge;
            ( HEADER_TYPE_MIRROR_EGRESS,  (header_info_t)EGR_PORT_MIRROR ):
                           parse_egr_port_mirror;
            default : reject;
        }
        //transition parse_ethernet;
    }

    state parse_bridge {
        pkt.extract(meta.bridge);
        transition parse_ethernet;
    }

    state parse_egr_port_mirror {
        pkt.extract(meta.egr_port_mirror);
        meta.egr_mirrored   = true;
        transition parse_ethernet;
        //transition accept;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan {
        transition parse_vlan_0;
    }

    state parse_vlan_0 {
        pkt.extract(hdr.vlan_list[0]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan_1;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan_1 {
        pkt.extract(hdr.vlan_list[1]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : parse_vlan_2;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state parse_vlan_2 {
        pkt.extract(hdr.vlan_list[2]);
        transition select(pkt.lookahead<bit<16>>()) {
            ETH_TYPE_VLAN &&& 0xEFFF : too_many_vlan_tags;  // this will matches 0x8100 and 0x9100
            default                  : parse_etherII;
        }
    }

    state too_many_vlan_tags {
        transition accept;
    }

    state parse_etherII {
        pkt.extract(hdr.etherII);
        transition select(hdr.etherII.ether_type) {
            ETH_TYPE_IPV4            : parse_ipv4;
            ETH_TYPE_IPV6            : parse_ipv6;
            default                  : accept;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            IP_PROTO_TCP : parse_tcp;
            IP_PROTO_UDP : parse_udp;
            default: accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition select(hdr.ipv4.dscp) {
            DSCP_INT &&& DSCP_MASK: parse_intl4_shim;
            default: accept;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.ipv4.dscp) {
            DSCP_INT &&& DSCP_MASK: parse_intl4_shim;
            default: accept;
        }
    }

    state parse_ipv6 {
        transition accept;
    }

    state parse_intl4_shim {
        pkt.extract(hdr.intl4_shim);
        transition parse_int_header;
    }

    state parse_int_header {
        pkt.extract(hdr.int_header);
        transition accept;
    }
}

    /***************** M A T C H - A C T I O N  *********************/

control Egress(
    inout packet_headers_t                             hdr,
    inout egress_metadata_t                            meta,
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md)
{
    action int_mirror(MirrorId_t mirror_session) {
        eg_dprsr_md.mirror_type = EGR_PORT_MIRROR;
        meta.mirror_header_type     = HEADER_TYPE_MIRROR_EGRESS;
        meta.mirror_header_info     = (header_info_t)EGR_PORT_MIRROR;
        meta.egr_mirror_session     = mirror_session;
        meta.ingress_port = (bit<16>)meta.bridge.ingress_port;
        meta.egress_port  = (bit<16>)eg_intr_md.egress_port;
        meta.egress_global_tstamp = (bit<32>)eg_prsr_md.global_tstamp;
        meta.enq_qdepth = (bit<24>)eg_intr_md.enq_qdepth;
        meta.egress_qid = (bit<8>)eg_intr_md.egress_qid;
    }

    table tb_int_mirror {
        key = {
            meta.bridge.ingress_port : ternary;
            eg_intr_md.egress_port   : ternary;
        }
        actions = {
            int_mirror; NoAction;
        }
        size = 512;
        default_action = NoAction();
    }


    apply {
        if (meta.bridge.isValid()) {
            process_int_source.apply(hdr, meta, eg_intr_md);
            process_int_transit.apply(hdr, meta, eg_intr_md, eg_prsr_md);
            if (meta.bridge.is_report == 1 && hdr.int_header.isValid()) {
                tb_int_mirror.apply();
            }
        }
        if (meta.egr_port_mirror.isValid()) {
            process_int_report.apply(hdr, meta, eg_intr_md);
        }
    }
}

    /*********************  D E P A R S E R  ************************/

control EgressDeparser(packet_out pkt,
    inout packet_headers_t                          hdr,
    in    egress_metadata_t                         meta,
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md,
    in    egress_intrinsic_metadata_t               eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t   eg_prsr_md)
{
    Checksum() ipv4_checksum;
    Mirror() egr_port_mirror;
    apply {
        if (meta.compute_checksum_ipv4) {
            if (hdr.report_ipv4.isValid()) {
                hdr.report_ipv4.hdr_checksum = ipv4_checksum.update(
                    {hdr.report_ipv4.version,
                     hdr.report_ipv4.ihl,
                     hdr.report_ipv4.dscp,
                     hdr.report_ipv4.ecn,
                     hdr.report_ipv4.len,
                     hdr.report_ipv4.identification,
                     hdr.report_ipv4.flags,
                     hdr.report_ipv4.frag_offset,
                     hdr.report_ipv4.ttl,
                     hdr.report_ipv4.protocol,
                     hdr.report_ipv4.src_addr,
                     hdr.report_ipv4.dst_addr});
            } else {
                hdr.ipv4.hdr_checksum = ipv4_checksum.update(
                    {hdr.ipv4.version,
                     hdr.ipv4.ihl,
                     hdr.ipv4.dscp,
                     hdr.ipv4.ecn,
                     hdr.ipv4.len,
                     hdr.ipv4.identification,
                     hdr.ipv4.flags,
                     hdr.ipv4.frag_offset,
                     hdr.ipv4.ttl,
                     hdr.ipv4.protocol,
                     hdr.ipv4.src_addr,
                     hdr.ipv4.dst_addr});
            }
        }
        if (eg_dprsr_md.mirror_type == EGR_PORT_MIRROR) {
            egr_port_mirror.emit<egr_port_mirror_h>(
                meta.egr_mirror_session,
                {
                    meta.mirror_header_type,
                    meta.mirror_header_info,
                    0,                               // flags
                    0,                               // pad2
                    meta.ingress_port,
                    meta.egress_port,
                    meta.bridge.ingress_mac_tstamp,
                    meta.egress_global_tstamp,
                    meta.enq_qdepth,
                    meta.egress_qid
                    //eg_intr_md.enq_congest_stat
                });
        }
        pkt.emit(hdr);
    }
}


Pipeline(
    IngressParser(),
    Ingress(),
    IngressDeparser(),
    EgressParser(),
    Egress(),
    EgressDeparser()
) pipe;

Switch(pipe) main;

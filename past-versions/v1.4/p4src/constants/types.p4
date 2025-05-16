/* -*- P4_16 -*- */

/**************** V1.4 ****************/

/*************************************************************************
 ************* C O N S T A N T S    A N D   T Y P E S  *******************
**************************************************************************/
typedef bit<48> mac_addr_t;
typedef bit<32> ipv4_addr_t;
typedef bit<128> ipv6_addr_t;

const bit<8> IP_PROTO_ICMP = 1;
const bit<8> IP_PROTO_UDP = 17;
const bit<8> IP_PROTO_TCP = 6;
const bit<16> INT = 0x0601;


enum bit<16> ether_type_t {
    IPV4 = 0x0800,
    ARP  = 0x0806,
    TPID = 0x8100,
    IPV6 = 0x86DD,
    MPLS = 0x8847,
    VLAN = 0x8100,
    QINQ = 0x88A8,
    INT = 0x0601
}


//Mirror constants
typedef bit<8>  pkt_type_t;
const pkt_type_t PKT_TYPE_NORMAL = 1;
const pkt_type_t PKT_TYPE_MIRROR = 2;

typedef bit<3> mirror_type_t; 

const mirror_type_t MIRROR_TYPE_I2E = 1;
const mirror_type_t MIRROR_TYPE_E2E = 2;


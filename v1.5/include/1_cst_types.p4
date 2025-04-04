typedef bit<48> mac_addr_t;
typedef bit<32> ipv4_addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<128> routeid_t;

//================= IP PROTOCOLS =====================
const bit<8> IP_PROTO_ICMP = 1;
const bit<8> IP_PROTO_UDP = 17;
const bit<8> IP_PROTO_TCP = 6;

//================ ETHER TYPES =========================
const bit<16> ETHER_TYPE_IPV4 = 0x0800;
const bit<16> ETHER_TYPE_IPV6 = 0x86DD;
const bit<16> ETHER_TYPE_POLKA = 0x8842;
const bit<16> ETHER_TYPE_ARP = 0x0806;
const bit<16> ETHER_TYPE_INT = 0X0601;
const bit<16> ETHER_TYPE_VLAN = 0x8100;
const bit<16> ETHER_TYPE_QINQ = 0x88A8;

typedef bit <128> polka_route_t;

//================ MIRRORING =========================
//Mirror constants
typedef bit<8>  pkt_type_t;
const pkt_type_t PKT_TYPE_NORMAL = 1;
const pkt_type_t PKT_TYPE_MIRROR = 2;

typedef bit<3> mirror_type_t; 

const mirror_type_t MIRROR_TYPE_I2E = 1;
const mirror_type_t MIRROR_TYPE_E2E = 2;



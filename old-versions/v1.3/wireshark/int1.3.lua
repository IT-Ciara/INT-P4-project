-- Declare the protocols
customINTShim = Proto("customINTShim", "Custom INT Shim Header")
customINT = Proto("customINT", "Custom INT Header")
local ip_proto = Dissector.get("ip")  -- Default IPv4 dissector in Wireshark
local ipv6_proto = Dissector.get("ipv6")  -- Default IPv6 dissector in Wireshark
local vlan_proto = Dissector.get("vlan")  -- Default VLAN dissector in Wireshark


-- Fields for Custom INT Shim
local f_shim_stack_full = ProtoField.uint8("customINTShim.stack_full", "Stack Full", base.DEC, nil, 0x80)
local f_shim_mtu_full = ProtoField.uint8("customINTShim.mtu_full", "MTU Full", base.DEC, nil, 0x40)
local f_shim_reserved = ProtoField.uint8("customINTShim.reserved", "Reserved", base.HEX, nil, 0x3F)
local f_shim_int_count = ProtoField.uint8("customINTShim.int_count", "INT Count", base.DEC)
local f_shim_next_hdr = ProtoField.uint16("customINTShim.next_hdr", "Next Header", base.HEX)

-- Fields for Custom INT
local f_int_data = ProtoField.uint32("customINT.data", "INT Data", base.DEC)

-- Register the fields
customINTShim.fields = {f_shim_stack_full, f_shim_mtu_full, f_shim_reserved, f_shim_int_count, f_shim_next_hdr}
customINT.fields = {f_int_data}

-- Declare globals
int_count = nil
next_hdr = nil
function customINTShim.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = "Custom INT Shim"

    -- Ensure buffer length is sufficient for the shim header
    if buffer:len() < 4 then
        tree:add_expert_info(PI_MALFORMED, PI_ERROR, "Packet too short for INT Shim Header")
        return
    end

    -- Extract fields
    
    local stack_full = buffer(0, 1):bitfield(0, 8)
    local mtu_full = buffer(0, 1):bitfield(0, 8)
    local reserved = buffer(0, 1):bitfield(0,8)
    -- local stack_full = buffer(0, 1):bitfield(6, 1)
    -- local mtu_full = buffer(0, 1):bitfield(7, 1)

    int_count = buffer(1, 1):uint() -- Assign to global variable
    next_hdr = buffer(2, 2):uint()  -- Assign to global variable

    -- Construct the header name with hexadecimal next_hdr
    local header_name = string.format(
        "Custom INT Shim Header. INT Count: %d, Next Header: 0x%04X",
        int_count,
        next_hdr
    )

    -- Parse INT Shim Header
    local shim_tree = tree:add(customINTShim, buffer(0, 4), header_name)

    -- Add fields to the shim tree
    shim_tree:add(f_shim_stack_full, stack_full)
    shim_tree:add(f_shim_mtu_full, mtu_full)
    shim_tree:add(f_shim_reserved, reserved)
    shim_tree:add(f_shim_int_count, int_count)
    shim_tree:add(f_shim_next_hdr, buffer(2, 2)):append_text(
        string.format(" (0x%04X)", next_hdr)
    )

    -- Call the Custom INT dissector for INT headers
    local next_buffer = buffer(4):tvb()
    customINT.dissector(next_buffer, pinfo, tree)
end

-- Custom INT dissector
function customINT.dissector(buffer, pinfo, tree)

    pinfo.cols.protocol = "Custom INT"
    local offset = 0
    local count = int_count -- Use global int_count
    local header_index = 1 -- Start the header numbering from 1

    -- Iterate through all INT headers
    while count > 0 and offset + 4 <= buffer:len() do
        local header_name = "Custom INT Header " .. tostring(count)
        local int_tree = tree:add(customINT, buffer(offset, 4), header_name)
        int_tree:add(f_int_data, buffer(offset, 4))
        offset = offset + 4
        count = count - 1
        header_index = header_index + 1 -- Increment the header number
    end

    -- Process the next protocol
    local next_buffer = buffer(offset):tvb()
    if next_hdr == 0x8100 or next_hdr == 0x88A8 then
        vlan_proto:call(next_buffer, pinfo, tree)
    elseif next_hdr == 0x0800 then
        ip_proto:call(next_buffer, pinfo, tree)
    elseif next_hdr == 0x86DD then
        ipv6_proto:call(next_buffer, pinfo, tree)
    end
end


-- Register the dissectors in the ethertype table
DissectorTable.get("ethertype"):add(0x0601, customINTShim)

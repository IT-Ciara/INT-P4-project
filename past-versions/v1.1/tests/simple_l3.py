################################################################################
# BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
#
# Copyright (c) 2018-2019 Barefoot Networks, Inc.

# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property of
# Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
# technical concepts contained herein are proprietary to Barefoot Networks,
# Inc.
# and its suppliers and may be covered by U.S. and Foreign Patents, patents in
# process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from
# Barefoot Networks, Inc.
#
# No warranty, explicit or implicit is provided, unless granted under a
# written agreement with Barefoot Networks, Inc.
#
#
###############################################################################

"""
Foundational class for PTF tests for a P4 program simple_l3

This module contains the BaseProgramTest class specifically tailored for the
given program. The tailoring is done by defining two methods:
   1) tableSetUp() which creates the lists of tables tests are supposed to
      access along with defining proper field attributes
   2) setUp() that calls the parent's setUp method, while passing tableSetUp
      as an additional argument

All individual tests are subclassed from the this base (BaseProgramTest) or
its subclasses if necessary

The easiest way to write a test for the program is to copy this file as well
as the file p4_program_test.py into the corresponding ptf-tests directory and
then rename this file as <program_name>.py

After that, you can write the files for the individual tests and start them
simply as (replace simple_l3 with your program's name):

from simple_l3 import *
"""

######### STANDARD MODULE IMPORTS ########
import logging
import grpc
import pdb

import struct

######### PTF modules for BFRuntime Client Library APIs #######
import ptf
from ptf.testutils import *
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc

from p4_program_test import P4ProgramTest

########## Program-specific Initialization ############
class BaseProgramTest(P4ProgramTest):
    def setUp(self):
        P4ProgramTest.setUp(self, self.tableSetUp)

    def tableSetUp(self):
        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations
        # ready
        self.ipv4_host = self.bfrt_info.table_get("Ingress.ipv4_host")
        self.ipv4_host.info.key_field_annotation_add(
            "hdr.ipv4.dst_addr", "ipv4")

        self.ipv4_lpm = self.bfrt_info.table_get("Ingress.ipv4_lpm")
        self.ipv4_lpm.info.key_field_annotation_add(
            "hdr.ipv4.dst_addr", "ipv4")

        self.tables = [ self.ipv4_host, self.ipv4_lpm ]

#
# Individual tests can now be subclassed from BaseProgramTest
#

#!/usr/bin/env python
# Copyright 2010 Google Inc. All Rights Reserved.
"""A module to load all vfs handler plugins."""


# pylint: disable=W0611
import platform

# These import populate the VFSHandler registry
from grr.client.vfs_handlers import files
from grr.client.vfs_handlers import memory
from grr.client.vfs_handlers import sleuthkit

# pylint: disable=C6204
if platform.system() == "Windows":
  from grr.client.vfs_handlers import registry

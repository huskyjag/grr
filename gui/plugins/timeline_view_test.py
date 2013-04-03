#!/usr/bin/env python
# -*- mode: python; encoding: utf-8 -*-

# Copyright 2011 Google Inc. All Rights Reserved.
"""Tests for the Timeline viewer flow."""



from grr.client import vfs

from grr.lib import access_control
from grr.lib import aff4
from grr.lib import config_lib
from grr.lib import rdfvalue
from grr.lib import test_lib


class TestTimelineView(test_lib.GRRSeleniumTest):
  """Test the timeline view."""

  @staticmethod
  def CreateTimelineFixture():
    """Creates a new timeline fixture we can play with."""
    # Create a client for testing
    client_id = "C.0000000000000001"

    token = access_control.ACLToken("test", "fixture")

    fd = aff4.FACTORY.Create(client_id, "VFSGRRClient", token=token)
    fd.Set(fd.Schema.CERT(config_lib.CONFIG["Client.certificate"]))
    fd.Close()

    # Install the mock
    vfs.VFS_HANDLERS[
        rdfvalue.RDFPathSpec.Enum("OS")] = test_lib.ClientVFSHandlerFixture
    client_mock = test_lib.ActionMock("ListDirectory")
    output_path = "analysis/Timeline/MAC"

    for _ in test_lib.TestFlowHelper(
        "RecursiveListDirectory", client_mock, client_id=client_id,
        pathspec=rdfvalue.RDFPathSpec(
            path="/", pathtype=rdfvalue.RDFPathSpec.Enum("OS")),
        token=token):
      pass

    # Now make a timeline
    for _ in test_lib.TestFlowHelper(
        "MACTimes", client_mock, client_id=client_id, token=token,
        path="aff4:/%s/" % client_id, output=output_path):
      pass

  def setUp(self):
    test_lib.GRRSeleniumTest.setUp(self)

    # Create a new collection
    self.CreateTimelineFixture()

  def testTimelineViewer(self):
    # Open the main page
    self.Open("/")

    self.WaitUntil(self.IsElementPresent, "client_query")
    self.Type("client_query", "0001")
    self.Click("client_query_submit")

    self.WaitUntilEqual(u"C.0000000000000001",
                        self.GetText, "css=span[type=subject]")

    # Choose client 1
    self.Click("css=td:contains('0001')")

    # Go to Browse VFS
    self.WaitUntil(self.IsElementPresent,
                   "css=a:contains('Browse Virtual Filesystem')")
    self.Click("css=a:contains('Browse Virtual Filesystem')")

    # Navigate to the analysis directory
    self.WaitUntil(self.IsElementPresent, "css=#_analysis")
    self.Click("css=#_analysis ins.jstree-icon")

    self.WaitUntil(self.IsElementPresent, "link=Timeline")
    self.Click("link=Timeline")

    self.WaitUntil(self.IsElementPresent,
                   "css=span[type=subject]:contains(\"MAC\")")
    self.Click("css=span[type=subject]:contains(\"MAC\")")

    self.WaitUntil(self.IsElementPresent, "css=td:contains(\"TIMELINE\")")
    self.assert_("View details" in self.GetText("css=td div.default_view a"))

    self.Click("css=a:contains(\"View details\")")

    self.WaitUntil(self.IsElementPresent, "container_query")

    self.Type("css=input#container_query",
              "subject contains bash and timestamp > 2010")

    # Use the hidden submit button to issue the query. Ordinarily users have to
    # press enter here as they do not see the submit button. But pressing enter
    # does not work with chrome.
    self.Click("css=#toolbar_main form[name=query_form] button[type=submit]")

    self.WaitUntilContains("2011-03-07 12:50:20",
                           self.GetText, "css=tbody tr:first")

    self.Click("css=tbody tr:first td")

    self.WaitUntilContains("2011-03-07 12:50:20", self.GetText,
                           "css=.tab-content h3")

    # Check that the embedded stat proto is properly presented
    self.assertTrue("2011-03-07 12:50:20" in self.GetText(
        "css=td.proto_value tr:contains(st_atime) td.proto_value"))

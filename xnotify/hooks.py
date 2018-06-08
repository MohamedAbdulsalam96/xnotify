# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "xnotify"
app_title = "XNotify"
app_publisher = "XLevel Retail Systems Nigeria Ltd"
app_description = "Send notifications "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "olamide@xlevelretail.com"
app_license = "MIT"

doc_events = {
	"Sales Invoice": {
		"on_submit": "xnotify.utils.notify",
	}
}

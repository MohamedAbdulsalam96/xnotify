import frappe
import six
from frappe.utils import cstr


def get_single(name):
	"""
	wrapper over `frappe.get_single`. It tries to handle the exception thrown
	if `frappe.get_single` fails

	:param name: Doctype name
	"""
	try:
		return frappe.get_single(name)
	except ImportError as e:
		frappe.throw(frappe._('Could not find {0}'.format(name)), ImportError)


def doc_is_pos(doc):
	"""
	Checks if the Sales Invoice doctype object - `doc` was generated from the
	POS.

	>>> doc_is_pos(frappe._dict(is_pos=1))
	True

	>>> doc_is_pos(frappe._dict(is_pos=0))
	False

	:param doc: `Document` - Sales Invoice doctype object
	:return: bool
	"""
	return bool(doc.get('is_pos'))


def send_sms(sms_center):
	sms_center.send_sms()


def parse_message(message, doc):
	"""
	In XNotify settings, you are allowed to add placeholders for the
	invoice's grand total and the invoice number. This function allows you to
	'compile' the message and returns a new string with the placeholders
	replaced with actual information from the Sales Invoice doctype object - `doc`

	>>> parse_message('Nothing is changed here', frappe._dict(name='SINV-1234', grand_total='1000'))
	u'Nothing is changed here'

	>>> parse_message('', frappe._dict(name='SINV-1234', grand_total='1000'))
	u''

	>>> parse_message('|xna|', frappe._dict(name='SINV-1234', grand_total='1000'))
	u'1000'

	>>> parse_message('Amount is |xna|', frappe._dict(name='SINV-1234', grand_total='1000'))
	u'Amount is 1000'

	>>> parse_message('Amount is |xna|, number is |xnn|', frappe._dict(name='SINV-1234', grand_total='1000'))
	u'Amount is 1000, number is SINV-1234'

	>>> parse_message('|xnn|, |xna|', frappe._dict(name='SINV-1234', grand_total='1000'))
	u'SINV-1234, 1000'

	>>> parse_message('|xnc|', frappe._dict(customer='Abel'))
	u'Abel'

	:param message: String - message to be sent in SMS
	:param doc: Sales Invoice `Document`
	"""
	msg = cstr(message)
	return msg.replace('|xna|', cstr(doc.grand_total))\
		.replace('|xnn|', cstr(doc.name))\
		.replace('|xnc|', cstr(doc.customer))


@frappe.whitelist()
def notify(doc, *args):
	"""
	Send an sms to a customer with the mobile phone number stored on the saved
	in the Sales Invoice. `notify` depends on `SMS Center` and `SMS Settings`.
	Both must be configured

	:param doc: Document - Sales Invoice doctype
	:param args: Any other argument from the hook
	"""
	if(isinstance(doc, six.string_types)):
		import json
		doc_ = json.loads(doc)
		doc = frappe._dict(**doc_)

	notify_settings = get_single('XNotify Settings')

	can_send_sms = notify_settings.send_sms and \
				(doc_is_pos(doc) == bool(notify_settings.send_for_pos))

	if can_send_sms:
		sms_center = get_single('SMS Center')
		sms_center.receiver_list = cstr(doc.contact_mobile)
		sms_center.message = parse_message(notify_settings.message, doc)

		frappe.enqueue(send_sms, sms_center=sms_center)


if __name__ == "__main__":
	import doctest
	doctest.testmod()

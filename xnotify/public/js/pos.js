// Licence: MIT

function submittedInvoice(pos) {
	const doc = {};
	const si_doc = pos.si_docs[pos.si_docs.length - 1];
	const serial_number = Object.keys(si_doc)[0]

	doc.contact_mobile = pos.contacts[si_doc[serial_number].customer].mobile_no;
	doc.grand_total = si_doc[serial_number].grand_total;
	doc.name = serial_number;
	doc.is_pos = 1;
	return doc;
}

function isPosPage() {
	return window.location.toString().includes('#pos');
}

function hijackOfflinePOS() {
	const pos = isPosPage() ? window.cur_pos : undefined;

	if (pos) {
		pos._submit_invoice = pos.submit_invoice;

		pos.submit_invoice = function notify() {
			pos._submit_invoice();
			const doc = submittedInvoice(pos);
			frappe.call({
				method: 'xnotify.utils.notify',
				args: {doc: doc},
				callback: function(r){}
			});
		}

		window.xnotify = 1;
	}

	if (isPosPage() && !pos) {
		// page was too slow to load.
		window.frappe.show_alert('POS did not load properly. Please reload the page for full functionality.');
	}
}

// delay to ensure DOM is settled and ensure `cur_pos` is not WIP
let timeoutId;

window.onload = () => {
	timeoutId = setTimeout(function() {
		if (!window.xnotify) {
			hijackOfflinePOS();
		}
	}, 5000);
};

window.onhashchange = () => {
	timeoutId = setTimeout(function() {
		if (!window.xnotify) {
			hijackOfflinePOS();
		}
	}, 5000);
};

window.onbeforeunload = function(id) {
	clearTimeout(timeoutId);
};

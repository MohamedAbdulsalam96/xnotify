// Licence: MIT

function getPhoneNumber(contacts, si, serialNumber) {
	const contact = contacts[si[serialNumber].customer];

	if (contact.phone) {
		console.log(contact.phone);
		return contact.phone;
	}

	if (contact.mobile_no) {
		console.log(contact.mobile_no);
		return contact.mobile_no;
	}
}

function getSubmittedInvoice(pos) {
	// the snake case variables as those are what the backend is expecting
	const doc = {};
	const si_doc = pos.si_docs[pos.si_docs.length - 1];
	const serialNumber = Object.keys(si_doc)[0];

	doc.contact_mobile = getPhoneNumber(pos.address, si_doc, serialNumber)
	doc.grand_total = si_doc[serialNumber].grand_total;
	doc.name = serialNumber;
	doc.is_pos = 1;
	return doc;
}

function isPosPage() {
	return window.location.toString().includes('#pos');
}

function injectXnotifyIntoPos() {
	const pos = isPosPage() ? window.cur_pos : undefined;

	if (pos) {
		pos._submit_invoice = pos.submit_invoice;

		pos.submit_invoice = function notify() {
			pos._submit_invoice();
			const doc = getSubmittedInvoice(pos);
			frappe.call({
				method: 'xnotify.utils.notify',
				args: {doc: doc},
				callback: () => {}
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
			injectXnotifyIntoPos();
		}
	}, 6000);
};

window.onhashchange = () => {
	timeoutId = setTimeout(function() {
		if (!window.xnotify) {
			injectXnotifyIntoPos();
		}
	}, 6000);
};

window.onbeforeunload = function(id) {
	clearTimeout(timeoutId);
};

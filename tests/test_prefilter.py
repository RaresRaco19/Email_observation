"""Rule-based none labels: each rule on its own, and its effect on prepare."""
import unittest

from observer import config, labels, prepare
from observer.prefilter import none_reason
from observer.util import read_json, write_json
from tests.helpers import TempCorpus, message


def meta(frm="a@enron.com", to=("b@enron.com",), cc=(), subject="Meter 1517"):
    return {"from": frm, "to": list(to), "cc": list(cc), "subject": subject}


class RuleTest(unittest.TestCase):
    def test_work_mail_is_left_to_the_labeler(self):
        self.assertIsNone(none_reason(meta()))
        self.assertIsNone(none_reason(meta(to=("mark.austin@us.andersen.com",))))  # external business recipient
        self.assertIsNone(none_reason(meta(to=(), subject="")))

    def test_broadcast_sender(self):
        self.assertEqual(none_reason(meta(frm="no.address@enron.com")), "broadcast_sender")
        self.assertEqual(none_reason(meta(frm="announcements.enron@enron.com")), "broadcast_sender")

    def test_personal_sender_including_subdomains(self):
        self.assertEqual(none_reason(meta(frm="dmoore21@charter.net")), "personal_sender")
        self.assertEqual(none_reason(meta(frm="x@mail.aol.com")), "personal_sender")
        self.assertIsNone(none_reason(meta(frm="x@notaol.com")))

    def test_personal_recipients_need_all_recipients(self):
        self.assertEqual(none_reason(meta(to=("kristi.giron@cfisd.net", "x@yahoo.com"))), "personal_recipients")
        self.assertIsNone(none_reason(meta(to=("kristi.giron@cfisd.net",), cc=("b@enron.com",))))

    def test_social_subject_but_not_third_party(self):
        self.assertEqual(none_reason(meta(subject="Golf on Friday")), "social_subject")
        self.assertEqual(none_reason(meta(subject="RE: Pre-Party??")), "social_subject")
        self.assertIsNone(none_reason(meta(subject="3rd Party Maintenance at Meter 6040")))
        self.assertIsNone(none_reason(meta(subject="Third party nominations")))


class PrepareTest(unittest.TestCase):
    def setUp(self):
        self.c = TempCorpus()
        self.c.add("m/inbox/1", message(msg_id="<1@x>"))
        self.c.add("m/inbox/2", message(msg_id="<2@x>", frm="pal@hotmail.com", subject="Weekend",
                                        body="Are we still on for the weekend at the lake house?"))

    def tearDown(self):
        self.c.cleanup()

    def test_ruled_message_is_not_batched_and_ends_up_valid_none(self):
        p = self.c.paths
        s = prepare.run(p, expected_files=None)
        self.assertEqual((s["messages_to_label"], s["messages_ruled_none"]), (1, {"personal_sender": 1}))
        batch = read_json(p.root / s["pending_batches"][0]["path"])
        self.assertEqual([m["msg_id"] for m in batch["messages"]], ["m/inbox/1"])
        labels.check_labels(p)
        status = {m["msg_id"]: (m["status"], m.get("label"), m.get("batch_id"))
                  for m in read_json(p.work / "messages.json")["messages"]}
        self.assertEqual(status["m/inbox/2"], ("valid", {"process": "none"}, "rule:v1:personal_sender"))
        again = prepare.run(p, expected_files=None)  # cached: not re-ruled, not re-batched
        self.assertEqual((again["messages_cached"], again["messages_to_label"]), (1, 1))

    def test_version_bump_reevaluates_ruled_messages(self):
        p = self.c.paths
        prepare.run(p, expected_files=None)
        store = read_json(p.work / "label_store.json")
        old = config.PREFILTER_VERSION
        config.PREFILTER_VERSION = old + 1
        try:
            s = prepare.run(p, expected_files=None)
        finally:
            config.PREFILTER_VERSION = old
        new_store = read_json(p.work / "label_store.json")
        self.assertEqual(s["messages_ruled_none"], {"personal_sender": 1})
        self.assertNotEqual(store, new_store)
        self.assertTrue(all(e["batch_id"].startswith(f"rule:v{old + 1}:") for e in new_store["labels"].values()))


if __name__ == "__main__":
    unittest.main()

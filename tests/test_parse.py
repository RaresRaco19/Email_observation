import unittest

from observer.config import Paths
from observer.parse import parse_file, split_new_text
from observer.prepare import corpus_files, dedup
from tests.helpers import REPO, TempCorpus, message

REAL = Paths(REPO)


class RealCorpusTest(unittest.TestCase):
    def test_reads_every_file(self):
        self.assertEqual(len(corpus_files(REAL)), 3240)

    def test_missing_date_is_none(self):
        m = parse_file(REAL.corpus / "giron-d/sent/795.", REAL.corpus)
        self.assertIsNone(m["date"])
        self.assertEqual(m["msg_id"], "giron-d/sent/795")

    def test_embedded_headers_ignored(self):
        # these files carry an empty "Message-ID:" inside an embedded message; only the top block counts
        msgs = [parse_file(REAL.corpus / f"giron-d/sent/{n}.", REAL.corpus) for n in (501, 670)]
        self.assertTrue(all(m["message_id_header"].startswith("<") for m in msgs))
        self.assertEqual(len(dedup(msgs)), 2)

    def test_empty_message_ids_do_not_merge(self):
        c = TempCorpus()
        try:
            c.add("a/inbox/1", message(msg_id="", body="first unrelated message body text"))
            c.add("a/inbox/2", message(msg_id="", body="second unrelated message body text"))
            msgs = [parse_file(c.paths.corpus / f"a/inbox/{n}.", c.paths.corpus) for n in (1, 2)]
            self.assertEqual(len(dedup(msgs)), 2)
        finally:
            c.cleanup()

    def test_future_date_is_undated(self):
        m = parse_file(REAL.corpus / "lokay-m/inbox/74.", REAL.corpus)  # Date: ... 2031
        self.assertIsNone(m["date"])
        self.assertTrue(m["date_out_of_range"])

    def test_huge_file_truncated(self):
        m = parse_file(REAL.corpus / "farmer-d/logistics/3221.", REAL.corpus)
        self.assertTrue(m["truncated"])
        self.assertLessEqual(len(m["new_text"]), 8000)

    def test_timezone_shifted_export_copy_merges(self):
        msgs = [parse_file(REAL.corpus / f"farmer-d/logistics/{n}.", REAL.corpus) for n in (189, 2154)]
        self.assertEqual(len(dedup(msgs)), 1)

    def test_daily_repeats_stay_separate(self):
        msgs = [parse_file(REAL.corpus / f"farmer-d/logistics/{n}.", REAL.corpus) for n in (1310, 1312)]
        self.assertEqual(len(dedup(msgs)), 2)


class SplitTest(unittest.TestCase):
    def test_outlook_original_message(self):
        new, src = split_new_text("Confirmed, same volumes as yesterday.\n\n -----Original Message-----\nFrom: x\nold text")
        self.assertEqual((new, src), ("Confirmed, same volumes as yesterday.", "new"))

    def test_lotus_forward(self):
        body = "Can you look at this before close?\n\n---------------------- Forwarded by Darron C Giron/HOU/ECT on 04/26/2001 \n03:38 PM ---------------------------\nold"
        self.assertEqual(split_new_text(body)[0], "Can you look at this before close?")

    def test_lotus_reply_header(self):
        body = "Fixed the path on deal 93804 today.\n\n\nTricia Truong\n03/20/2001 11:21 AM\nTo: Darron C Giron/HOU/ECT@ECT\ncc:\nold"
        self.assertEqual(split_new_text(body)[0], "Fixed the path on deal 93804 today.")

    def test_pure_forward_falls_back_to_body(self):
        body = "\n---------------------- Forwarded by A on 01/01/2001 09:00 AM ----------\nThe real content of the notice is here."
        new, src = split_new_text(body)
        self.assertEqual(src, "body")
        self.assertIn("real content", new)


class DedupSyntheticTest(unittest.TestCase):
    def setUp(self):
        self.c = TempCorpus()

    def tearDown(self):
        self.c.cleanup()

    def parse(self, rel):
        return parse_file(self.c.paths.corpus / (rel + "."), self.c.paths.corpus)

    def test_same_message_id_merges_lowest_path_wins(self):
        self.c.add("a/inbox/2", message(msg_id="<same@x>"))
        self.c.add("a/inbox/10", message(msg_id="<same@x>", body="different wrapping\nof the same message text"), crlf=True)
        out = dedup([self.parse("a/inbox/2"), self.parse("a/inbox/10")])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["msg_id"], "a/inbox/10")  # lexicographic order: "10" < "2"
        self.assertEqual(out[0]["dup_paths"], ["a/inbox/2"])


if __name__ == "__main__":
    unittest.main()

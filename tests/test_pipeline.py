"""Stages 2-5 on a synthetic corpus, with hand-written 'model output' standing in for the subagents."""
import json
import unittest

from observer import artifacts, config, labels, prepare, rank, solutions
from observer.util import read_json, write_json
from observer.validate import quote_error
from tests.helpers import TempCorpus, message

BODY = ("Daren - there was flow of 14 mmbtus on Mar. 1 at meter {n}. We have no deal at the meter\n"
        "until Mar. 14. Could you either set up a new deal or extend the deal from Feb.? Allocations close today.")
QUOTE = "We have no deal at the meter until Mar. 14."


class QuoteTest(unittest.TestCase):
    def setUp(self):
        self.c = TempCorpus()
        self.c.add("m/inbox/1", message(body=BODY.format(n=1517)), crlf=True)

    def tearDown(self):
        self.c.cleanup()

    def test_wrapped_crlf_quote_matches(self):
        self.assertIsNone(quote_error(QUOTE, "m/inbox/1", self.c.paths.corpus))

    def test_paraphrase_rejected(self):
        self.assertIsNotNone(quote_error("There was no deal at the meter until March 14.", "m/inbox/1", self.c.paths.corpus))

    def test_ellipsis_and_short_rejected(self):
        self.assertIsNotNone(quote_error("We have no deal ... until Mar. 14.", "m/inbox/1", self.c.paths.corpus))
        self.assertIsNotNone(quote_error("no deal", "m/inbox/1", self.c.paths.corpus))


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.c = TempCorpus()
        p = self.c.paths
        # 9 meter requests (9 threads) spread over Mar 1 - Apr 30 + 1 lunch note
        for i, day in enumerate([1, 8, 15, 22, 29, 36, 43, 50, 61]):
            month, d = (3 + (day - 1) // 31), ((day - 1) % 31) + 1
            d = min(d, 30)
            self.c.add(f"m/inbox/{i}", message(msg_id=f"<{i}@x>", date=f"Thu, {d} {['Mar','Apr','May'][month-3]} 2001 09:00:00 -0000",
                                               subject=f"Meter {1500 + i}", body=BODY.format(n=1500 + i)))
        self.c.add("m/inbox/9", message(msg_id="<9@x>", subject="Lunch", body="Lunch at noon on Friday with everyone from the desk?"))
        self.summary = prepare.run(p, expected_files=None)
        self.batch = self.summary["pending_batches"][0]
        self.payload = read_json(p.root / self.batch["path"])["messages"]

    def tearDown(self):
        self.c.cleanup()

    def write_labels(self, labels_list):
        write_json(self.c.paths.root / self.batch["output"], {"batch_id": self.batch["id"], "labels": labels_list})

    def write_delta(self, label="meter_deal_fix", pid="meter_fix", remedy="automation"):
        write_json(self.c.paths.work / "process_map_delta.json", {"new_processes": [{"id": pid, "name": "Meter deal fixes",
                   "description": "d", "remedy": remedy, "action_idea": "a"}], "map": {label: pid}})

    def good_labels(self):
        out = []
        for m in self.payload:
            if m["subject"] == "Lunch":
                out.append({"msg_id": m["msg_id"], "process": "none"})
            else:
                out.append({"msg_id": m["msg_id"], "process": "meter_deal_fix", "process_description": "Fix meters without deals",
                            "kind": "request", "manual_steps": "create or extend deal", "minutes_estimate": 20,
                            "stall_signal": "Allocations close today", "quote": QUOTE})
        return out

    def test_coverage_miss_retries_then_fails(self):
        p = self.c.paths
        self.write_labels(self.good_labels()[:-1])
        s = labels.check_labels(p)
        self.assertEqual(len(s["retry_batches"]), 1)
        self.assertIn("no label", s["retry_batches"][0]["errors"][0])
        self.assertEqual(labels.check_labels(p)["retry_batches"][0]["id"], self.batch["id"])  # idempotent re-check
        self.write_labels(self.good_labels()[:-2])  # second, different failing attempt
        s = labels.check_labels(p)
        self.assertEqual((len(s["retry_batches"]), len(s["failed_batches"])), (0, 1))

    def test_bad_quotes_fail_batch_and_are_dropped(self):
        labs = self.good_labels()
        for lab in labs[:3]:
            if lab["process"] != "none":
                lab["quote"] = "This sentence does not appear anywhere in the email."
        self.write_labels(labs)
        s = labels.check_labels(self.c.paths)
        self.assertEqual(len(s["retry_batches"]), 1)
        self.assertTrue(any("failed verbatim check" in e for e in s["retry_batches"][0]["errors"]))
        self.assertEqual(s["labels_valid"], 0)  # a batch awaiting its retry contributes nothing yet

    def test_rejected_quote_is_listed_in_report(self):
        p = self.c.paths
        labs = self.good_labels()
        bad = next(lab for lab in labs if lab["process"] != "none")
        bad["quote"] = "This sentence does not appear anywhere in the email."
        self.write_labels(labs)
        s = labels.check_labels(p)
        self.assertEqual((s["ok"], s["quotes_rejected"], s["labels_valid"]), (1, 1, 9))
        status = {m["msg_id"]: m["status"] for m in read_json(p.work / "messages.json")["messages"]}
        self.assertEqual(status[bad["msg_id"]], "rejected")
        labels.candidates(p)
        self.write_delta()
        labels.check_process_map(p)
        rank.build(p)
        g = read_json(p.out / "report.json")["generated_from"]
        self.assertEqual([x["msg_id"] for x in g["rejected_quotes"]], [bad["msg_id"]])

    def test_rank_refuses_view_from_older_prepare(self):
        p = self.c.paths
        self.run_through_rank()
        prepare.run(p, expected_files=None)  # rewrites messages.json without label status
        with self.assertRaisesRegex(SystemExit, "run check-labels"):
            rank.build(p)
        labels.check_labels(p)
        self.assertEqual(rank.build(p)["opportunities"][0]["messages"], 9)

    def run_through_rank(self, top_n=None, remedy="automation"):
        p = self.c.paths
        self.write_labels(self.good_labels())
        self.assertEqual(labels.check_labels(p)["ok"], 1)
        self.assertTrue(labels.candidates(p)["needs_consolidation"])
        self.write_delta(remedy=remedy)
        self.assertTrue(labels.check_process_map(p)["ok"])
        self.assertFalse(labels.candidates(p)["needs_consolidation"])
        old = config.TOP_N
        if top_n is not None:
            config.TOP_N = top_n
        try:
            return rank.build(p)
        finally:
            config.TOP_N = old

    def test_rank_arithmetic(self):
        s = self.run_through_rank()
        o = read_json(self.c.paths.out / "report.json")["opportunities"][0]
        self.assertEqual(o["messages"], 9)
        # mailbox m observed Mar 1 -> Apr 30 = 60 days = 1.971 months; 9/1.971 = 4.566/month x 20 min x 0.6 x $85 = $78
        expected = 9 / (60 / 30.44) * 20 / 60 * 0.6 * 85
        self.assertEqual(o["usd_month"], round(expected))
        self.assertEqual(s["total_usd_month"], round(expected))
        self.assertEqual([t["id"] for t in s["artifact_targets"]], ["meter_fix"])  # inside the top N

    def test_process_map_must_cover_candidates(self):
        p = self.c.paths
        self.write_labels(self.good_labels())
        labels.check_labels(p)
        labels.candidates(p)
        write_json(p.work / "process_map_delta.json", {"new_processes": [], "map": {}})
        r = labels.check_process_map(p)
        self.assertFalse(r["ok"])
        self.assertTrue(any("unmapped" in e for e in r["errors"]))

    def test_min_evidence_rejects(self):
        p = self.c.paths
        labs = [lab if i < 2 or lab["process"] == "none" else {"msg_id": lab["msg_id"], "process": "none"}
                for i, lab in enumerate(self.good_labels())]
        self.write_labels(labs)
        labels.check_labels(p)
        labels.candidates(p)
        self.write_delta()
        labels.check_process_map(p)
        rank.build(p)
        r = read_json(p.out / "report.json")
        self.assertEqual(r["opportunities"], [])
        self.assertEqual(r["rejected"][0]["id"], "meter_fix")

    def test_artifact_checks(self):
        s = self.run_through_rank()
        t = s["artifact_targets"][0]
        p = self.c.paths
        ev = read_json(p.root / t["evidence_path"])
        cite = ev["messages"][0]["msg_id"]
        good = (f"---\nopportunity: meter_fix\ntype: sop\ncitations: [{cite}]\n---\n# Checklist\n"
                f"- Check meters with flow and no deal [{cite}]\n\n> {QUOTE}\n\nSaves {ev['allowed_figures'][0]}/month.\n")
        out = p.root / t["output_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(good)
        self.assertEqual(artifacts.artifact_errors(p, "meter_fix"), [])
        out.write_text(good.replace(f"[{cite}]\n\n>", "[m/inbox/99]\n\n>").replace("/month.", "/month, or $9,999 a year."))
        errs = artifacts.artifact_errors(p, "meter_fix")
        self.assertTrue(any("m/inbox/99" in e for e in errs))
        self.assertTrue(any("$9,999" in e for e in errs))
        out.write_text(good.replace(QUOTE, "There was no deal at that meter until the fourteenth of March."))
        self.assertTrue(any("not verbatim" in e for e in artifacts.artifact_errors(p, "meter_fix")))

    def test_prepare_is_incremental(self):
        p = self.c.paths
        self.write_labels(self.good_labels())
        again = prepare.run(p, expected_files=None)
        self.assertEqual(again["pending_batches"], [])
        self.assertEqual((again["messages_cached"], again["messages_to_label"]), (10, 0))

    def test_new_file_queues_only_itself_and_extends_map(self):
        p = self.c.paths
        self.run_through_rank()
        self.c.add("m/inbox/20", message(msg_id="<20@x>", date="Thu, 3 May 2001 09:00:00 -0000",
                                         subject="RE: Meter 1500", body="Gas desk: please extend the deal at meter 1500."))
        s = prepare.run(p, expected_files=None)
        self.assertEqual((s["files"], s["messages_cached"], s["messages_to_label"]), (11, 10, 1))
        batch = read_json(p.root / s["pending_batches"][0]["path"])
        self.assertEqual([m["msg_id"] for m in batch["messages"]], ["m/inbox/20"])
        self.assertEqual([c["process"] for c in batch["context"]], ["meter_deal_fix"])  # earlier thread message
        write_json(p.root / s["pending_batches"][0]["output"], {"batch_id": batch["batch_id"], "labels": [
            {"msg_id": "m/inbox/20", "process": "deal_extension", "process_description": "Extend deals",
             "kind": "request", "manual_steps": "extend", "minutes_estimate": 20, "stall_signal": "",
             "quote": "please extend the deal at meter 1500."}]})
        cl = labels.check_labels(p)
        self.assertEqual((cl["messages_labeled"], cl["labels_process"]), (11, 10))  # old labels kept from the store
        c = labels.candidates(p)
        self.assertEqual((c["candidates"], c["already_mapped"]), (1, 1))
        cands = read_json(p.work / "candidates.json")
        self.assertEqual([e["id"] for e in cands["existing_processes"]], ["meter_fix"])
        # the consolidator may not redefine existing ids, only map new labels onto them
        write_json(p.work / "process_map_delta.json", {"new_processes": [{"id": "meter_fix", "name": "x",
                   "description": "d", "remedy": "automation", "action_idea": "a"}], "map": {"deal_extension": "meter_fix"}})
        self.assertFalse(labels.check_process_map(p)["ok"])
        write_json(p.work / "process_map_delta.json", {"new_processes": [], "map": {"deal_extension": "meter_fix"}})
        self.assertTrue(labels.check_process_map(p)["ok"])
        pm = read_json(p.work / "process_map.json")
        self.assertEqual(pm["map"], {"meter_deal_fix": "meter_fix", "deal_extension": "meter_fix"})
        self.assertEqual(rank.build(p)["opportunities"][0]["messages"], 10)

    def test_failed_batch_messages_are_not_requeued(self):
        p = self.c.paths
        self.write_labels(self.good_labels()[:-1])
        labels.check_labels(p)
        self.write_labels(self.good_labels()[:-2])
        self.assertEqual(len(labels.check_labels(p)["failed_batches"]), 1)
        s = prepare.run(p, expected_files=None)
        self.assertEqual(s["messages_to_label"], 0)
        self.assertEqual(labels.check_labels(p)["messages_failed"], 2)

    def test_thread_gate_rejects_one_conversation(self):
        p = self.c.paths
        old = config.MIN_THREADS
        config.MIN_THREADS = 10  # the fixture has 9 threads
        try:
            self.run_through_rank()
        finally:
            config.MIN_THREADS = old
        r = read_json(p.out / "report.json")
        self.assertEqual(r["opportunities"], [])
        self.assertIn("distinct threads", r["rejected"][0]["reason"])

    def test_observed_window_is_union_of_mailbox_windows(self):
        from datetime import datetime
        d = lambda s: datetime.fromisoformat(s)
        w = {"a": (d("2001-01-01"), d("2001-03-02")), "b": (d("2001-02-01"), d("2001-04-01")), "c": (d("2001-06-01"), d("2001-06-11"))}
        self.assertEqual(rank.observed_days(["a", "b"], w), 90)  # overlap counted once
        self.assertEqual(rank.observed_days(["a", "c"], w), 70)  # gap between windows not counted

    def write_design(self, **changes):
        p = self.c.paths
        ev = read_json(p.evidence / "meter_fix.json")
        cite = ev["messages"][0]["msg_id"]
        d = {"opportunity": "meter_fix", "summary": "Meters flow without deals; a nightly check would catch them.",
             "current_workflow": [{"step": s, "who": "scheduler", "citations": [cite]} for s in ("spot flow", "ask desk", "extend deal")],
             "stall_points": [{"description": "waits on the desk", "quote": QUOTE, "citation": cite}],
             "solution": {"approach": "Compare flow to deals nightly.", "trigger": "nightly", "inputs": ["flow"],
                          "outputs": ["exception list"], "systems": ["Allocations"], "components": ["comparison job"]},
             "implementation_steps": ["build", "pilot"], "stays_manual": ["pricing"], "risks": ["late data"],
             "effort": "S", "success_metric": f"meters without deals; saves {ev['allowed_figures'][0]}/month"}
        for k, v in changes.items():
            target = d["solution"] if k in d["solution"] else d
            target[k] = v
        write_json(p.work / "solutions" / "meter_fix.json", d)

    def test_solution_design_checks(self):
        s = self.run_through_rank()
        p = self.c.paths
        self.assertEqual([t["id"] for t in s["solution_targets"]], ["meter_fix"])
        self.assertFalse(s["solution_targets"][0]["done"])
        self.write_design()
        self.assertEqual(solutions.design_errors(p, "meter_fix"), [])
        bad = {"systems": ["SAP"], "effort": "XL", "success_metric": "saves $9,999 a month",
               "stall_points": [{"description": "x", "quote": "There was no deal at that meter in March at all.", "citation": "m/inbox/0"}],
               "current_workflow": [{"step": "a", "who": "b", "citations": ["m/inbox/99"]}] * 3}
        expect = {"systems": "not mentioned in the evidence", "effort": "effort must be", "success_metric": "$9,999",
                  "stall_points": "not found verbatim", "current_workflow": "m/inbox/99"}
        for k, v in bad.items():
            self.write_design(**{k: v})
            errs = solutions.design_errors(p, "meter_fix")
            self.assertTrue(any(expect[k] in e for e in errs), (k, errs))

    def write_artifact(self, s):
        p = self.c.paths
        cite = read_json(p.evidence / "meter_fix.json")["messages"][0]["msg_id"]
        out = p.root / s["artifact_targets"][0]["output_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"---\nopportunity: meter_fix\ntype: sop\ncitations: [{cite}]\n---\nCheck the meter [{cite}]\n")

    def test_valid_design_is_cached(self):
        self.run_through_rank()
        p = self.c.paths
        self.write_design()
        self.assertEqual(solutions.check(p)["ok"], ["meter_fix"])
        self.assertTrue((p.out / "solutions" / "meter_fix.json").exists())
        self.assertTrue(rank.build(self.c.paths)["solution_targets"][0]["done"])
        self.write_design(effort="M")  # changed after validation: needs checking again
        self.assertFalse(rank.build(self.c.paths)["solution_targets"][0]["done"])

    def test_below_top_n_is_not_shown_totalled_or_drafted(self):
        s = self.run_through_rank(top_n=0)
        p = self.c.paths
        self.assertEqual((s["solution_targets"], s["artifact_targets"], s["total_usd_month"]), ([], [], 0))
        self.assertFalse(list(p.evidence.glob("*.json")) if p.evidence.exists() else [])
        r = read_json(p.out / "report.json")
        self.assertEqual(r["opportunities"], [])
        self.assertEqual([o["id"] for o in r["below_cutoff"]], ["meter_fix"])
        self.assertEqual(s["opportunities"][0]["id"], "meter_fix")  # still printed for the run log

    def test_quick_win_gets_design_and_draft(self):
        s = self.run_through_rank(remedy="quick_win")
        p = self.c.paths
        self.assertEqual([(t["id"], t["remedy"]) for t in s["solution_targets"]], [("meter_fix", "quick_win")])
        self.assertEqual(s["artifact_targets"][0]["solution_path"], "out/solutions/meter_fix.json")
        self.assertEqual(solutions.check(p)["missing"], ["meter_fix"])
        ev = read_json(p.evidence / "meter_fix.json")
        self.assertEqual(ev["allowed_types"], ["reply", "checklist", "template"])

    def test_draft_needs_validated_design_and_is_redone_when_it_changes(self):
        s = self.run_through_rank()
        p = self.c.paths
        self.write_artifact(s)
        self.assertEqual(artifacts.check(p)["retry"][0]["errors"],
                         ["its solution design has not been validated; run check-solutions first"])
        self.write_design()
        solutions.check(p)
        self.assertEqual(artifacts.check(p)["ok"], ["meter_fix"])
        self.assertTrue(rank.build(p)["artifact_targets"][0]["done"])
        self.write_design(effort="M")
        solutions.check(p)
        self.assertFalse(rank.build(p)["artifact_targets"][0]["done"])

    def test_artifact_type_must_match_remedy(self):
        for remedy, wrong, right in (("automation", "reply", "email"), ("quick_win", "sop", "reply")):
            with self.subTest(remedy=remedy):
                self.tearDown(); self.setUp()
                s = self.run_through_rank(remedy=remedy)
                p = self.c.paths
                cite = read_json(p.evidence / "meter_fix.json")["messages"][0]["msg_id"]
                out = p.root / s["artifact_targets"][0]["output_path"]
                out.parent.mkdir(parents=True, exist_ok=True)
                body = f"---\nopportunity: meter_fix\ntype: {{}}\ncitations: [{cite}]\n---\nCheck the meter [{cite}]\n"
                out.write_text(body.format(wrong))
                self.assertTrue(any("front matter type" in e for e in artifacts.artifact_errors(p, "meter_fix")))
                out.write_text(body.format(right))
                self.assertEqual(artifacts.artifact_errors(p, "meter_fix"), [])

    def test_remedy_is_required(self):
        p = self.c.paths
        self.write_labels(self.good_labels())
        labels.check_labels(p)
        labels.candidates(p)
        self.write_delta(remedy="rewrite_everything")
        r = labels.check_process_map(p)
        self.assertFalse(r["ok"])
        self.assertTrue(any("remedy must be" in e for e in r["errors"]))

    def test_rank_refuses_map_without_remedies(self):
        p = self.c.paths
        self.run_through_rank()
        pm = read_json(p.work / "process_map.json")
        for proc in pm["processes"]:
            del proc["remedy"]
        write_json(p.work / "process_map.json", pm)
        labels.check_process_map(p)  # re-stamps the edited map
        with self.assertRaisesRegex(SystemExit, "reconsolidate"):
            rank.build(p)


if __name__ == "__main__":
    unittest.main()

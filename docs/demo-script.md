# 2-minute demo video: script and shot list

You record this (screen plus voice); aim for 2:00, never more than 2:30. Use the live site
(https://16-178-109-242.sslip.io) in a clean browser window at normal zoom, one tab, notifications off.
The questions below all work on the loaded synthetic corpus. Do a dry run first: answers take about 9
seconds, so keep talking while they stream.

| Time | On screen | Say (adapt, do not read word for word) |
|---|---|---|
| 0:00 | Login page, click **Try the demo** | "Groundwork answers questions about invoices and contracts, and shows where every answer came from. This is a shared read-only demo with synthetic data." |
| 0:10 | Documents page, scroll the list | "325 documents: 25 contracts and 300 invoices. A background worker parsed, embedded and extracted structured fields from each one." |
| 0:25 | Chat, click the Kestrel termination-notice suggestion | "A clause question. The agent searches the documents..." |
| 0:35 | Answer streams; click the `[C1]` chip; show the source panel | "...and every claim carries a citation. This opens the exact page and sentence, so you can check it." |
| 0:55 | Open **Steps** under the answer | "Here is the work: the tool it called, the arguments and the latency. It chose search for a clause." |
| 1:05 | Click the Ironbridge billing suggestion | "A different kind of question: totals. Search cannot add up invoices, so the agent calls a parameterised SQL tool. The model never writes SQL." |
| 1:25 | Click the net-45 "billed the most" suggestion | "A multi-hop question: contract terms plus invoice totals. This went from 30 to 100 percent correct once I stored contract terms in a table instead of searching for them." |
| 1:45 | Switch to the README results table (or a slide) | "I measured everything: hybrid search lifted recall from 82 to 93 percent on a hard set, exact invoice numbers from 50 to 100. A reranker I also tested was slower and worse, so it is off." |
| 2:00 | README architecture diagram | "Deployed on one AWS host with HTTPS, tested backups, and written to move to Oracle with config changes only. Code and write-up are linked below." |

Tips: show the browser only (hide bookmarks); if the daily cap message appears, say that is the demo
protecting a free quota and try again tomorrow; do not show the invite code, the admin token or the
AWS console; upload the finished video to YouTube (unlisted is fine) or the repo's GitHub release and
link it at the top of the README and in the project card.

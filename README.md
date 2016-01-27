# HTTP access log monitor

## Application:
* Monitors a w3c-formatted HTTP access log and reports on the stats in the console.
* It can both tail a log file and update the stats every 10s (configurable), or run once and display the stats
* In tail mode there's an alarm for having lots of hits in the last 2 mins.
* There's also a very basic apache access log emulator to test the Monitor program in a realistic scenario

## Sample Output
<pre>
Generating initial stats from w3c log
#################################
Processed in 1.82s at 17:47:19 2016-01-27
Period: 12:13:20 2015-11-30 - 12:16:00 2015-12-31

Hits: 419087    Users: 10279    Data: 5.9 GiB
Sections: 189   Pages: 2163
Hits in last 120s: 0

No alerts to display

Most hits by status
200 (399148 hits, 5.9 GiB)
304 (10641 hits, 0.0 B)
301 (5278 hits, 1.2 MiB)
404 (2828 hits, 20.0 MiB)
206 (827 hits, 13.5 MiB)

Most hits by section
root (345020 hits, 5.3 GiB)
static-images (35484 hits, 198.6 MiB)
ajax (29615 hits, 124.3 MiB)
oldSites (4414 hits, 118.4 MiB)
photos (1412 hits, 71.8 MiB)

Most hits by host
37.205.63.195 (49163 hits, 1.7 GiB)
188.39.39.50 (40259 hits, 165.9 MiB)
212.49.193.102 (23417 hits, 97.1 MiB)
80.169.201.66 (11804 hits, 48.9 MiB)
86.181.63.3 (10158 hits, 41.2 MiB)

Most hits by page
/currcam_small.jpg (125909 hits, 388.4 MiB)
/currcam.jpg (74126 hits, 2.4 GiB)
/ajax/wx-body.php (28711 hits, 122.4 MiB)
/mainGraph1.png (28340 hits, 159.5 MiB)
/mainGraph2.png (28289 hits, 250.6 MiB)

#################################
HTTP Log Monitor finished
</pre>

## Design TODO:
* Separate out display logic into its own class rather than having a long output_to_console function in Monitor
  For now it's ok since the UI is very basic, but any more complexity would require this

* Put the parsing on a separate thread so we could aggregate and parse simultaneously:
  The parser could push records to a queue from which the Monitor would grab and process them

* The alerting should probably be less sensitive to movements around the threshold;
  perhaps have a timer to regulate how frequently alerts can be generated
  Also keep them in a limited size queue so the total number of alerts is contained

* Currently everything runs in-memory. For very large log files it would be beneficial
  to parse and process in batches, and dump old processed records to disk (or erase), since they
  aren't especially useful. Only the counters and the most recent 2 mins hold
  useful data, and these are lightweight.

* Implement a more flexible and extensive custom counting class. For now, collections.Counter
  works great but any more complex counting (like top users per section) would be cumbersome.

* Finally, in terms of features, it would be nice to tabulate the results, and have an export option.
  Naturally there are many more stats to be displayed, and custom alerting rules for a variety of fields would be great.

# HTTP access log monitor

## Application:
* Monitors a w3c-formatted HTTP access log and reports on the stats in the console.
* It can both tail a log file and update the stats every 10s (configurable), or run once and display the stats
* In tail mode there's an alarm for having lots of hits in the last 2 mins.
* There's also a very basic apache access log emulator to test the Monitor program in a realistic scenario


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

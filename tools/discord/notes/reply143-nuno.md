Reply to nuno6573, not posted. It says what is true before the release; once v1.4.3-beta is out, add the link.

Thanks for the report, it was not your problem, and it is fixed for the next build. We reproduced two causes in the lab:

1. If a settings file (settings_riptopl.cfg) sits beside RIPPS2.ELF, the next boot read that one and ignored the destination you chose. It saved to your drive, then went back to the old settings.
2. If the drive had not started yet (USB and MMCE are on Manual by default), RIPPS2 said it was not connected and left the settings where they were. Now it starts that drive first.

Until the build is out: set that drive to Auto in Game Sources, Save Changes, restart, then choose it in Save Settings To and Save Changes again. Keep RIPPS2.ELF out of any folder holding a settings file.

Our lab has no USB or MMCE, only an internal HDD that goes the same way as USB, so your console is the real test. When the build is out, please try both, power cycle, and check the row. Your DIAG.TXT will say which way it went.

One correction from the test post: Manage does see a plain BIBLE once BIBLE has started RIPPS2, so its settings page works. Leave its first row alone on your console, since that row is the bind.
